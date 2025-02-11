from dis import get_instructions
from typing import Any, Dict, List, Optional, Set
from pyjion import il, native, offsets as get_offsets, symbols
from collections import namedtuple
from warnings import warn
import struct
from platform import machine
import dataclasses


__all__ = [
    "dis",
    "dis_native",
    "print_il"
]

# Pre stack effect
Pop0 = 0
Pop1 = 1
PopI = 2
VarPop = 4
PopI4 = 8
PopI8 = 16
PopR4 = 32
PopR8 = 64
PopRef = 128

# Post stack effect
Push0 = 0
Push1 = 1
PushI = 2
VarPush = 4
PushI4 = 8
PushI8 = 16
PushR4 = 32
PushR8 = 64
PushRef = 128

# Size
InlineNone = 0
ShortInlineVar = 1
ShortInlineI = 2
ShortInlineR = 3
InlineI = 4
InlineI8 = 5
InlineR = 6
InlineR8 = 7
InlineMethod = 8
InlineSig = 9
InlineBrTarget = 10
InlineVar = 11
InlineType = 12
InlineField = 13
ShortInlineBrTarget = 14
InlineSwitch = 15
InlineString = 16
InlineTok = 17

# Type
IPrimitive = 1
IMacro = 2
IObjModel = 3
IInternal = 4
IPrefix = 5

NEXT = 1
BREAK = 2
CALL = 3
RETURN = 4
BRANCH = 5
COND_BRANCH = 6
THROW = 7
META = 8

MOOT = None

OPDEF = namedtuple("OPDEF", "cee_code name es_effect_pre es_effect_post size type n_bytes first_byte second_byte flow_arg")

# Copy + Paste these from opcode.def and wrap the CEE codes in quotes.

