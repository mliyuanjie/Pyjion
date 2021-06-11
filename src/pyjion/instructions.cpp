/*
* The MIT License (MIT)
*
* Copyright (c) Microsoft Corporation
*
* Permission is hereby granted, free of charge, to any person obtaining a
* copy of this software and associated documentation files (the "Software"),
* to deal in the Software without restriction, including without limitation
* the rights to use, copy, modify, merge, publish, distribute, sublicense,
* and/or sell copies of the Software, and to permit persons to whom the
* Software is furnished to do so, subject to the following conditions:
*
* The above copyright notice and this permission notice shall be included
* in all copies or substantial portions of the Software.
*
* THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
* OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
* FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
* THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
* OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
* ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
* OTHER DEALINGS IN THE SOFTWARE.
*
*/

#include "instructions.h"
#include "pycomp.h"
#include "unboxing.h"


InstructionGraph::InstructionGraph(PyCodeObject *code, unordered_map<py_opindex , const InterpreterStack*> stacks) {
    auto mByteCode = (_Py_CODEUNIT *)PyBytes_AS_STRING(code->co_code);
    auto size = PyBytes_Size(code->co_code);
    for (py_opindex curByte = 0; curByte < size; curByte += SIZEOF_CODEUNIT) {
        py_opindex index = curByte;
        py_opcode opcode = GET_OPCODE(curByte);
        py_oparg oparg = GET_OPARG(curByte);

        if (opcode == EXTENDED_ARG)
        {
            instructions[index] = {
                    .index = index,
                    .opcode = opcode,
                    .oparg = oparg,
                    .escape = false
            };
            curByte += SIZEOF_CODEUNIT;
            oparg = (oparg << 8) | GET_OPARG(curByte);
            opcode = GET_OPCODE(curByte);
            index = curByte;
        }
        if (stacks[index] != nullptr){
            for (const auto & si: *stacks[index]){
                if (si.hasSource()){
                    ssize_t stackPosition = si.Sources->isConsumedBy(index);
                    if (stackPosition != -1) {
                        edges.push_back({
                            .from = si.Sources->producer(),
                            .to = index,
                            .label = si.Sources->describe(),
                            .value = si.Value,
                            .source = si.Sources,
                            .escaped = NoEscape,
                            .kind = si.hasValue() ? si.Value->kind() : AVK_Any,
                            .position = static_cast<py_opindex>(stackPosition)
                        });
                    }
                }
            }
        }
        instructions[index] = {
            .index = index,
            .opcode = opcode,
            .oparg = oparg,
            .escape = false
        };
    }
    fixInstructions();
    fixLocals();
    fixEdges();
}

void InstructionGraph::fixEdges(){
    for (auto & edge: this->edges){
        if (!this->instructions[edge.from].escape) {
            // From non-escaped operation
            if (this->instructions[edge.to].escape){
                edge.escaped = Unbox;
            } else {
                edge.escaped = NoEscape;
            }
        } else {
            // From escaped operation
            if (this->instructions[edge.to].escape){
                edge.escaped = Unboxed;
            } else {
                edge.escaped = Box;
            }
        }
    }
}

void InstructionGraph::fixInstructions(){
    for (auto & instruction: this->instructions) {
        if (!supportsUnboxing(instruction.second.opcode))
            continue;
        if (instruction.second.opcode == LOAD_FAST || instruction.second.opcode == STORE_FAST )
            continue; // handled in fixLocals();

        // Check that all inbound edges can be escaped.
        bool allEdgesEscapable = true;
        for (auto & edgeIn: getEdges(instruction.first)){
            if (!supportsEscaping(edgeIn.second.kind))
                allEdgesEscapable = false;
        }
        if (!allEdgesEscapable)
            continue;

        // Check that all inbound edges can be escaped.
        bool allOutputsEscapable = true;
        for (auto & edgeOut: getEdgesFrom(instruction.first)){
            if (!supportsEscaping(edgeOut.second.kind))
                allOutputsEscapable = false;
        }
        if (!allOutputsEscapable)
            continue;

        // Otherwise, we can escape this instruction..
        instruction.second.escape = true;
    }
}

void InstructionGraph::fixLocals(){
    for (auto & instruction: this->instructions) {
        if (instruction.second.opcode != LOAD_FAST && instruction.second.opcode != STORE_FAST )
            continue;
        // TODO : Decide which locals can be escaped.
    }
}

void InstructionGraph::printGraph(const char* name) {
    printf("digraph %s { \n", name);
    printf("\tnode [shape=box];\n");
    printf("\tFRAME [label=FRAME];\n");
    for (const auto & node: instructions){
        if (node.second.escape)
            printf("\tOP%u [label=\"%s (%d)\" color=blue];\n", node.first, opcodeName(node.second.opcode), node.second.oparg);
        else
            printf("\tOP%u [label=\"%s (%d)\"];\n", node.first, opcodeName(node.second.opcode), node.second.oparg);
        switch(node.second.opcode){
            case JUMP_FORWARD:
                printf("\tOP%u -> OP%u [label=\"Jump\" color=yellow];\n", node.second.index, node.second.index + node.second.oparg);
                break;
            case JUMP_ABSOLUTE:
            case JUMP_IF_FALSE_OR_POP:
            case JUMP_IF_TRUE_OR_POP:
            case JUMP_IF_NOT_EXC_MATCH:
            case POP_JUMP_IF_TRUE:
            case POP_JUMP_IF_FALSE:
                printf("\tOP%u -> OP%u [label=\"Jump\" color=yellow];\n", node.second.index, node.second.oparg);
                break;
        }
    }

    for (const auto & edge: edges){
        if (edge.from == -1) {
            printf("\tFRAME -> OP%u [label=\"%s (%s)\"];\n", edge.to, edge.label, edge.value->describe());
        } else {
            switch (edge.escaped) {
                case NoEscape:
                    printf("\tOP%u -> OP%u [label=\"%s (%s) -%u\" color=black];\n", edge.from, edge.to, edge.label, edge.value->describe(), edge.position);
                    break;
                case Unbox:
                    printf("\tOP%u -> OP%u [label=\"%s (%s) U%u\" color=red];\n", edge.from, edge.to, edge.label, edge.value->describe(), edge.position);
                    break;
                case Box:
                    printf("\tOP%u -> OP%u [label=\"%s (%s) B%u\" color=green];\n", edge.from, edge.to, edge.label, edge.value->describe(), edge.position);
                    break;
                case Unboxed:
                    printf("\tOP%u -> OP%u [label=\"%s (%s) UN%u\" color=purple];\n", edge.from, edge.to, edge.label, edge.value->describe(), edge.position);
                    break;
            }
        }
    }
    printf("}\n");
}

EdgeMap InstructionGraph::getEdges(py_opindex i){
    EdgeMap filteredEdges;
    for (auto & edge: this->edges){
        if (edge.to == i)
            filteredEdges[edge.position] = edge;
    }
    return filteredEdges;
}

EdgeMap InstructionGraph::getEdgesFrom(py_opindex i){
    EdgeMap filteredEdges;
    for (auto & edge: this->edges){
        if (edge.from == i)
            filteredEdges[edge.position] = edge;
    }
    return filteredEdges;
}