opcodes = [
OPDEF("CEE_NOP",                        "nop",              Pop0,               Push0,       InlineNone,         IPrimitive,  1,  0xFF,    0x00,    NEXT),
OPDEF("CEE_BREAK",                      "break",            Pop0,               Push0,       InlineNone,         IPrimitive,  1,  0xFF,    0x01,    BREAK),
OPDEF("CEE_LDARG_0",                    "ldarg.0",          Pop0,               Push1,       InlineNone,         IMacro,      1,  0xFF,    0x02,    NEXT),
OPDEF("CEE_LDARG_1",                    "ldarg.1",          Pop0,               Push1,       InlineNone,         IMacro,      1,  0xFF,    0x03,    NEXT),
OPDEF("CEE_LDARG_2",                    "ldarg.2",          Pop0,               Push1,       InlineNone,         IMacro,      1,  0xFF,    0x04,    NEXT),
OPDEF("CEE_LDARG_3",                    "ldarg.3",          Pop0,               Push1,       InlineNone,         IMacro,      1,  0xFF,    0x05,    NEXT),
OPDEF("CEE_LDLOC_0",                    "ldloc.0",          Pop0,               Push1,       InlineNone,         IMacro,      1,  0xFF,    0x06,    NEXT),
OPDEF("CEE_LDLOC_1",                    "ldloc.1",          Pop0,               Push1,       InlineNone,         IMacro,      1,  0xFF,    0x07,    NEXT),
OPDEF("CEE_LDLOC_2",                    "ldloc.2",          Pop0,               Push1,       InlineNone,         IMacro,      1,  0xFF,    0x08,    NEXT),
OPDEF("CEE_LDLOC_3",                    "ldloc.3",          Pop0,               Push1,       InlineNone,         IMacro,      1,  0xFF,    0x09,    NEXT),
OPDEF("CEE_STLOC_0",                    "stloc.0",          Pop1,               Push0,       InlineNone,         IMacro,      1,  0xFF,    0x0A,    NEXT),
OPDEF("CEE_STLOC_1",                    "stloc.1",          Pop1,               Push0,       InlineNone,         IMacro,      1,  0xFF,    0x0B,    NEXT),
OPDEF("CEE_STLOC_2",                    "stloc.2",          Pop1,               Push0,       InlineNone,         IMacro,      1,  0xFF,    0x0C,    NEXT),
OPDEF("CEE_STLOC_3",                    "stloc.3",          Pop1,               Push0,       InlineNone,         IMacro,      1,  0xFF,    0x0D,    NEXT),
OPDEF("CEE_LDARG_S",                    "ldarg.s",          Pop0,               Push1,       ShortInlineVar,     IMacro,      1,  0xFF,    0x0E,    NEXT),
OPDEF("CEE_LDARGA_S",                   "ldarga.s",         Pop0,               PushI,       ShortInlineVar,     IMacro,      1,  0xFF,    0x0F,    NEXT),
OPDEF("CEE_STARG_S",                    "starg.s",          Pop1,               Push0,       ShortInlineVar,     IMacro,      1,  0xFF,    0x10,    NEXT),
OPDEF("CEE_LDLOC_S",                    "ldloc.s",          Pop0,               Push1,       ShortInlineVar,     IMacro,      1,  0xFF,    0x11,    NEXT),
OPDEF("CEE_LDLOCA_S",                   "ldloca.s",         Pop0,               PushI,       ShortInlineVar,     IMacro,      1,  0xFF,    0x12,    NEXT),
OPDEF("CEE_STLOC_S",                    "stloc.s",          Pop1,               Push0,       ShortInlineVar,     IMacro,      1,  0xFF,    0x13,    NEXT),
OPDEF("CEE_LDNULL",                     "ldnull",           Pop0,               PushRef,     InlineNone,         IPrimitive,  1,  0xFF,    0x14,    NEXT),
OPDEF("CEE_LDC_I4_M1",                  "ldc.i4.m1",        Pop0,               PushI,       InlineNone,         IMacro,      1,  0xFF,    0x15,    NEXT),
OPDEF("CEE_LDC_I4_0",                   "ldc.i4.0",         Pop0,               PushI,       InlineNone,         IMacro,      1,  0xFF,    0x16,    NEXT),
OPDEF("CEE_LDC_I4_1",                   "ldc.i4.1",         Pop0,               PushI,       InlineNone,         IMacro,      1,  0xFF,    0x17,    NEXT),
OPDEF("CEE_LDC_I4_2",                   "ldc.i4.2",         Pop0,               PushI,       InlineNone,         IMacro,      1,  0xFF,    0x18,    NEXT),
OPDEF("CEE_LDC_I4_3",                   "ldc.i4.3",         Pop0,               PushI,       InlineNone,         IMacro,      1,  0xFF,    0x19,    NEXT),
OPDEF("CEE_LDC_I4_4",                   "ldc.i4.4",         Pop0,               PushI,       InlineNone,         IMacro,      1,  0xFF,    0x1A,    NEXT),
OPDEF("CEE_LDC_I4_5",                   "ldc.i4.5",         Pop0,               PushI,       InlineNone,         IMacro,      1,  0xFF,    0x1B,    NEXT),
OPDEF("CEE_LDC_I4_6",                   "ldc.i4.6",         Pop0,               PushI,       InlineNone,         IMacro,      1,  0xFF,    0x1C,    NEXT),
OPDEF("CEE_LDC_I4_7",                   "ldc.i4.7",         Pop0,               PushI,       InlineNone,         IMacro,      1,  0xFF,    0x1D,    NEXT),
OPDEF("CEE_LDC_I4_8",                   "ldc.i4.8",         Pop0,               PushI,       InlineNone,         IMacro,      1,  0xFF,    0x1E,    NEXT),
OPDEF("CEE_LDC_I4_S",                   "ldc.i4.s",         Pop0,               PushI,       ShortInlineI,       IMacro,      1,  0xFF,    0x1F,    NEXT),
OPDEF("CEE_LDC_I4",                     "ldc.i4",           Pop0,               PushI,       InlineI,            IPrimitive,  1,  0xFF,    0x20,    NEXT),
OPDEF("CEE_LDC_I8",                     "ldc.i8",           Pop0,               PushI8,      InlineI8,           IPrimitive,  1,  0xFF,    0x21,    NEXT),
OPDEF("CEE_LDC_R4",                     "ldc.r4",           Pop0,               PushR4,      ShortInlineR,       IPrimitive,  1,  0xFF,    0x22,    NEXT),
OPDEF("CEE_LDC_R8",                     "ldc.r8",           Pop0,               PushR8,      InlineR,            IPrimitive,  1,  0xFF,    0x23,    NEXT),
OPDEF("CEE_UNUSED49",                   "unused",           Pop0,               Push0,       InlineNone,         IPrimitive,  1,  0xFF,    0x24,    NEXT),
OPDEF("CEE_DUP",                        "dup",              Pop1,               Push1+Push1, InlineNone,         IPrimitive,  1,  0xFF,    0x25,    NEXT),
OPDEF("CEE_POP",                        "pop",              Pop1,               Push0,       InlineNone,         IPrimitive,  1,  0xFF,    0x26,    NEXT),
OPDEF("CEE_JMP",                        "jmp",              Pop0,               Push0,       InlineMethod,       IPrimitive,  1,  0xFF,    0x27,    CALL),
OPDEF("CEE_CALL",                       "call",             VarPop,             VarPush,     InlineMethod,       IPrimitive,  1,  0xFF,    0x28,    CALL),
OPDEF("CEE_CALLI",                      "calli",            VarPop,             VarPush,     InlineSig,          IPrimitive,  1,  0xFF,    0x29,    CALL),
OPDEF("CEE_RET",                        "ret",              VarPop,             Push0,       InlineNone,         IPrimitive,  1,  0xFF,    0x2A,    RETURN),
OPDEF("CEE_BR_S",                       "br.s",             Pop0,               Push0,       ShortInlineBrTarget,IMacro,      1,  0xFF,    0x2B,    BRANCH),
OPDEF("CEE_BRFALSE_S",                  "brfalse.s",        PopI,               Push0,       ShortInlineBrTarget,IMacro,      1,  0xFF,    0x2C,    COND_BRANCH),
OPDEF("CEE_BRTRUE_S",                   "brtrue.s",         PopI,               Push0,       ShortInlineBrTarget,IMacro,      1,  0xFF,    0x2D,    COND_BRANCH),
OPDEF("CEE_BEQ_S",                      "beq.s",            Pop1+Pop1,          Push0,       ShortInlineBrTarget,IMacro,      1,  0xFF,    0x2E,    COND_BRANCH),
OPDEF("CEE_BGE_S",                      "bge.s",            Pop1+Pop1,          Push0,       ShortInlineBrTarget,IMacro,      1,  0xFF,    0x2F,    COND_BRANCH),
OPDEF("CEE_BGT_S",                      "bgt.s",            Pop1+Pop1,          Push0,       ShortInlineBrTarget,IMacro,      1,  0xFF,    0x30,    COND_BRANCH),
OPDEF("CEE_BLE_S",                      "ble.s",            Pop1+Pop1,          Push0,       ShortInlineBrTarget,IMacro,      1,  0xFF,    0x31,    COND_BRANCH),
OPDEF("CEE_BLT_S",                      "blt.s",            Pop1+Pop1,          Push0,       ShortInlineBrTarget,IMacro,      1,  0xFF,    0x32,    COND_BRANCH),
OPDEF("CEE_BNE_UN_S",                   "bne.un.s",         Pop1+Pop1,          Push0,       ShortInlineBrTarget,IMacro,      1,  0xFF,    0x33,    COND_BRANCH),
OPDEF("CEE_BGE_UN_S",                   "bge.un.s",         Pop1+Pop1,          Push0,       ShortInlineBrTarget,IMacro,      1,  0xFF,    0x34,    COND_BRANCH),
OPDEF("CEE_BGT_UN_S",                   "bgt.un.s",         Pop1+Pop1,          Push0,       ShortInlineBrTarget,IMacro,      1,  0xFF,    0x35,    COND_BRANCH),
OPDEF("CEE_BLE_UN_S",                   "ble.un.s",         Pop1+Pop1,          Push0,       ShortInlineBrTarget,IMacro,      1,  0xFF,    0x36,    COND_BRANCH),
OPDEF("CEE_BLT_UN_S",                   "blt.un.s",         Pop1+Pop1,          Push0,       ShortInlineBrTarget,IMacro,      1,  0xFF,    0x37,    COND_BRANCH),
OPDEF("CEE_BR",                         "br",               Pop0,               Push0,       InlineBrTarget,     IPrimitive,  1,  0xFF,    0x38,    BRANCH),
OPDEF("CEE_BRFALSE",                    "brfalse",          PopI,               Push0,       InlineBrTarget,     IPrimitive,  1,  0xFF,    0x39,    COND_BRANCH),
OPDEF("CEE_BRTRUE",                     "brtrue",           PopI,               Push0,       InlineBrTarget,     IPrimitive,  1,  0xFF,    0x3A,    COND_BRANCH),
OPDEF("CEE_BEQ",                        "beq",              Pop1+Pop1,          Push0,       InlineBrTarget,     IMacro,      1,  0xFF,    0x3B,    COND_BRANCH),
OPDEF("CEE_BGE",                        "bge",              Pop1+Pop1,          Push0,       InlineBrTarget,     IMacro,      1,  0xFF,    0x3C,    COND_BRANCH),
OPDEF("CEE_BGT",                        "bgt",              Pop1+Pop1,          Push0,       InlineBrTarget,     IMacro,      1,  0xFF,    0x3D,    COND_BRANCH),
OPDEF("CEE_BLE",                        "ble",              Pop1+Pop1,          Push0,       InlineBrTarget,     IMacro,      1,  0xFF,    0x3E,    COND_BRANCH),
OPDEF("CEE_BLT",                        "blt",              Pop1+Pop1,          Push0,       InlineBrTarget,     IMacro,      1,  0xFF,    0x3F,    COND_BRANCH),
OPDEF("CEE_BNE_UN",                     "bne.un",           Pop1+Pop1,          Push0,       InlineBrTarget,     IMacro,      1,  0xFF,    0x40,    COND_BRANCH),
OPDEF("CEE_BGE_UN",                     "bge.un",           Pop1+Pop1,          Push0,       InlineBrTarget,     IMacro,      1,  0xFF,    0x41,    COND_BRANCH),
OPDEF("CEE_BGT_UN",                     "bgt.un",           Pop1+Pop1,          Push0,       InlineBrTarget,     IMacro,      1,  0xFF,    0x42,    COND_BRANCH),
OPDEF("CEE_BLE_UN",                     "ble.un",           Pop1+Pop1,          Push0,       InlineBrTarget,     IMacro,      1,  0xFF,    0x43,    COND_BRANCH),
OPDEF("CEE_BLT_UN",                     "blt.un",           Pop1+Pop1,          Push0,       InlineBrTarget,     IMacro,      1,  0xFF,    0x44,    COND_BRANCH),
OPDEF("CEE_SWITCH",                     "switch",           PopI,               Push0,       InlineSwitch,       IPrimitive,  1,  0xFF,    0x45,    COND_BRANCH),
OPDEF("CEE_LDIND_I1",                   "ldind.i1",         PopI,               PushI,       InlineNone,         IPrimitive,  1,  0xFF,    0x46,    NEXT),
OPDEF("CEE_LDIND_U1",                   "ldind.u1",         PopI,               PushI,       InlineNone,         IPrimitive,  1,  0xFF,    0x47,    NEXT),
OPDEF("CEE_LDIND_I2",                   "ldind.i2",         PopI,               PushI,       InlineNone,         IPrimitive,  1,  0xFF,    0x48,    NEXT),
OPDEF("CEE_LDIND_U2",                   "ldind.u2",         PopI,               PushI,       InlineNone,         IPrimitive,  1,  0xFF,    0x49,    NEXT),
OPDEF("CEE_LDIND_I4",                   "ldind.i4",         PopI,               PushI,       InlineNone,         IPrimitive,  1,  0xFF,    0x4A,    NEXT),
OPDEF("CEE_LDIND_U4",                   "ldind.u4",         PopI,               PushI,       InlineNone,         IPrimitive,  1,  0xFF,    0x4B,    NEXT),
OPDEF("CEE_LDIND_I8",                   "ldind.i8",         PopI,               PushI8,      InlineNone,         IPrimitive,  1,  0xFF,    0x4C,    NEXT),
OPDEF("CEE_LDIND_I",                    "ldind.i",          PopI,               PushI,       InlineNone,         IPrimitive,  1,  0xFF,    0x4D,    NEXT),
OPDEF("CEE_LDIND_R4",                   "ldind.r4",         PopI,               PushR4,      InlineNone,         IPrimitive,  1,  0xFF,    0x4E,    NEXT),
OPDEF("CEE_LDIND_R8",                   "ldind.r8",         PopI,               PushR8,      InlineNone,         IPrimitive,  1,  0xFF,    0x4F,    NEXT),
OPDEF("CEE_LDIND_REF",                  "ldind.ref",        PopI,               PushRef,     InlineNone,         IPrimitive,  1,  0xFF,    0x50,    NEXT),
OPDEF("CEE_STIND_REF",                  "stind.ref",        PopI+PopI,          Push0,       InlineNone,         IPrimitive,  1,  0xFF,    0x51,    NEXT),
OPDEF("CEE_STIND_I1",                   "stind.i1",         PopI+PopI,          Push0,       InlineNone,         IPrimitive,  1,  0xFF,    0x52,    NEXT),
OPDEF("CEE_STIND_I2",                   "stind.i2",         PopI+PopI,          Push0,       InlineNone,         IPrimitive,  1,  0xFF,    0x53,    NEXT),
OPDEF("CEE_STIND_I4",                   "stind.i4",         PopI+PopI,          Push0,       InlineNone,         IPrimitive,  1,  0xFF,    0x54,    NEXT),
OPDEF("CEE_STIND_I8",                   "stind.i8",         PopI+PopI8,         Push0,       InlineNone,         IPrimitive,  1,  0xFF,    0x55,    NEXT),
OPDEF("CEE_STIND_R4",                   "stind.r4",         PopI+PopR4,         Push0,       InlineNone,         IPrimitive,  1,  0xFF,    0x56,    NEXT),
OPDEF("CEE_STIND_R8",                   "stind.r8",         PopI+PopR8,         Push0,       InlineNone,         IPrimitive,  1,  0xFF,    0x57,    NEXT),
OPDEF("CEE_ADD",                        "add",              Pop1+Pop1,          Push1,       InlineNone,         IPrimitive,  1,  0xFF,    0x58,    NEXT),
OPDEF("CEE_SUB",                        "sub",              Pop1+Pop1,          Push1,       InlineNone,         IPrimitive,  1,  0xFF,    0x59,    NEXT),
OPDEF("CEE_MUL",                        "mul",              Pop1+Pop1,          Push1,       InlineNone,         IPrimitive,  1,  0xFF,    0x5A,    NEXT),
OPDEF("CEE_DIV",                        "div",              Pop1+Pop1,          Push1,       InlineNone,         IPrimitive,  1,  0xFF,    0x5B,    NEXT),
OPDEF("CEE_DIV_UN",                     "div.un",           Pop1+Pop1,          Push1,       InlineNone,         IPrimitive,  1,  0xFF,    0x5C,    NEXT),
OPDEF("CEE_REM",                        "rem",              Pop1+Pop1,          Push1,       InlineNone,         IPrimitive,  1,  0xFF,    0x5D,    NEXT),
OPDEF("CEE_REM_UN",                     "rem.un",           Pop1+Pop1,          Push1,       InlineNone,         IPrimitive,  1,  0xFF,    0x5E,    NEXT),
OPDEF("CEE_AND",                        "and",              Pop1+Pop1,          Push1,       InlineNone,         IPrimitive,  1,  0xFF,    0x5F,    NEXT),
OPDEF("CEE_OR",                         "or",               Pop1+Pop1,          Push1,       InlineNone,         IPrimitive,  1,  0xFF,    0x60,    NEXT),
OPDEF("CEE_XOR",                        "xor",              Pop1+Pop1,          Push1,       InlineNone,         IPrimitive,  1,  0xFF,    0x61,    NEXT),
OPDEF("CEE_SHL",                        "shl",              Pop1+Pop1,          Push1,       InlineNone,         IPrimitive,  1,  0xFF,    0x62,    NEXT),
OPDEF("CEE_SHR",                        "shr",              Pop1+Pop1,          Push1,       InlineNone,         IPrimitive,  1,  0xFF,    0x63,    NEXT),
OPDEF("CEE_SHR_UN",                     "shr.un",           Pop1+Pop1,          Push1,       InlineNone,         IPrimitive,  1,  0xFF,    0x64,    NEXT),
OPDEF("CEE_NEG",                        "neg",              Pop1,               Push1,       InlineNone,         IPrimitive,  1,  0xFF,    0x65,    NEXT),
OPDEF("CEE_NOT",                        "not",              Pop1,               Push1,       InlineNone,         IPrimitive,  1,  0xFF,    0x66,    NEXT),
OPDEF("CEE_CONV_I1",                    "conv.i1",          Pop1,               PushI,       InlineNone,         IPrimitive,  1,  0xFF,    0x67,    NEXT),
OPDEF("CEE_CONV_I2",                    "conv.i2",          Pop1,               PushI,       InlineNone,         IPrimitive,  1,  0xFF,    0x68,    NEXT),
OPDEF("CEE_CONV_I4",                    "conv.i4",          Pop1,               PushI,       InlineNone,         IPrimitive,  1,  0xFF,    0x69,    NEXT),
OPDEF("CEE_CONV_I8",                    "conv.i8",          Pop1,               PushI8,      InlineNone,         IPrimitive,  1,  0xFF,    0x6A,    NEXT),
OPDEF("CEE_CONV_R4",                    "conv.r4",          Pop1,               PushR4,      InlineNone,         IPrimitive,  1,  0xFF,    0x6B,    NEXT),
OPDEF("CEE_CONV_R8",                    "conv.r8",          Pop1,               PushR8,      InlineNone,         IPrimitive,  1,  0xFF,    0x6C,    NEXT),
OPDEF("CEE_CONV_U4",                    "conv.u4",          Pop1,               PushI,       InlineNone,         IPrimitive,  1,  0xFF,    0x6D,    NEXT),
OPDEF("CEE_CONV_U8",                    "conv.u8",          Pop1,               PushI8,      InlineNone,         IPrimitive,  1,  0xFF,    0x6E,    NEXT),
OPDEF("CEE_CALLVIRT",                   "callvirt",         VarPop,             VarPush,     InlineMethod,       IObjModel,   1,  0xFF,    0x6F,    CALL),
OPDEF("CEE_CPOBJ",                      "cpobj",            PopI+PopI,          Push0,       InlineType,         IObjModel,   1,  0xFF,    0x70,    NEXT),
OPDEF("CEE_LDOBJ",                      "ldobj",            PopI,               Push1,       InlineType,         IObjModel,   1,  0xFF,    0x71,    NEXT),
OPDEF("CEE_LDSTR",                      "ldstr",            Pop0,               PushRef,     InlineString,       IObjModel,   1,  0xFF,    0x72,    NEXT),
OPDEF("CEE_NEWOBJ",                     "newobj",           VarPop,             PushRef,     InlineMethod,       IObjModel,   1,  0xFF,    0x73,    CALL),
OPDEF("CEE_CASTCLASS",                  "castclass",        PopRef,             PushRef,     InlineType,         IObjModel,   1,  0xFF,    0x74,    NEXT),
OPDEF("CEE_ISINST",                     "isinst",           PopRef,             PushI,       InlineType,         IObjModel,   1,  0xFF,    0x75,    NEXT),
OPDEF("CEE_CONV_R_UN",                  "conv.r.un",        Pop1,               PushR8,      InlineNone,         IPrimitive,  1,  0xFF,    0x76,    NEXT),
OPDEF("CEE_UNUSED58",                   "unused",           Pop0,               Push0,       InlineNone,         IPrimitive,  1,  0xFF,    0x77,    NEXT),
OPDEF("CEE_UNUSED1",                    "unused",           Pop0,               Push0,       InlineNone,         IPrimitive,  1,  0xFF,    0x78,    NEXT),
OPDEF("CEE_UNBOX",                      "unbox",            PopRef,             PushI,       InlineType,         IPrimitive,  1,  0xFF,    0x79,    NEXT),
OPDEF("CEE_THROW",                      "throw",            PopRef,             Push0,       InlineNone,         IObjModel,   1,  0xFF,    0x7A,    THROW),
OPDEF("CEE_LDFLD",                      "ldfld",            PopRef,             Push1,       InlineField,        IObjModel,   1,  0xFF,    0x7B,    NEXT),
OPDEF("CEE_LDFLDA",                     "ldflda",           PopRef,             PushI,       InlineField,        IObjModel,   1,  0xFF,    0x7C,    NEXT),
OPDEF("CEE_STFLD",                      "stfld",            PopRef+Pop1,        Push0,       InlineField,        IObjModel,   1,  0xFF,    0x7D,    NEXT),
OPDEF("CEE_LDSFLD",                     "ldsfld",           Pop0,               Push1,       InlineField,        IObjModel,   1,  0xFF,    0x7E,    NEXT),
OPDEF("CEE_LDSFLDA",                    "ldsflda",          Pop0,               PushI,       InlineField,        IObjModel,   1,  0xFF,    0x7F,    NEXT),
OPDEF("CEE_STSFLD",                     "stsfld",           Pop1,               Push0,       InlineField,        IObjModel,   1,  0xFF,    0x80,    NEXT),
OPDEF("CEE_STOBJ",                      "stobj",            PopI+Pop1,          Push0,       InlineType,         IPrimitive,  1,  0xFF,    0x81,    NEXT),
OPDEF("CEE_CONV_OVF_I1_UN",             "conv.ovf.i1.un",   Pop1,               PushI,       InlineNone,         IPrimitive,  1,  0xFF,    0x82,    NEXT),
OPDEF("CEE_CONV_OVF_I2_UN",             "conv.ovf.i2.un",   Pop1,               PushI,       InlineNone,         IPrimitive,  1,  0xFF,    0x83,    NEXT),
OPDEF("CEE_CONV_OVF_I4_UN",             "conv.ovf.i4.un",   Pop1,               PushI,       InlineNone,         IPrimitive,  1,  0xFF,    0x84,    NEXT),
OPDEF("CEE_CONV_OVF_I8_UN",             "conv.ovf.i8.un",   Pop1,               PushI8,      InlineNone,         IPrimitive,  1,  0xFF,    0x85,    NEXT),
OPDEF("CEE_CONV_OVF_U1_UN",             "conv.ovf.u1.un",   Pop1,               PushI,       InlineNone,         IPrimitive,  1,  0xFF,    0x86,    NEXT),
OPDEF("CEE_CONV_OVF_U2_UN",             "conv.ovf.u2.un",   Pop1,               PushI,       InlineNone,         IPrimitive,  1,  0xFF,    0x87,    NEXT),
OPDEF("CEE_CONV_OVF_U4_UN",             "conv.ovf.u4.un",   Pop1,               PushI,       InlineNone,         IPrimitive,  1,  0xFF,    0x88,    NEXT),
OPDEF("CEE_CONV_OVF_U8_UN",             "conv.ovf.u8.un",   Pop1,               PushI8,      InlineNone,         IPrimitive,  1,  0xFF,    0x89,    NEXT),
OPDEF("CEE_CONV_OVF_I_UN",              "conv.ovf.i.un",    Pop1,               PushI,       InlineNone,         IPrimitive,  1,  0xFF,    0x8A,    NEXT),
OPDEF("CEE_CONV_OVF_U_UN",              "conv.ovf.u.un",    Pop1,               PushI,       InlineNone,         IPrimitive,  1,  0xFF,    0x8B,    NEXT),
OPDEF("CEE_BOX",                        "box",              Pop1,               PushRef,     InlineType,         IPrimitive,  1,  0xFF,    0x8C,    NEXT),
OPDEF("CEE_NEWARR",                     "newarr",           PopI,               PushRef,     InlineType,         IObjModel,   1,  0xFF,    0x8D,    NEXT),
OPDEF("CEE_LDLEN",                      "ldlen",            PopRef,             PushI,       InlineNone,         IObjModel,   1,  0xFF,    0x8E,    NEXT),
OPDEF("CEE_LDELEMA",                    "ldelema",          PopRef+PopI,        PushI,       InlineType,         IObjModel,   1,  0xFF,    0x8F,    NEXT),
OPDEF("CEE_LDELEM_I1",                  "ldelem.i1",        PopRef+PopI,        PushI,       InlineNone,         IObjModel,   1,  0xFF,    0x90,    NEXT),
OPDEF("CEE_LDELEM_U1",                  "ldelem.u1",        PopRef+PopI,        PushI,       InlineNone,         IObjModel,   1,  0xFF,    0x91,    NEXT),
OPDEF("CEE_LDELEM_I2",                  "ldelem.i2",        PopRef+PopI,        PushI,       InlineNone,         IObjModel,   1,  0xFF,    0x92,    NEXT),
OPDEF("CEE_LDELEM_U2",                  "ldelem.u2",        PopRef+PopI,        PushI,       InlineNone,         IObjModel,   1,  0xFF,    0x93,    NEXT),
OPDEF("CEE_LDELEM_I4",                  "ldelem.i4",        PopRef+PopI,        PushI,       InlineNone,         IObjModel,   1,  0xFF,    0x94,    NEXT),
OPDEF("CEE_LDELEM_U4",                  "ldelem.u4",        PopRef+PopI,        PushI,       InlineNone,         IObjModel,   1,  0xFF,    0x95,    NEXT),
OPDEF("CEE_LDELEM_I8",                  "ldelem.i8",        PopRef+PopI,        PushI8,      InlineNone,         IObjModel,   1,  0xFF,    0x96,    NEXT),
OPDEF("CEE_LDELEM_I",                   "ldelem.i",         PopRef+PopI,        PushI,       InlineNone,         IObjModel,   1,  0xFF,    0x97,    NEXT),
OPDEF("CEE_LDELEM_R4",                  "ldelem.r4",        PopRef+PopI,        PushR4,      InlineNone,         IObjModel,   1,  0xFF,    0x98,    NEXT),
OPDEF("CEE_LDELEM_R8",                  "ldelem.r8",        PopRef+PopI,        PushR8,      InlineNone,         IObjModel,   1,  0xFF,    0x99,    NEXT),
OPDEF("CEE_LDELEM_REF",                 "ldelem.ref",       PopRef+PopI,        PushRef,     InlineNone,         IObjModel,   1,  0xFF,    0x9A,    NEXT),
OPDEF("CEE_STELEM_I",                   "stelem.i",         PopRef+PopI+PopI,   Push0,       InlineNone,         IObjModel,   1,  0xFF,    0x9B,    NEXT),
OPDEF("CEE_STELEM_I1",                  "stelem.i1",        PopRef+PopI+PopI,   Push0,       InlineNone,         IObjModel,   1,  0xFF,    0x9C,    NEXT),
OPDEF("CEE_STELEM_I2",                  "stelem.i2",        PopRef+PopI+PopI,   Push0,       InlineNone,         IObjModel,   1,  0xFF,    0x9D,    NEXT),
OPDEF("CEE_STELEM_I4",                  "stelem.i4",        PopRef+PopI+PopI,   Push0,       InlineNone,         IObjModel,   1,  0xFF,    0x9E,    NEXT),
OPDEF("CEE_STELEM_I8",                  "stelem.i8",        PopRef+PopI+PopI8,  Push0,       InlineNone,         IObjModel,   1,  0xFF,    0x9F,    NEXT),
OPDEF("CEE_STELEM_R4",                  "stelem.r4",        PopRef+PopI+PopR4,  Push0,       InlineNone,         IObjModel,   1,  0xFF,    0xA0,    NEXT),
OPDEF("CEE_STELEM_R8",                  "stelem.r8",        PopRef+PopI+PopR8,  Push0,       InlineNone,         IObjModel,   1,  0xFF,    0xA1,    NEXT),
OPDEF("CEE_STELEM_REF",                 "stelem.ref",       PopRef+PopI+PopRef, Push0,       InlineNone,         IObjModel,   1,  0xFF,    0xA2,    NEXT),
OPDEF("CEE_UNUSED2",                    "unused",           Pop0,               Push0,       InlineNone,         IPrimitive,  1,  0xFF,    0xA3,    NEXT),
OPDEF("CEE_UNUSED3",                    "unused",           Pop0,               Push0,       InlineNone,         IPrimitive,  1,  0xFF,    0xA4,    NEXT),
OPDEF("CEE_UNUSED4",                    "unused",           Pop0,               Push0,       InlineNone,         IPrimitive,  1,  0xFF,    0xA5,    NEXT),
OPDEF("CEE_UNUSED5",                    "unused",           Pop0,               Push0,       InlineNone,         IPrimitive,  1,  0xFF,    0xA6,    NEXT),
OPDEF("CEE_UNUSED6",                    "unused",           Pop0,               Push0,       InlineNone,         IPrimitive,  1,  0xFF,    0xA7,    NEXT),
OPDEF("CEE_UNUSED7",                    "unused",           Pop0,               Push0,       InlineNone,         IPrimitive,  1,  0xFF,    0xA8,    NEXT),
OPDEF("CEE_UNUSED8",                    "unused",           Pop0,               Push0,       InlineNone,         IPrimitive,  1,  0xFF,    0xA9,    NEXT),
OPDEF("CEE_UNUSED9",                    "unused",           Pop0,               Push0,       InlineNone,         IPrimitive,  1,  0xFF,    0xAA,    NEXT),
OPDEF("CEE_UNUSED10",                   "unused",           Pop0,               Push0,       InlineNone,         IPrimitive,  1,  0xFF,    0xAB,    NEXT),
OPDEF("CEE_UNUSED11",                   "unused",           Pop0,               Push0,       InlineNone,         IPrimitive,  1,  0xFF,    0xAC,    NEXT),
OPDEF("CEE_UNUSED12",                   "unused",           Pop0,               Push0,       InlineNone,         IPrimitive,  1,  0xFF,    0xAD,    NEXT),
OPDEF("CEE_UNUSED13",                   "unused",           Pop0,               Push0,       InlineNone,         IPrimitive,  1,  0xFF,    0xAE,    NEXT),
OPDEF("CEE_UNUSED14",                   "unused",           Pop0,               Push0,       InlineNone,         IPrimitive,  1,  0xFF,    0xAF,    NEXT),
OPDEF("CEE_UNUSED15",                   "unused",           Pop0,               Push0,       InlineNone,         IPrimitive,  1,  0xFF,    0xB0,    NEXT),
OPDEF("CEE_UNUSED16",                   "unused",           Pop0,               Push0,       InlineNone,         IPrimitive,  1,  0xFF,    0xB1,    NEXT),
OPDEF("CEE_UNUSED17",                   "unused",           Pop0,               Push0,       InlineNone,         IPrimitive,  1,  0xFF,    0xB2,    NEXT),
OPDEF("CEE_CONV_OVF_I1",                "conv.ovf.i1",      Pop1,               PushI,       InlineNone,         IPrimitive,  1,  0xFF,    0xB3,    NEXT),
OPDEF("CEE_CONV_OVF_U1",                "conv.ovf.u1",      Pop1,               PushI,       InlineNone,         IPrimitive,  1,  0xFF,    0xB4,    NEXT),
OPDEF("CEE_CONV_OVF_I2",                "conv.ovf.i2",      Pop1,               PushI,       InlineNone,         IPrimitive,  1,  0xFF,    0xB5,    NEXT),
OPDEF("CEE_CONV_OVF_U2",                "conv.ovf.u2",      Pop1,               PushI,       InlineNone,         IPrimitive,  1,  0xFF,    0xB6,    NEXT),
OPDEF("CEE_CONV_OVF_I4",                "conv.ovf.i4",      Pop1,               PushI,       InlineNone,         IPrimitive,  1,  0xFF,    0xB7,    NEXT),
OPDEF("CEE_CONV_OVF_U4",                "conv.ovf.u4",      Pop1,               PushI,       InlineNone,         IPrimitive,  1,  0xFF,    0xB8,    NEXT),
OPDEF("CEE_CONV_OVF_I8",                "conv.ovf.i8",      Pop1,               PushI8,      InlineNone,         IPrimitive,  1,  0xFF,    0xB9,    NEXT),
OPDEF("CEE_CONV_OVF_U8",                "conv.ovf.u8",      Pop1,               PushI8,      InlineNone,         IPrimitive,  1,  0xFF,    0xBA,    NEXT),
OPDEF("CEE_UNUSED50",                   "unused",           Pop0,               Push0,       InlineNone,         IPrimitive,  1,  0xFF,    0xBB,    NEXT),
OPDEF("CEE_UNUSED18",                   "unused",           Pop0,               Push0,       InlineNone,         IPrimitive,  1,  0xFF,    0xBC,    NEXT),
OPDEF("CEE_UNUSED19",                   "unused",           Pop0,               Push0,       InlineNone,         IPrimitive,  1,  0xFF,    0xBD,    NEXT),
OPDEF("CEE_UNUSED20",                   "unused",           Pop0,               Push0,       InlineNone,         IPrimitive,  1,  0xFF,    0xBE,    NEXT),
OPDEF("CEE_UNUSED21",                   "unused",           Pop0,               Push0,       InlineNone,         IPrimitive,  1,  0xFF,    0xBF,    NEXT),
OPDEF("CEE_UNUSED22",                   "unused",           Pop0,               Push0,       InlineNone,         IPrimitive,  1,  0xFF,    0xC0,    NEXT),
OPDEF("CEE_UNUSED23",                   "unused",           Pop0,               Push0,       InlineNone,         IPrimitive,  1,  0xFF,    0xC1,    NEXT),
OPDEF("CEE_REFANYVAL",                  "refanyval",        Pop1,               PushI,       InlineType,         IPrimitive,  1,  0xFF,    0xC2,    NEXT),
OPDEF("CEE_CKFINITE",                   "ckfinite",         Pop1,               PushR8,      InlineNone,         IPrimitive,  1,  0xFF,    0xC3,    NEXT),
OPDEF("CEE_UNUSED24",                   "unused",           Pop0,               Push0,       InlineNone,         IPrimitive,  1,  0xFF,    0xC4,    NEXT),
OPDEF("CEE_UNUSED25",                   "unused",           Pop0,               Push0,       InlineNone,         IPrimitive,  1,  0xFF,    0xC5,    NEXT),
OPDEF("CEE_MKREFANY",                   "mkrefany",         PopI,               Push1,       InlineType,         IPrimitive,  1,  0xFF,    0xC6,    NEXT),
OPDEF("CEE_UNUSED59",                   "unused",           Pop0,               Push0,       InlineNone,         IPrimitive,  1,  0xFF,    0xC7,    NEXT),
OPDEF("CEE_UNUSED60",                   "unused",           Pop0,               Push0,       InlineNone,         IPrimitive,  1,  0xFF,    0xC8,    NEXT),
OPDEF("CEE_UNUSED61",                   "unused",           Pop0,               Push0,       InlineNone,         IPrimitive,  1,  0xFF,    0xC9,    NEXT),
OPDEF("CEE_UNUSED62",                   "unused",           Pop0,               Push0,       InlineNone,         IPrimitive,  1,  0xFF,    0xCA,    NEXT),
OPDEF("CEE_UNUSED63",                   "unused",           Pop0,               Push0,       InlineNone,         IPrimitive,  1,  0xFF,    0xCB,    NEXT),
OPDEF("CEE_UNUSED64",                   "unused",           Pop0,               Push0,       InlineNone,         IPrimitive,  1,  0xFF,    0xCC,    NEXT),
OPDEF("CEE_UNUSED65",                   "unused",           Pop0,               Push0,       InlineNone,         IPrimitive,  1,  0xFF,    0xCD,    NEXT),
OPDEF("CEE_UNUSED66",                   "unused",           Pop0,               Push0,       InlineNone,         IPrimitive,  1,  0xFF,    0xCE,    NEXT),
OPDEF("CEE_UNUSED67",                   "unused",           Pop0,               Push0,       InlineNone,         IPrimitive,  1,  0xFF,    0xCF,    NEXT),
OPDEF("CEE_LDTOKEN",                    "ldtoken",          Pop0,               PushI,       InlineTok,          IPrimitive,  1,  0xFF,    0xD0,    NEXT),
OPDEF("CEE_CONV_U2",                    "conv.u2",          Pop1,               PushI,       InlineNone,         IPrimitive,  1,  0xFF,    0xD1,    NEXT),
OPDEF("CEE_CONV_U1",                    "conv.u1",          Pop1,               PushI,       InlineNone,         IPrimitive,  1,  0xFF,    0xD2,    NEXT),
OPDEF("CEE_CONV_I",                     "conv.i",           Pop1,               PushI,       InlineNone,         IPrimitive,  1,  0xFF,    0xD3,    NEXT),
OPDEF("CEE_CONV_OVF_I",                 "conv.ovf.i",       Pop1,               PushI,       InlineNone,         IPrimitive,  1,  0xFF,    0xD4,    NEXT),
OPDEF("CEE_CONV_OVF_U",                 "conv.ovf.u",       Pop1,               PushI,       InlineNone,         IPrimitive,  1,  0xFF,    0xD5,    NEXT),
OPDEF("CEE_ADD_OVF",                    "add.ovf",          Pop1+Pop1,          Push1,       InlineNone,         IPrimitive,  1,  0xFF,    0xD6,    NEXT),
OPDEF("CEE_ADD_OVF_UN",                 "add.ovf.un",       Pop1+Pop1,          Push1,       InlineNone,         IPrimitive,  1,  0xFF,    0xD7,    NEXT),
OPDEF("CEE_MUL_OVF",                    "mul.ovf",          Pop1+Pop1,          Push1,       InlineNone,         IPrimitive,  1,  0xFF,    0xD8,    NEXT),
OPDEF("CEE_MUL_OVF_UN",                 "mul.ovf.un",       Pop1+Pop1,          Push1,       InlineNone,         IPrimitive,  1,  0xFF,    0xD9,    NEXT),
OPDEF("CEE_SUB_OVF",                    "sub.ovf",          Pop1+Pop1,          Push1,       InlineNone,         IPrimitive,  1,  0xFF,    0xDA,    NEXT),
OPDEF("CEE_SUB_OVF_UN",                 "sub.ovf.un",       Pop1+Pop1,          Push1,       InlineNone,         IPrimitive,  1,  0xFF,    0xDB,    NEXT),
OPDEF("CEE_ENDFINALLY",                 "endfinally",       Pop0,               Push0,       InlineNone,         IPrimitive,  1,  0xFF,    0xDC,    RETURN),
OPDEF("CEE_LEAVE",                      "leave",            Pop0,               Push0,       InlineBrTarget,     IPrimitive,  1,  0xFF,    0xDD,    BRANCH),
OPDEF("CEE_LEAVE_S",                    "leave.s",          Pop0,               Push0,       ShortInlineBrTarget,IPrimitive,  1,  0xFF,    0xDE,    BRANCH),
OPDEF("CEE_STIND_I",                    "stind.i",          PopI+PopI,          Push0,       InlineNone,         IPrimitive,  1,  0xFF,    0xDF,    NEXT),
OPDEF("CEE_CONV_U",                     "conv.u",           Pop1,               PushI,       InlineNone,         IPrimitive,  1,  0xFF,    0xE0,    NEXT),
OPDEF("CEE_UNUSED26",                   "unused",           Pop0,               Push0,       InlineNone,         IPrimitive,  1,  0xFF,    0xE1,    NEXT),
OPDEF("CEE_UNUSED27",                   "unused",           Pop0,               Push0,       InlineNone,         IPrimitive,  1,  0xFF,    0xE2,    NEXT),
OPDEF("CEE_UNUSED28",                   "unused",           Pop0,               Push0,       InlineNone,         IPrimitive,  1,  0xFF,    0xE3,    NEXT),
OPDEF("CEE_UNUSED29",                   "unused",           Pop0,               Push0,       InlineNone,         IPrimitive,  1,  0xFF,    0xE4,    NEXT),
OPDEF("CEE_UNUSED30",                   "unused",           Pop0,               Push0,       InlineNone,         IPrimitive,  1,  0xFF,    0xE5,    NEXT),
OPDEF("CEE_UNUSED31",                   "unused",           Pop0,               Push0,       InlineNone,         IPrimitive,  1,  0xFF,    0xE6,    NEXT),
OPDEF("CEE_UNUSED32",                   "unused",           Pop0,               Push0,       InlineNone,         IPrimitive,  1,  0xFF,    0xE7,    NEXT),
OPDEF("CEE_UNUSED33",                   "unused",           Pop0,               Push0,       InlineNone,         IPrimitive,  1,  0xFF,    0xE8,    NEXT),
OPDEF("CEE_UNUSED34",                   "unused",           Pop0,               Push0,       InlineNone,         IPrimitive,  1,  0xFF,    0xE9,    NEXT),
OPDEF("CEE_UNUSED35",                   "unused",           Pop0,               Push0,       InlineNone,         IPrimitive,  1,  0xFF,    0xEA,    NEXT),
OPDEF("CEE_UNUSED36",                   "unused",           Pop0,               Push0,       InlineNone,         IPrimitive,  1,  0xFF,    0xEB,    NEXT),
OPDEF("CEE_UNUSED37",                   "unused",           Pop0,               Push0,       InlineNone,         IPrimitive,  1,  0xFF,    0xEC,    NEXT),
OPDEF("CEE_UNUSED38",                   "unused",           Pop0,               Push0,       InlineNone,         IPrimitive,  1,  0xFF,    0xED,    NEXT),
OPDEF("CEE_UNUSED39",                   "unused",           Pop0,               Push0,       InlineNone,         IPrimitive,  1,  0xFF,    0xEE,    NEXT),
OPDEF("CEE_UNUSED40",                   "unused",           Pop0,               Push0,       InlineNone,         IPrimitive,  1,  0xFF,    0xEF,    NEXT),
OPDEF("CEE_UNUSED41",                   "unused",           Pop0,               Push0,       InlineNone,         IPrimitive,  1,  0xFF,    0xF0,    NEXT),
OPDEF("CEE_UNUSED42",                   "unused",           Pop0,               Push0,       InlineNone,         IPrimitive,  1,  0xFF,    0xF1,    NEXT),
OPDEF("CEE_UNUSED43",                   "unused",           Pop0,               Push0,       InlineNone,         IPrimitive,  1,  0xFF,    0xF2,    NEXT),
OPDEF("CEE_UNUSED44",                   "unused",           Pop0,               Push0,       InlineNone,         IPrimitive,  1,  0xFF,    0xF3,    NEXT),
OPDEF("CEE_UNUSED45",                   "unused",           Pop0,               Push0,       InlineNone,         IPrimitive,  1,  0xFF,    0xF4,    NEXT),
OPDEF("CEE_UNUSED46",                   "unused",           Pop0,               Push0,       InlineNone,         IPrimitive,  1,  0xFF,    0xF5,    NEXT),
OPDEF("CEE_UNUSED47",                   "unused",           Pop0,               Push0,       InlineNone,         IPrimitive,  1,  0xFF,    0xF6,    NEXT),
OPDEF("CEE_UNUSED48",                   "unused",           Pop0,               Push0,       InlineNone,         IPrimitive,  1,  0xFF,    0xF7,    NEXT),
OPDEF("CEE_PREFIX7",                    "prefix7",          Pop0,               Push0,       InlineNone,         IInternal,   1,  0xFF,    0xF8,    META),
OPDEF("CEE_PREFIX6",                    "prefix6",          Pop0,               Push0,       InlineNone,         IInternal,   1,  0xFF,    0xF9,    META),
OPDEF("CEE_PREFIX5",                    "prefix5",          Pop0,               Push0,       InlineNone,         IInternal,   1,  0xFF,    0xFA,    META),
OPDEF("CEE_PREFIX4",                    "prefix4",          Pop0,               Push0,       InlineNone,         IInternal,   1,  0xFF,    0xFB,    META),
OPDEF("CEE_PREFIX3",                    "prefix3",          Pop0,               Push0,       InlineNone,         IInternal,   1,  0xFF,    0xFC,    META),
OPDEF("CEE_PREFIX2",                    "prefix2",          Pop0,               Push0,       InlineNone,         IInternal,   1,  0xFF,    0xFD,    META),
OPDEF("CEE_PREFIX1",                    "prefix1",          Pop0,               Push0,       InlineNone,         IInternal,   1,  0xFF,    0xFE,    META),
OPDEF("CEE_PREFIXREF",                  "prefixref",        Pop0,               Push0,       InlineNone,         IInternal,   1,  0xFF,    0xFF,    META),
OPDEF("CEE_ARGLIST",                    "arglist",          Pop0,               PushI,       InlineNone,         IPrimitive,  2,  0xFE,    0x00,    NEXT),
OPDEF("CEE_CEQ",                        "ceq",              Pop1+Pop1,          PushI,       InlineNone,         IPrimitive,  2,  0xFE,    0x01,    NEXT),
OPDEF("CEE_CGT",                        "cgt",              Pop1+Pop1,          PushI,       InlineNone,         IPrimitive,  2,  0xFE,    0x02,    NEXT),
OPDEF("CEE_CGT_UN",                     "cgt.un",           Pop1+Pop1,          PushI,       InlineNone,         IPrimitive,  2,  0xFE,    0x03,    NEXT),
OPDEF("CEE_CLT",                        "clt",              Pop1+Pop1,          PushI,       InlineNone,         IPrimitive,  2,  0xFE,    0x04,    NEXT),
OPDEF("CEE_CLT_UN",                     "clt.un",           Pop1+Pop1,          PushI,       InlineNone,         IPrimitive,  2,  0xFE,    0x05,    NEXT),
OPDEF("CEE_LDFTN",                      "ldftn",            Pop0,               PushI,       InlineMethod,       IPrimitive,  2,  0xFE,    0x06,    NEXT),
OPDEF("CEE_LDVIRTFTN",                  "ldvirtftn",        PopRef,             PushI,       InlineMethod,       IPrimitive,  2,  0xFE,    0x07,    NEXT),
OPDEF("CEE_UNUSED56",                   "unused",           Pop0,               Push0,       InlineNone,         IPrimitive,  2,  0xFE,    0x08,    NEXT),
OPDEF("CEE_LDARG",                      "ldarg",            Pop0,               Push1,       InlineVar,          IPrimitive,  2,  0xFE,    0x09,    NEXT),
OPDEF("CEE_LDARGA",                     "ldarga",           Pop0,               PushI,       InlineVar,          IPrimitive,  2,  0xFE,    0x0A,    NEXT),
OPDEF("CEE_STARG",                      "starg",            Pop1,               Push0,       InlineVar,          IPrimitive,  2,  0xFE,    0x0B,    NEXT),
OPDEF("CEE_LDLOC",                      "ldloc",            Pop0,               Push1,       InlineVar,          IPrimitive,  2,  0xFE,    0x0C,    NEXT),
OPDEF("CEE_LDLOCA",                     "ldloca",           Pop0,               PushI,       InlineVar,          IPrimitive,  2,  0xFE,    0x0D,    NEXT),
OPDEF("CEE_STLOC",                      "stloc",            Pop1,               Push0,       InlineVar,          IPrimitive,  2,  0xFE,    0x0E,    NEXT),
OPDEF("CEE_LOCALLOC",                   "localloc",         PopI,               PushI,       InlineNone,         IPrimitive,  2,  0xFE,    0x0F,    NEXT),
OPDEF("CEE_UNUSED57",                   "unused",           Pop0,               Push0,       InlineNone,         IPrimitive,  2,  0xFE,    0x10,    NEXT),
OPDEF("CEE_ENDFILTER",                  "endfilter",        PopI,               Push0,       InlineNone,         IPrimitive,  2,  0xFE,    0x11,    RETURN),
OPDEF("CEE_UNALIGNED",                  "unaligned.",       Pop0,               Push0,       ShortInlineI,       IPrefix,     2,  0xFE,    0x12,    META),
OPDEF("CEE_VOLATILE",                   "volatile.",        Pop0,               Push0,       InlineNone,         IPrefix,     2,  0xFE,    0x13,    META),
OPDEF("CEE_TAILCALL",                   "tail.",            Pop0,               Push0,       InlineNone,         IPrefix,     2,  0xFE,    0x14,    META),
OPDEF("CEE_INITOBJ",                    "initobj",          PopI,               Push0,       InlineType,         IObjModel,   2,  0xFE,    0x15,    NEXT),
OPDEF("CEE_UNUSED68",                   "unused",           Pop0,               Push0,       InlineNone,         IPrimitive,  2,  0xFE,    0x16,    NEXT),
OPDEF("CEE_CPBLK",                      "cpblk",            PopI+PopI+PopI,     Push0,       InlineNone,         IPrimitive,  2,  0xFE,    0x17,    NEXT),
OPDEF("CEE_INITBLK",                    "initblk",          PopI+PopI+PopI,     Push0,       InlineNone,         IPrimitive,  2,  0xFE,    0x18,    NEXT),
OPDEF("CEE_UNUSED69",                   "unused",           Pop0,               Push0,       InlineNone,         IPrimitive,  2,  0xFE,    0x19,    NEXT),
OPDEF("CEE_RETHROW",                    "rethrow",          Pop0,               Push0,       InlineNone,         IObjModel,   2,  0xFE,    0x1A,    THROW),
OPDEF("CEE_UNUSED51",                   "unused",           Pop0,               Push0,       InlineNone,         IPrimitive,  2,  0xFE,    0x1B,    NEXT),
OPDEF("CEE_SIZEOF",                     "sizeof",           Pop0,               PushI,       InlineType,         IPrimitive,  2,  0xFE,    0x1C,    NEXT),
OPDEF("CEE_REFANYTYPE",                 "refanytype",       Pop1,               PushI,       InlineNone,         IPrimitive,  2,  0xFE,    0x1D,    NEXT),
OPDEF("CEE_UNUSED52",                   "unused",           Pop0,               Push0,       InlineNone,         IPrimitive,  2,  0xFE,    0x1E,    NEXT),
OPDEF("CEE_UNUSED53",                   "unused",           Pop0,               Push0,       InlineNone,         IPrimitive,  2,  0xFE,    0x1F,    NEXT),
OPDEF("CEE_UNUSED54",                   "unused",           Pop0,               Push0,       InlineNone,         IPrimitive,  2,  0xFE,    0x20,    NEXT),
OPDEF("CEE_UNUSED55",                   "unused",           Pop0,               Push0,       InlineNone,         IPrimitive,  2,  0xFE,    0x21,    NEXT),
OPDEF("CEE_UNUSED70",                   "unused",           Pop0,               Push0,       InlineNone,         IPrimitive,  2,  0xFE,    0x22,    NEXT),
]

@dataclasses.dataclass
class CILInstruction:
    offset: int
    opcode: OPDEF
    argument: Optional[Any]
    jump_offset: Optional[int]

    def __str__(self):
        if self.jump_offset:
            return f"{self.opcode.name} {self.argument} (IL_{self.jump_offset:04x})"
        if self.argument:
            return f"{self.opcode.name} {self.argument}"
        return f"{self.opcode.name}"



opcode_map: Dict[int, OPDEF] = {}
for opcode in opcodes:
    if opcode.first_byte == 0xFF:
        # single byte opcode
        opcode_map[opcode.second_byte] = opcode
    else:
        opcode_map[opcode.first_byte + opcode.second_byte] = opcode


def cil_instructions(il, symbols) -> List[CILInstruction]:
    i = iter(il)
    instructions: List[CILInstruction] = []
    try:
        pc = 0
        while True:
            first = next(i)
            if first == 0 and pc == 0:
                raise NotImplementedError(f"CorILMethod_FatFormat not yet supported")

            op = opcode_map[first]
            if op.size == InlineNone:
                if op.cee_code != "CEE_NOP":
                    instructions.append(CILInstruction(pc, op, None, None))
                pc += 1
                continue
            elif op.size == ShortInlineBrTarget:
                target = int.from_bytes((next(i),), byteorder='little', signed=True)
                effective_target = (pc + 2) + target # What is the actual destination address
                instructions.append(CILInstruction(pc, op, target, effective_target))
                pc += 2
                continue
            elif op.size == ShortInlineVar:
                target = int.from_bytes((next(i),), byteorder='little', signed=True)
                instructions.append(CILInstruction(pc, op, target, None))
                pc += 2
                continue
            elif op.size == ShortInlineI:
                target = int.from_bytes((next(i),), byteorder='little', signed=True)
                instructions.append(CILInstruction(pc, op, target, None))
                pc += 2
                continue
            elif op.size == ShortInlineR:
                target = int.from_bytes((next(i), next(i), next(i), next(i)), byteorder='little', signed=True)
                instructions.append(CILInstruction(pc, op, target, None))
                pc += 5
                continue
            elif op.size == InlineBrTarget:
                target = int.from_bytes((next(i), next(i), next(i), next(i)), byteorder='little', signed=True)
                effective_target = (pc + 5) + target # What is the actual destination address
                instructions.append(CILInstruction(pc, op, target, effective_target))
                pc += 5
                continue
            elif op.size == InlineField:
                field = int.from_bytes((next(i), next(i), next(i), next(i)), byteorder='little', signed=True)
                instructions.append(CILInstruction(pc, op, field, None))
                pc += 5
                continue
            elif op.size == InlineR:
                target = struct.unpack('d', bytes((next(i), next(i), next(i), next(i), next(i), next(i), next(i), next(i))))
                instructions.append(CILInstruction(pc, op, target, None))
                pc += 9
                continue
            elif op.size == InlineI:
                target = int.from_bytes((next(i), next(i), next(i), next(i)), byteorder='little', signed=True)
                instructions.append(CILInstruction(pc, op, target, None))
                pc += 5
                continue
            elif op.size == InlineI8:
                target = int.from_bytes((next(i), next(i), next(i), next(i), next(i), next(i), next(i), next(i)), byteorder='little', signed=True)
                instructions.append(CILInstruction(pc, op, target, None))
                pc += 9
                continue
            elif op.size == InlineMethod:
                target = int.from_bytes((next(i), next(i), next(i), next(i)), byteorder='little', signed=True)
                meth = symbols.get(target, target)
                instructions.append(CILInstruction(pc, op, meth, None))
                pc += 5
                continue
            elif op.size == InlineSig:
                target = int.from_bytes((next(i), next(i), next(i), next(i)), byteorder='little', signed=True)
                instructions.append(CILInstruction(pc, op, target, None))
                pc += 5
                continue
            elif op.size == InlineTok:
                target = int.from_bytes((next(i), next(i), next(i), next(i)), byteorder='little', signed=True)
                instructions.append(CILInstruction(pc, op, target, None))
                pc += 5
                continue
            elif op.size == InlineString:
                target = bytearray((next(i), next(i), next(i), next(i))).decode('utf-8')
                instructions.append(CILInstruction(pc, op, target, None))
                pc += 5
                continue
            elif op.size == InlineVar:
                target = int.from_bytes((next(i), next(i)), byteorder='little', signed=True)
                instructions.append(CILInstruction(pc, op, target, None))
                pc += 3
                continue
            else:
                raise NotImplementedError(f"Haven't implemented IL Opcode {op.name} with size {op.size}")

    except StopIteration:
        pass

    return instructions


def print_il(il: bytearray, symbols, offsets=None, bytecodes=None, print_pc=True) -> None:
    """
    Print the CIL sequence

    :param il: A bytearray of ECMA 335 CIL
    :param offsets: A dictionary of Python bytecode offsets
    :param bytecodes: The dictionary of Python bytecode instructions
    :param print_pc: Flag to include the PC offsets in the print
    """
    instructions = cil_instructions(il, symbols)
    for instruction in instructions:
        # See if this is the offset of a matching Python instruction
        if offsets and bytecodes:
            for py_offset, il_offset, _, offset_type in offsets:
                if il_offset == instruction.offset and offset_type == 'instruction':
                    try:
                        python_instruction = bytecodes[py_offset]
                        print(f'// {python_instruction.offset} {python_instruction.opname} - {python_instruction.arg} ({python_instruction.argval})', )
                    except KeyError:
                        warn("Invalid offset {0}".format(offsets))

        pc_label = f"IL_{instruction.offset:04x}: " if print_pc else ""
        print(f"{pc_label}{instruction}")


def flow_graph(f):
    """
    Return a control flow-graph in DOT syntax for the CIL instructions for f

    :param f: The compiled function or code object
    :returns: The Graph in DOT format
    :rtype: ``str``
    """
    _il = il(f)
    result = ""
    if not _il:
        print("No IL for this function, it may not have compiled correctly.")
        return
    instructions = cil_instructions(_il, symbols(f))
    result += """
digraph g {
graph [
rankdir = "LR"
];
node [
fontsize = "16"
shape = "ellipse"
];
edge [
];\n
"""
    block_starts: Set[int] = {0}
    block_jumps = []  # list of tuples (from, to)
    jump_to_block = {}

    # Compile a list of basic block starts
    for idx, instruction in enumerate(instructions):
        if instruction.jump_offset:
            block_starts.add(instruction.jump_offset)
            block_jumps.append((instruction.offset, instruction.jump_offset))
            if instruction.opcode.cee_code not in ["CEE_BR", "CEE_BR_S"]:
                block_starts.add(instructions[idx+1].offset)
                block_jumps.append((instruction.offset, instructions[idx+1].offset))

    in_block = False
    cur_block = None
    labels = []
    for idx, instruction in enumerate(instructions):
        if instruction.offset in block_starts:
            if in_block:
                result += "label = \"" + ' | '.join(labels) + "\"\n"
                labels.clear()
                result += 'shape = "record"\n];\n'
                # Add fall-through jumps
                if instructions[idx-1].opcode.size not in [InlineBrTarget, ShortInlineBrTarget]:
                    if (instructions[idx-1].offset, instruction.offset) not in block_jumps:
                        block_jumps.append((instructions[idx-1].offset, instruction.offset))
                        jump_to_block[instructions[idx-1].offset] = cur_block

            result += f'"block_{instruction.offset:04x}" [\n'
            in_block = True
            cur_block = f"block_{instruction.offset:04x}"
        if instruction.jump_offset:
            jump_to_block[instruction.offset] = cur_block

        labels.append(f"<IL{instruction.offset:04x}> {instruction.offset:04x} : {instruction}")

    if in_block:
        result += "label = \"" + ' | '.join(labels) + "\"\n"
        labels.clear()
        result += 'shape = "record"\n];\n'

    for from_, to in block_jumps:
        resolved_block = jump_to_block[from_]
        result += f'{resolved_block}:IL{from_:04x} -> "block_{to:04x}":IL{to:04x};\n'

    result += "\n}\n"
    return result


def dis(f, include_offsets=False, print_pc=True):
    """
    Disassemble a code object into IL.

    :param f: The compiled function or code object
    :param include_offsets: Flag to print python bytecode offsets as comments
    :param print_pc: Flag to print the memory address of each instruction
    """
    _il = il(f)
    if not _il:
        print("No IL for this function, it may not have compiled correctly.")
        return
    if include_offsets:
        python_instructions = {i.offset: i for i in get_instructions(f)}
        print_il(_il, offsets=get_offsets(f), bytecodes=python_instructions, print_pc=print_pc, symbols=symbols(f))
    else:
        print_il(_il, print_pc=print_pc, symbols=symbols(f))


def dis_native(f, include_offsets=False, print_pc=True) -> None:
    """
    Disassemble and print the JITed code object's native machine code
    :param f: The compiled function or code object
    :param include_offsets: Flag to print python bytecode offsets as comments
    :param print_pc: Flag to print the memory address of each instruction
    """
    if machine() != 'x86_64':
        print("disassembly only supported on x86_64")
        return
    try:
        import distorm3
        from rich.console import Console
        from rich.syntax import Syntax
    except ImportError:
        raise ModuleNotFoundError("Install distorm3 and rich before disassembling native functions")

    _native = native(f)

    if not _native:
        print("No native code for this function, it may not have compiled correctly")
        return
    symbol_table = symbols(f)

    if include_offsets:
        python_instructions = {i.offset: i for i in get_instructions(f)}
        jit_offsets = get_offsets(f)
    else:
        python_instructions = {}
        jit_offsets = []

    code, _, position = _native
    iterable = distorm3.DecodeGenerator(position, bytes(code), distorm3.Decode64Bits)

    disassembled = [(offset, instruction) for (offset, _, instruction, _) in iterable]

    console = Console()
    offsets = [offset for (offset, _) in disassembled]
    instructions = [instruction for (_, instruction) in disassembled]

    syntax = Syntax("", lexer="nasm", theme="ansi_dark")
    highlighted_lines = syntax.highlight("\n".join(instructions)).split("\n")

    for (offset, line) in zip(offsets, highlighted_lines):
        # See if this is the offset of a matching Python instruction
        if include_offsets:
            for py_offset, _, native_offset, offset_type in jit_offsets:
                if native_offset > 0 and (position + native_offset) == offset and offset_type == "instruction":
                    try:
                        instruction = python_instructions[py_offset]
                        console.print(f'; {instruction.offset} {instruction.opname} - {instruction.arg} ({instruction.argval})', style="dim")
                    except KeyError:
                        warn("Invalid offset {0}".format(offsets))
        if print_pc:
            console.print("[grey]%.8x" % offset, style="dim", end=" ")
        console.print(line, end="")
        if include_offsets:
            for py_offset, _, native_offset, offset_type in jit_offsets:
                if native_offset > 0 and (position + native_offset) == offset and offset_type == "call":
                    try:
                        console.print(" [grey]; %s" % symbol_table[py_offset], style="dim", end="")
                    except KeyError:
                        warn("Invalid offset {0}".format(offsets))
        console.print('')  # force line-sep

