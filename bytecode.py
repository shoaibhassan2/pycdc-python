import enum
from typing import TextIO, Optional, Tuple, TYPE_CHECKING
from data import PycBuffer, formatted_print
from pyc_module import PycModule
from pyc_code import PycCode
from data import PycBuffer, formatted_print


class Opcode(enum.IntEnum):
    # =========================================================================
    #  STANDARD OPCODES (No Argument)
    # =========================================================================
    STOP_CODE = 0
    POP_TOP = 1
    ROT_TWO = 2
    ROT_THREE = 3
    DUP_TOP = 4
    DUP_TOP_TWO = 5
    UNARY_POSITIVE = 6
    UNARY_NEGATIVE = 7
    UNARY_NOT = 8
    UNARY_CONVERT = 9
    UNARY_CALL = 10
    UNARY_INVERT = 11
    BINARY_POWER = 12
    BINARY_MULTIPLY = 13
    BINARY_DIVIDE = 14
    BINARY_MODULO = 15
    BINARY_ADD = 16
    BINARY_SUBTRACT = 17
    BINARY_SUBSCR = 18
    BINARY_CALL = 19
    SLICE_0 = 20
    SLICE_1 = 21
    SLICE_2 = 22
    SLICE_3 = 23
    STORE_SLICE_0 = 24
    STORE_SLICE_1 = 25
    STORE_SLICE_2 = 26
    STORE_SLICE_3 = 27
    DELETE_SLICE_0 = 28
    DELETE_SLICE_1 = 29
    DELETE_SLICE_2 = 30
    DELETE_SLICE_3 = 31
    STORE_SUBSCR = 32
    DELETE_SUBSCR = 33
    BINARY_LSHIFT = 34
    BINARY_RSHIFT = 35
    BINARY_AND = 36
    BINARY_XOR = 37
    BINARY_OR = 38
    PRINT_EXPR = 39
    PRINT_ITEM = 40
    PRINT_NEWLINE = 41
    BREAK_LOOP = 42
    RAISE_EXCEPTION = 43
    LOAD_LOCALS = 44
    RETURN_VALUE = 45
    LOAD_GLOBALS = 46
    EXEC_STMT = 47
    BUILD_FUNCTION = 48
    POP_BLOCK = 49
    END_FINALLY = 50
    BUILD_CLASS = 51
    ROT_FOUR = 52
    NOP = 53
    LIST_APPEND = 54
    BINARY_FLOOR_DIVIDE = 55
    BINARY_TRUE_DIVIDE = 56
    INPLACE_FLOOR_DIVIDE = 57
    INPLACE_TRUE_DIVIDE = 58
    GET_LEN = 59
    MATCH_MAPPING = 60
    MATCH_SEQUENCE = 61
    MATCH_KEYS = 62
    COPY_DICT_WITHOUT_KEYS = 63
    STORE_MAP = 64
    INPLACE_ADD = 65
    INPLACE_SUBTRACT = 66
    INPLACE_MULTIPLY = 67
    INPLACE_DIVIDE = 68
    INPLACE_MODULO = 69
    INPLACE_POWER = 70
    GET_ITER = 71
    PRINT_ITEM_TO = 72
    PRINT_NEWLINE_TO = 73
    INPLACE_LSHIFT = 74
    INPLACE_RSHIFT = 75
    INPLACE_AND = 76
    INPLACE_XOR = 77
    INPLACE_OR = 78
    WITH_CLEANUP = 79
    WITH_CLEANUP_START = 80
    WITH_CLEANUP_FINISH = 81
    IMPORT_STAR = 82
    SETUP_ANNOTATIONS = 83
    YIELD_VALUE = 84
    LOAD_BUILD_CLASS = 85
    STORE_LOCALS = 86
    POP_EXCEPT = 87
    SET_ADD = 88
    YIELD_FROM = 89
    BINARY_MATRIX_MULTIPLY = 90
    INPLACE_MATRIX_MULTIPLY = 91
    GET_AITER = 92
    GET_ANEXT = 93
    BEFORE_ASYNC_WITH = 94
    GET_YIELD_FROM_ITER = 95
    GET_AWAITABLE = 96
    BEGIN_FINALLY = 97
    END_ASYNC_FOR = 98
    RERAISE = 99
    WITH_EXCEPT_START = 100
    LOAD_ASSERTION_ERROR = 101
    LIST_TO_TUPLE = 102
    CACHE = 103
    PUSH_NULL = 104
    PUSH_EXC_INFO = 105
    CHECK_EXC_MATCH = 106
    CHECK_EG_MATCH = 107
    BEFORE_WITH = 108
    RETURN_GENERATOR = 109
    ASYNC_GEN_WRAP = 110
    PREP_RERAISE_STAR = 111
    INTERPRETER_EXIT = 112
    END_FOR = 113
    END_SEND = 114
    RESERVED = 115
    BINARY_SLICE = 116
    STORE_SLICE = 117
    CLEANUP_THROW = 118
    EXIT_INIT_CHECK = 119
    FORMAT_SIMPLE = 120
    FORMAT_WITH_SPEC = 121
    MAKE_FUNCTION = 122
    TO_BOOL = 123

    # =========================================================================
    #  OPCODES WITH ARGUMENTS (PYC_HAVE_ARG marker)
    # =========================================================================
    
    STORE_NAME_A = 124  # Starts at PYC_HAVE_ARG
    PYC_HAVE_ARG = 124
    
    DELETE_NAME_A = 125
    UNPACK_TUPLE_A = 126
    UNPACK_LIST_A = 127
    UNPACK_ARG_A = 128
    STORE_ATTR_A = 129
    DELETE_ATTR_A = 130
    STORE_GLOBAL_A = 131
    DELETE_GLOBAL_A = 132
    ROT_N_A = 133
    UNPACK_VARARG_A = 134
    LOAD_CONST_A = 135
    LOAD_NAME_A = 136
    BUILD_TUPLE_A = 137
    BUILD_LIST_A = 138
    BUILD_MAP_A = 139
    LOAD_ATTR_A = 140
    COMPARE_OP_A = 141
    IMPORT_NAME_A = 142
    IMPORT_FROM_A = 143
    ACCESS_MODE_A = 144
    JUMP_FORWARD_A = 145
    JUMP_IF_FALSE_A = 146
    JUMP_IF_TRUE_A = 147
    JUMP_ABSOLUTE_A = 148
    FOR_LOOP_A = 149
    LOAD_LOCAL_A = 150
    LOAD_GLOBAL_A = 151
    SET_FUNC_ARGS_A = 152
    SETUP_LOOP_A = 153
    SETUP_EXCEPT_A = 154
    SETUP_FINALLY_A = 155
    RESERVE_FAST_A = 156
    LOAD_FAST_A = 157
    STORE_FAST_A = 158
    DELETE_FAST_A = 159
    GEN_START_A = 160
    SET_LINENO_A = 161
    STORE_ANNOTATION_A = 162
    RAISE_VARARGS_A = 163
    CALL_FUNCTION_A = 164
    MAKE_FUNCTION_A = 165
    BUILD_SLICE_A = 166
    CALL_FUNCTION_VAR_A = 167
    CALL_FUNCTION_KW_A = 168
    CALL_FUNCTION_VAR_KW_A = 169
    CALL_FUNCTION_EX_A = 170
    UNPACK_SEQUENCE_A = 171
    FOR_ITER_A = 172
    DUP_TOPX_A = 173
    BUILD_SET_A = 174
    JUMP_IF_FALSE_OR_POP_A = 175
    JUMP_IF_TRUE_OR_POP_A = 176
    POP_JUMP_IF_FALSE_A = 177
    POP_JUMP_IF_TRUE_A = 178
    CONTINUE_LOOP_A = 179
    MAKE_CLOSURE_A = 180
    LOAD_CLOSURE_A = 181
    LOAD_DEREF_A = 182
    STORE_DEREF_A = 183
    DELETE_DEREF_A = 184
    EXTENDED_ARG_A = 185
    SETUP_WITH_A = 186
    SET_ADD_A = 187
    MAP_ADD_A = 188
    UNPACK_EX_A = 189
    LIST_APPEND_A = 190
    LOAD_CLASSDEREF_A = 191
    MATCH_CLASS_A = 192
    BUILD_LIST_UNPACK_A = 193
    BUILD_MAP_UNPACK_A = 194
    BUILD_MAP_UNPACK_WITH_CALL_A = 195
    BUILD_TUPLE_UNPACK_A = 196
    BUILD_SET_UNPACK_A = 197
    SETUP_ASYNC_WITH_A = 198
    FORMAT_VALUE_A = 199
    BUILD_CONST_KEY_MAP_A = 200
    BUILD_STRING_A = 201
    BUILD_TUPLE_UNPACK_WITH_CALL_A = 202
    LOAD_METHOD_A = 203
    CALL_METHOD_A = 204
    CALL_FINALLY_A = 205
    POP_FINALLY_A = 206
    IS_OP_A = 207
    CONTAINS_OP_A = 208
    RERAISE_A = 209
    JUMP_IF_NOT_EXC_MATCH_A = 210
    LIST_EXTEND_A = 211
    SET_UPDATE_A = 212
    DICT_MERGE_A = 213
    DICT_UPDATE_A = 214
    SWAP_A = 215
    POP_JUMP_FORWARD_IF_FALSE_A = 216
    POP_JUMP_FORWARD_IF_TRUE_A = 217
    COPY_A = 218
    BINARY_OP_A = 219
    SEND_A = 220
    POP_JUMP_FORWARD_IF_NOT_NONE_A = 221
    POP_JUMP_FORWARD_IF_NONE_A = 222
    GET_AWAITABLE_A = 223
    JUMP_BACKWARD_NO_INTERRUPT_A = 224
    MAKE_CELL_A = 225
    JUMP_BACKWARD_A = 226
    COPY_FREE_VARS_A = 227
    RESUME_A = 228
    PRECALL_A = 229
    CALL_A = 230
    KW_NAMES_A = 231
    POP_JUMP_BACKWARD_IF_NOT_NONE_A = 232
    POP_JUMP_BACKWARD_IF_NONE_A = 233
    POP_JUMP_BACKWARD_IF_FALSE_A = 234
    POP_JUMP_BACKWARD_IF_TRUE_A = 235
    RETURN_CONST_A = 236
    LOAD_FAST_CHECK_A = 237
    POP_JUMP_IF_NOT_NONE_A = 238
    POP_JUMP_IF_NONE_A = 239
    LOAD_SUPER_ATTR_A = 240
    LOAD_FAST_AND_CLEAR_A = 241
    YIELD_VALUE_A = 242
    CALL_INTRINSIC_1_A = 243
    CALL_INTRINSIC_2_A = 244
    LOAD_FROM_DICT_OR_GLOBALS_A = 245
    LOAD_FROM_DICT_OR_DEREF_A = 246
    CALL_KW_A = 247
    CONVERT_VALUE_A = 248
    ENTER_EXECUTOR_A = 249
    LOAD_FAST_LOAD_FAST_A = 250
    SET_FUNCTION_ATTRIBUTE_A = 251
    STORE_FAST_LOAD_FAST_A = 252
    STORE_FAST_STORE_FAST_A = 253

    # =========================================================================
    #  INSTRUMENTED OPCODES
    # =========================================================================
    INSTRUMENTED_LOAD_SUPER_ATTR_A = 254
    INSTRUMENTED_POP_JUMP_IF_NONE_A = 255
    INSTRUMENTED_POP_JUMP_IF_NOT_NONE_A = 256
    INSTRUMENTED_RESUME_A = 257
    INSTRUMENTED_CALL_A = 258
    INSTRUMENTED_RETURN_VALUE_A = 259
    INSTRUMENTED_YIELD_VALUE_A = 260
    INSTRUMENTED_CALL_FUNCTION_EX_A = 261
    INSTRUMENTED_JUMP_FORWARD_A = 262
    INSTRUMENTED_JUMP_BACKWARD_A = 263
    INSTRUMENTED_RETURN_CONST_A = 264
    INSTRUMENTED_FOR_ITER_A = 265
    INSTRUMENTED_POP_JUMP_IF_FALSE_A = 266
    INSTRUMENTED_POP_JUMP_IF_TRUE_A = 267
    INSTRUMENTED_END_FOR_A = 268
    INSTRUMENTED_END_SEND_A = 269
    INSTRUMENTED_INSTRUCTION_A = 270
    INSTRUMENTED_LINE_A = 271
    INSTRUMENTED_CALL_KW_A = 272

    # =========================================================================
    #  META / INVALID
    # =========================================================================
    PYC_LAST_OPCODE = 273
    PYC_INVALID_OPCODE = -1

# Disassembly Flags
DISASM_PYCODE_VERBOSE = 0x1
DISASM_SHOW_CACHES = 0x2

# =========================================================================
#  VERSION MAPPINGS
# =========================================================================
def python_1_1_map(id_: int) -> int:
    mapping = {
        0:  Opcode.STOP_CODE,
        1:  Opcode.POP_TOP,
        2:  Opcode.ROT_TWO,
        3:  Opcode.ROT_THREE,
        4:  Opcode.DUP_TOP,

        10: Opcode.UNARY_POSITIVE,
        11: Opcode.UNARY_NEGATIVE,
        12: Opcode.UNARY_NOT,
        13: Opcode.UNARY_CONVERT,
        14: Opcode.UNARY_CALL,
        15: Opcode.UNARY_INVERT,

        20: Opcode.BINARY_MULTIPLY,
        21: Opcode.BINARY_DIVIDE,
        22: Opcode.BINARY_MODULO,
        23: Opcode.BINARY_ADD,
        24: Opcode.BINARY_SUBTRACT,
        25: Opcode.BINARY_SUBSCR,
        26: Opcode.BINARY_CALL,

        30: Opcode.SLICE_0,
        31: Opcode.SLICE_1,
        32: Opcode.SLICE_2,
        33: Opcode.SLICE_3,

        40: Opcode.STORE_SLICE_0,
        41: Opcode.STORE_SLICE_1,
        42: Opcode.STORE_SLICE_2,
        43: Opcode.STORE_SLICE_3,

        50: Opcode.DELETE_SLICE_0,
        51: Opcode.DELETE_SLICE_1,
        52: Opcode.DELETE_SLICE_2,
        53: Opcode.DELETE_SLICE_3,

        60: Opcode.STORE_SUBSCR,
        61: Opcode.DELETE_SUBSCR,
        62: Opcode.BINARY_LSHIFT,
        63: Opcode.BINARY_RSHIFT,
        64: Opcode.BINARY_AND,
        65: Opcode.BINARY_XOR,
        66: Opcode.BINARY_OR,

        70: Opcode.PRINT_EXPR,
        71: Opcode.PRINT_ITEM,
        72: Opcode.PRINT_NEWLINE,

        80: Opcode.BREAK_LOOP,
        81: Opcode.RAISE_EXCEPTION,
        82: Opcode.LOAD_LOCALS,
        83: Opcode.RETURN_VALUE,
        84: Opcode.LOAD_GLOBALS,
        85: Opcode.EXEC_STMT,
        86: Opcode.BUILD_FUNCTION,
        87: Opcode.POP_BLOCK,
        88: Opcode.END_FINALLY,
        89: Opcode.BUILD_CLASS,

        90: Opcode.STORE_NAME_A,
        91: Opcode.DELETE_NAME_A,
        92: Opcode.UNPACK_TUPLE_A,
        93: Opcode.UNPACK_LIST_A,
        94: Opcode.UNPACK_ARG_A,
        95: Opcode.STORE_ATTR_A,
        96: Opcode.DELETE_ATTR_A,
        97: Opcode.STORE_GLOBAL_A,
        98: Opcode.DELETE_GLOBAL_A,
        99: Opcode.UNPACK_VARARG_A,

        100: Opcode.LOAD_CONST_A,
        101: Opcode.LOAD_NAME_A,
        102: Opcode.BUILD_TUPLE_A,
        103: Opcode.BUILD_LIST_A,
        104: Opcode.BUILD_MAP_A,
        105: Opcode.LOAD_ATTR_A,
        106: Opcode.COMPARE_OP_A,
        107: Opcode.IMPORT_NAME_A,
        108: Opcode.IMPORT_FROM_A,
        109: Opcode.ACCESS_MODE_A,

        110: Opcode.JUMP_FORWARD_A,
        111: Opcode.JUMP_IF_FALSE_A,
        112: Opcode.JUMP_IF_TRUE_A,
        113: Opcode.JUMP_ABSOLUTE_A,
        114: Opcode.FOR_LOOP_A,
        115: Opcode.LOAD_LOCAL_A,
        116: Opcode.LOAD_GLOBAL_A,

        120: Opcode.SETUP_LOOP_A,
        121: Opcode.SETUP_EXCEPT_A,
        122: Opcode.SETUP_FINALLY_A,
        123: Opcode.RESERVE_FAST_A,
        124: Opcode.LOAD_FAST_A,
        125: Opcode.STORE_FAST_A,
        126: Opcode.DELETE_FAST_A,
        127: Opcode.SET_LINENO_A,
    }

    return mapping.get(id_)

def python_1_1_map(id_: int) -> int:
    mapping = {
        0:  Opcode.STOP_CODE,
        1:  Opcode.POP_TOP,
        2:  Opcode.ROT_TWO,
        3:  Opcode.ROT_THREE,
        4:  Opcode.DUP_TOP,

        10: Opcode.UNARY_POSITIVE,
        11: Opcode.UNARY_NEGATIVE,
        12: Opcode.UNARY_NOT,
        13: Opcode.UNARY_CONVERT,
        14: Opcode.UNARY_CALL,
        15: Opcode.UNARY_INVERT,

        20: Opcode.BINARY_MULTIPLY,
        21: Opcode.BINARY_DIVIDE,
        22: Opcode.BINARY_MODULO,
        23: Opcode.BINARY_ADD,
        24: Opcode.BINARY_SUBTRACT,
        25: Opcode.BINARY_SUBSCR,
        26: Opcode.BINARY_CALL,

        30: Opcode.SLICE_0,
        31: Opcode.SLICE_1,
        32: Opcode.SLICE_2,
        33: Opcode.SLICE_3,

        40: Opcode.STORE_SLICE_0,
        41: Opcode.STORE_SLICE_1,
        42: Opcode.STORE_SLICE_2,
        43: Opcode.STORE_SLICE_3,

        50: Opcode.DELETE_SLICE_0,
        51: Opcode.DELETE_SLICE_1,
        52: Opcode.DELETE_SLICE_2,
        53: Opcode.DELETE_SLICE_3,

        60: Opcode.STORE_SUBSCR,
        61: Opcode.DELETE_SUBSCR,
        62: Opcode.BINARY_LSHIFT,
        63: Opcode.BINARY_RSHIFT,
        64: Opcode.BINARY_AND,
        65: Opcode.BINARY_XOR,
        66: Opcode.BINARY_OR,

        70: Opcode.PRINT_EXPR,
        71: Opcode.PRINT_ITEM,
        72: Opcode.PRINT_NEWLINE,

        80: Opcode.BREAK_LOOP,
        81: Opcode.RAISE_EXCEPTION,
        82: Opcode.LOAD_LOCALS,
        83: Opcode.RETURN_VALUE,
        84: Opcode.LOAD_GLOBALS,
        85: Opcode.EXEC_STMT,
        86: Opcode.BUILD_FUNCTION,
        87: Opcode.POP_BLOCK,
        88: Opcode.END_FINALLY,
        89: Opcode.BUILD_CLASS,

        90: Opcode.STORE_NAME_A,
        91: Opcode.DELETE_NAME_A,
        92: Opcode.UNPACK_TUPLE_A,
        93: Opcode.UNPACK_LIST_A,
        94: Opcode.UNPACK_ARG_A,
        95: Opcode.STORE_ATTR_A,
        96: Opcode.DELETE_ATTR_A,
        97: Opcode.STORE_GLOBAL_A,
        98: Opcode.DELETE_GLOBAL_A,
        99: Opcode.UNPACK_VARARG_A,

        100: Opcode.LOAD_CONST_A,
        101: Opcode.LOAD_NAME_A,
        102: Opcode.BUILD_TUPLE_A,
        103: Opcode.BUILD_LIST_A,
        104: Opcode.BUILD_MAP_A,
        105: Opcode.LOAD_ATTR_A,
        106: Opcode.COMPARE_OP_A,
        107: Opcode.IMPORT_NAME_A,
        108: Opcode.IMPORT_FROM_A,
        109: Opcode.ACCESS_MODE_A,

        110: Opcode.JUMP_FORWARD_A,
        111: Opcode.JUMP_IF_FALSE_A,
        112: Opcode.JUMP_IF_TRUE_A,
        113: Opcode.JUMP_ABSOLUTE_A,
        114: Opcode.FOR_LOOP_A,
        115: Opcode.LOAD_LOCAL_A,
        116: Opcode.LOAD_GLOBAL_A,
        117: Opcode.SET_FUNC_ARGS_A,

        120: Opcode.SETUP_LOOP_A,
        121: Opcode.SETUP_EXCEPT_A,
        122: Opcode.SETUP_FINALLY_A,
        123: Opcode.RESERVE_FAST_A,
        124: Opcode.LOAD_FAST_A,
        125: Opcode.STORE_FAST_A,
        126: Opcode.DELETE_FAST_A,
        127: Opcode.SET_LINENO_A,
    }

    return mapping.get(id_)

def python_1_3_map(id_: int) -> int:
    mapping = {
        0:  Opcode.STOP_CODE,
        1:  Opcode.POP_TOP,
        2:  Opcode.ROT_TWO,
        3:  Opcode.ROT_THREE,
        4:  Opcode.DUP_TOP,

        10: Opcode.UNARY_POSITIVE,
        11: Opcode.UNARY_NEGATIVE,
        12: Opcode.UNARY_NOT,
        13: Opcode.UNARY_CONVERT,
        15: Opcode.UNARY_INVERT,

        20: Opcode.BINARY_MULTIPLY,
        21: Opcode.BINARY_DIVIDE,
        22: Opcode.BINARY_MODULO,
        23: Opcode.BINARY_ADD,
        24: Opcode.BINARY_SUBTRACT,
        25: Opcode.BINARY_SUBSCR,

        30: Opcode.SLICE_0,
        31: Opcode.SLICE_1,
        32: Opcode.SLICE_2,
        33: Opcode.SLICE_3,

        40: Opcode.STORE_SLICE_0,
        41: Opcode.STORE_SLICE_1,
        42: Opcode.STORE_SLICE_2,
        43: Opcode.STORE_SLICE_3,

        50: Opcode.DELETE_SLICE_0,
        51: Opcode.DELETE_SLICE_1,
        52: Opcode.DELETE_SLICE_2,
        53: Opcode.DELETE_SLICE_3,

        60: Opcode.STORE_SUBSCR,
        61: Opcode.DELETE_SUBSCR,
        62: Opcode.BINARY_LSHIFT,
        63: Opcode.BINARY_RSHIFT,
        64: Opcode.BINARY_AND,
        65: Opcode.BINARY_XOR,
        66: Opcode.BINARY_OR,

        70: Opcode.PRINT_EXPR,
        71: Opcode.PRINT_ITEM,
        72: Opcode.PRINT_NEWLINE,

        80: Opcode.BREAK_LOOP,
        82: Opcode.LOAD_LOCALS,
        83: Opcode.RETURN_VALUE,
        85: Opcode.EXEC_STMT,
        87: Opcode.POP_BLOCK,
        88: Opcode.END_FINALLY,
        89: Opcode.BUILD_CLASS,

        90: Opcode.STORE_NAME_A,
        91: Opcode.DELETE_NAME_A,
        92: Opcode.UNPACK_TUPLE_A,
        93: Opcode.UNPACK_LIST_A,
        94: Opcode.UNPACK_ARG_A,
        95: Opcode.STORE_ATTR_A,
        96: Opcode.DELETE_ATTR_A,
        97: Opcode.STORE_GLOBAL_A,
        98: Opcode.DELETE_GLOBAL_A,
        99: Opcode.UNPACK_VARARG_A,

        100: Opcode.LOAD_CONST_A,
        101: Opcode.LOAD_NAME_A,
        102: Opcode.BUILD_TUPLE_A,
        103: Opcode.BUILD_LIST_A,
        104: Opcode.BUILD_MAP_A,
        105: Opcode.LOAD_ATTR_A,
        106: Opcode.COMPARE_OP_A,
        107: Opcode.IMPORT_NAME_A,
        108: Opcode.IMPORT_FROM_A,
        109: Opcode.ACCESS_MODE_A,

        110: Opcode.JUMP_FORWARD_A,
        111: Opcode.JUMP_IF_FALSE_A,
        112: Opcode.JUMP_IF_TRUE_A,
        113: Opcode.JUMP_ABSOLUTE_A,
        114: Opcode.FOR_LOOP_A,
        115: Opcode.LOAD_LOCAL_A,
        116: Opcode.LOAD_GLOBAL_A,
        117: Opcode.SET_FUNC_ARGS_A,

        120: Opcode.SETUP_LOOP_A,
        121: Opcode.SETUP_EXCEPT_A,
        122: Opcode.SETUP_FINALLY_A,

        124: Opcode.LOAD_FAST_A,
        125: Opcode.STORE_FAST_A,
        126: Opcode.DELETE_FAST_A,
        127: Opcode.SET_LINENO_A,

        130: Opcode.RAISE_VARARGS_A,
        131: Opcode.CALL_FUNCTION_A,
        132: Opcode.MAKE_FUNCTION_A,
    }

    return mapping.get(id_)

def python_1_4_map(id_: int) -> int:
    mapping = {
        0:  Opcode.STOP_CODE,
        1:  Opcode.POP_TOP,
        2:  Opcode.ROT_TWO,
        3:  Opcode.ROT_THREE,
        4:  Opcode.DUP_TOP,

        10: Opcode.UNARY_POSITIVE,
        11: Opcode.UNARY_NEGATIVE,
        12: Opcode.UNARY_NOT,
        13: Opcode.UNARY_CONVERT,
        15: Opcode.UNARY_INVERT,

        19: Opcode.BINARY_POWER,
        20: Opcode.BINARY_MULTIPLY,
        21: Opcode.BINARY_DIVIDE,
        22: Opcode.BINARY_MODULO,
        23: Opcode.BINARY_ADD,
        24: Opcode.BINARY_SUBTRACT,
        25: Opcode.BINARY_SUBSCR,

        30: Opcode.SLICE_0,
        31: Opcode.SLICE_1,
        32: Opcode.SLICE_2,
        33: Opcode.SLICE_3,

        40: Opcode.STORE_SLICE_0,
        41: Opcode.STORE_SLICE_1,
        42: Opcode.STORE_SLICE_2,
        43: Opcode.STORE_SLICE_3,

        50: Opcode.DELETE_SLICE_0,
        51: Opcode.DELETE_SLICE_1,
        52: Opcode.DELETE_SLICE_2,
        53: Opcode.DELETE_SLICE_3,

        60: Opcode.STORE_SUBSCR,
        61: Opcode.DELETE_SUBSCR,
        62: Opcode.BINARY_LSHIFT,
        63: Opcode.BINARY_RSHIFT,
        64: Opcode.BINARY_AND,
        65: Opcode.BINARY_XOR,
        66: Opcode.BINARY_OR,

        70: Opcode.PRINT_EXPR,
        71: Opcode.PRINT_ITEM,
        72: Opcode.PRINT_NEWLINE,

        80: Opcode.BREAK_LOOP,
        82: Opcode.LOAD_LOCALS,
        83: Opcode.RETURN_VALUE,
        85: Opcode.EXEC_STMT,
        87: Opcode.POP_BLOCK,
        88: Opcode.END_FINALLY,
        89: Opcode.BUILD_CLASS,

        90: Opcode.STORE_NAME_A,
        91: Opcode.DELETE_NAME_A,
        92: Opcode.UNPACK_TUPLE_A,
        93: Opcode.UNPACK_LIST_A,
        94: Opcode.UNPACK_ARG_A,
        95: Opcode.STORE_ATTR_A,
        96: Opcode.DELETE_ATTR_A,
        97: Opcode.STORE_GLOBAL_A,
        98: Opcode.DELETE_GLOBAL_A,
        99: Opcode.UNPACK_VARARG_A,

        100: Opcode.LOAD_CONST_A,
        101: Opcode.LOAD_NAME_A,
        102: Opcode.BUILD_TUPLE_A,
        103: Opcode.BUILD_LIST_A,
        104: Opcode.BUILD_MAP_A,
        105: Opcode.LOAD_ATTR_A,
        106: Opcode.COMPARE_OP_A,
        107: Opcode.IMPORT_NAME_A,
        108: Opcode.IMPORT_FROM_A,
        109: Opcode.ACCESS_MODE_A,

        110: Opcode.JUMP_FORWARD_A,
        111: Opcode.JUMP_IF_FALSE_A,
        112: Opcode.JUMP_IF_TRUE_A,
        113: Opcode.JUMP_ABSOLUTE_A,
        114: Opcode.FOR_LOOP_A,
        115: Opcode.LOAD_LOCAL_A,
        116: Opcode.LOAD_GLOBAL_A,
        117: Opcode.SET_FUNC_ARGS_A,

        120: Opcode.SETUP_LOOP_A,
        121: Opcode.SETUP_EXCEPT_A,
        122: Opcode.SETUP_FINALLY_A,

        124: Opcode.LOAD_FAST_A,
        125: Opcode.STORE_FAST_A,
        126: Opcode.DELETE_FAST_A,
        127: Opcode.SET_LINENO_A,

        130: Opcode.RAISE_VARARGS_A,
        131: Opcode.CALL_FUNCTION_A,
        132: Opcode.MAKE_FUNCTION_A,
        133: Opcode.BUILD_SLICE_A,
    }

    return mapping.get(id_)

def python_1_5_map(id_: int) -> int:
    mapping = {
        0:  Opcode.STOP_CODE,
        1:  Opcode.POP_TOP,
        2:  Opcode.ROT_TWO,
        3:  Opcode.ROT_THREE,
        4:  Opcode.DUP_TOP,

        10: Opcode.UNARY_POSITIVE,
        11: Opcode.UNARY_NEGATIVE,
        12: Opcode.UNARY_NOT,
        13: Opcode.UNARY_CONVERT,
        15: Opcode.UNARY_INVERT,

        19: Opcode.BINARY_POWER,
        20: Opcode.BINARY_MULTIPLY,
        21: Opcode.BINARY_DIVIDE,
        22: Opcode.BINARY_MODULO,
        23: Opcode.BINARY_ADD,
        24: Opcode.BINARY_SUBTRACT,
        25: Opcode.BINARY_SUBSCR,

        30: Opcode.SLICE_0,
        31: Opcode.SLICE_1,
        32: Opcode.SLICE_2,
        33: Opcode.SLICE_3,

        40: Opcode.STORE_SLICE_0,
        41: Opcode.STORE_SLICE_1,
        42: Opcode.STORE_SLICE_2,
        43: Opcode.STORE_SLICE_3,

        50: Opcode.DELETE_SLICE_0,
        51: Opcode.DELETE_SLICE_1,
        52: Opcode.DELETE_SLICE_2,
        53: Opcode.DELETE_SLICE_3,

        60: Opcode.STORE_SUBSCR,
        61: Opcode.DELETE_SUBSCR,
        62: Opcode.BINARY_LSHIFT,
        63: Opcode.BINARY_RSHIFT,
        64: Opcode.BINARY_AND,
        65: Opcode.BINARY_XOR,
        66: Opcode.BINARY_OR,

        70: Opcode.PRINT_EXPR,
        71: Opcode.PRINT_ITEM,
        72: Opcode.PRINT_NEWLINE,

        80: Opcode.BREAK_LOOP,
        82: Opcode.LOAD_LOCALS,
        83: Opcode.RETURN_VALUE,
        85: Opcode.EXEC_STMT,
        87: Opcode.POP_BLOCK,
        88: Opcode.END_FINALLY,
        89: Opcode.BUILD_CLASS,

        90: Opcode.STORE_NAME_A,
        91: Opcode.DELETE_NAME_A,
        92: Opcode.UNPACK_TUPLE_A,
        93: Opcode.UNPACK_LIST_A,

        95: Opcode.STORE_ATTR_A,
        96: Opcode.DELETE_ATTR_A,
        97: Opcode.STORE_GLOBAL_A,
        98: Opcode.DELETE_GLOBAL_A,

        100: Opcode.LOAD_CONST_A,
        101: Opcode.LOAD_NAME_A,
        102: Opcode.BUILD_TUPLE_A,
        103: Opcode.BUILD_LIST_A,
        104: Opcode.BUILD_MAP_A,
        105: Opcode.LOAD_ATTR_A,
        106: Opcode.COMPARE_OP_A,
        107: Opcode.IMPORT_NAME_A,
        108: Opcode.IMPORT_FROM_A,

        110: Opcode.JUMP_FORWARD_A,
        111: Opcode.JUMP_IF_FALSE_A,
        112: Opcode.JUMP_IF_TRUE_A,
        113: Opcode.JUMP_ABSOLUTE_A,
        114: Opcode.FOR_LOOP_A,

        116: Opcode.LOAD_GLOBAL_A,

        120: Opcode.SETUP_LOOP_A,
        121: Opcode.SETUP_EXCEPT_A,
        122: Opcode.SETUP_FINALLY_A,

        124: Opcode.LOAD_FAST_A,
        125: Opcode.STORE_FAST_A,
        126: Opcode.DELETE_FAST_A,
        127: Opcode.SET_LINENO_A,

        130: Opcode.RAISE_VARARGS_A,
        131: Opcode.CALL_FUNCTION_A,
        132: Opcode.MAKE_FUNCTION_A,
        133: Opcode.BUILD_SLICE_A,
    }

    return mapping.get(id_)

def python_1_6_map(id_: int) -> int:
    mapping = {
        0:  Opcode.STOP_CODE,
        1:  Opcode.POP_TOP,
        2:  Opcode.ROT_TWO,
        3:  Opcode.ROT_THREE,
        4:  Opcode.DUP_TOP,

        10: Opcode.UNARY_POSITIVE,
        11: Opcode.UNARY_NEGATIVE,
        12: Opcode.UNARY_NOT,
        13: Opcode.UNARY_CONVERT,
        15: Opcode.UNARY_INVERT,

        19: Opcode.BINARY_POWER,
        20: Opcode.BINARY_MULTIPLY,
        21: Opcode.BINARY_DIVIDE,
        22: Opcode.BINARY_MODULO,
        23: Opcode.BINARY_ADD,
        24: Opcode.BINARY_SUBTRACT,
        25: Opcode.BINARY_SUBSCR,

        30: Opcode.SLICE_0,
        31: Opcode.SLICE_1,
        32: Opcode.SLICE_2,
        33: Opcode.SLICE_3,

        40: Opcode.STORE_SLICE_0,
        41: Opcode.STORE_SLICE_1,
        42: Opcode.STORE_SLICE_2,
        43: Opcode.STORE_SLICE_3,

        50: Opcode.DELETE_SLICE_0,
        51: Opcode.DELETE_SLICE_1,
        52: Opcode.DELETE_SLICE_2,
        53: Opcode.DELETE_SLICE_3,

        60: Opcode.STORE_SUBSCR,
        61: Opcode.DELETE_SUBSCR,
        62: Opcode.BINARY_LSHIFT,
        63: Opcode.BINARY_RSHIFT,
        64: Opcode.BINARY_AND,
        65: Opcode.BINARY_XOR,
        66: Opcode.BINARY_OR,

        70: Opcode.PRINT_EXPR,
        71: Opcode.PRINT_ITEM,
        72: Opcode.PRINT_NEWLINE,

        80: Opcode.BREAK_LOOP,
        82: Opcode.LOAD_LOCALS,
        83: Opcode.RETURN_VALUE,
        85: Opcode.EXEC_STMT,
        87: Opcode.POP_BLOCK,
        88: Opcode.END_FINALLY,
        89: Opcode.BUILD_CLASS,

        90: Opcode.STORE_NAME_A,
        91: Opcode.DELETE_NAME_A,
        92: Opcode.UNPACK_TUPLE_A,
        93: Opcode.UNPACK_LIST_A,

        95: Opcode.STORE_ATTR_A,
        96: Opcode.DELETE_ATTR_A,
        97: Opcode.STORE_GLOBAL_A,
        98: Opcode.DELETE_GLOBAL_A,

        100: Opcode.LOAD_CONST_A,
        101: Opcode.LOAD_NAME_A,
        102: Opcode.BUILD_TUPLE_A,
        103: Opcode.BUILD_LIST_A,
        104: Opcode.BUILD_MAP_A,
        105: Opcode.LOAD_ATTR_A,
        106: Opcode.COMPARE_OP_A,
        107: Opcode.IMPORT_NAME_A,
        108: Opcode.IMPORT_FROM_A,

        110: Opcode.JUMP_FORWARD_A,
        111: Opcode.JUMP_IF_FALSE_A,
        112: Opcode.JUMP_IF_TRUE_A,
        113: Opcode.JUMP_ABSOLUTE_A,
        114: Opcode.FOR_LOOP_A,

        116: Opcode.LOAD_GLOBAL_A,

        120: Opcode.SETUP_LOOP_A,
        121: Opcode.SETUP_EXCEPT_A,
        122: Opcode.SETUP_FINALLY_A,

        124: Opcode.LOAD_FAST_A,
        125: Opcode.STORE_FAST_A,
        126: Opcode.DELETE_FAST_A,
        127: Opcode.SET_LINENO_A,

        130: Opcode.RAISE_VARARGS_A,
        131: Opcode.CALL_FUNCTION_A,
        132: Opcode.MAKE_FUNCTION_A,
        133: Opcode.BUILD_SLICE_A,

        140: Opcode.CALL_FUNCTION_VAR_A,
        141: Opcode.CALL_FUNCTION_KW_A,
        142: Opcode.CALL_FUNCTION_VAR_KW_A,
    }

    return mapping.get(id_)

def python_2_0_map(id_: int) -> int:
    mapping = {
        0:  Opcode.STOP_CODE,
        1:  Opcode.POP_TOP,
        2:  Opcode.ROT_TWO,
        3:  Opcode.ROT_THREE,
        4:  Opcode.DUP_TOP,
        5:  Opcode.ROT_FOUR,

        10: Opcode.UNARY_POSITIVE,
        11: Opcode.UNARY_NEGATIVE,
        12: Opcode.UNARY_NOT,
        13: Opcode.UNARY_CONVERT,
        15: Opcode.UNARY_INVERT,

        19: Opcode.BINARY_POWER,
        20: Opcode.BINARY_MULTIPLY,
        21: Opcode.BINARY_DIVIDE,
        22: Opcode.BINARY_MODULO,
        23: Opcode.BINARY_ADD,
        24: Opcode.BINARY_SUBTRACT,
        25: Opcode.BINARY_SUBSCR,

        30: Opcode.SLICE_0,
        31: Opcode.SLICE_1,
        32: Opcode.SLICE_2,
        33: Opcode.SLICE_3,

        40: Opcode.STORE_SLICE_0,
        41: Opcode.STORE_SLICE_1,
        42: Opcode.STORE_SLICE_2,
        43: Opcode.STORE_SLICE_3,

        50: Opcode.DELETE_SLICE_0,
        51: Opcode.DELETE_SLICE_1,
        52: Opcode.DELETE_SLICE_2,
        53: Opcode.DELETE_SLICE_3,

        55: Opcode.INPLACE_ADD,
        56: Opcode.INPLACE_SUBTRACT,
        57: Opcode.INPLACE_MULTIPLY,
        58: Opcode.INPLACE_DIVIDE,
        59: Opcode.INPLACE_MODULO,

        60: Opcode.STORE_SUBSCR,
        61: Opcode.DELETE_SUBSCR,
        62: Opcode.BINARY_LSHIFT,
        63: Opcode.BINARY_RSHIFT,
        64: Opcode.BINARY_AND,
        65: Opcode.BINARY_XOR,
        66: Opcode.BINARY_OR,
        67: Opcode.INPLACE_POWER,

        70: Opcode.PRINT_EXPR,
        71: Opcode.PRINT_ITEM,
        72: Opcode.PRINT_NEWLINE,
        73: Opcode.PRINT_ITEM_TO,
        74: Opcode.PRINT_NEWLINE_TO,

        75: Opcode.INPLACE_LSHIFT,
        76: Opcode.INPLACE_RSHIFT,
        77: Opcode.INPLACE_AND,
        78: Opcode.INPLACE_XOR,
        79: Opcode.INPLACE_OR,

        80: Opcode.BREAK_LOOP,
        82: Opcode.LOAD_LOCALS,
        83: Opcode.RETURN_VALUE,
        84: Opcode.IMPORT_STAR,
        85: Opcode.EXEC_STMT,
        87: Opcode.POP_BLOCK,
        88: Opcode.END_FINALLY,
        89: Opcode.BUILD_CLASS,

        90: Opcode.STORE_NAME_A,
        91: Opcode.DELETE_NAME_A,
        92: Opcode.UNPACK_SEQUENCE_A,

        95: Opcode.STORE_ATTR_A,
        96: Opcode.DELETE_ATTR_A,
        97: Opcode.STORE_GLOBAL_A,
        98: Opcode.DELETE_GLOBAL_A,
        99: Opcode.DUP_TOPX_A,

        100: Opcode.LOAD_CONST_A,
        101: Opcode.LOAD_NAME_A,
        102: Opcode.BUILD_TUPLE_A,
        103: Opcode.BUILD_LIST_A,
        104: Opcode.BUILD_MAP_A,
        105: Opcode.LOAD_ATTR_A,
        106: Opcode.COMPARE_OP_A,
        107: Opcode.IMPORT_NAME_A,
        108: Opcode.IMPORT_FROM_A,

        110: Opcode.JUMP_FORWARD_A,
        111: Opcode.JUMP_IF_FALSE_A,
        112: Opcode.JUMP_IF_TRUE_A,
        113: Opcode.JUMP_ABSOLUTE_A,
        114: Opcode.FOR_LOOP_A,

        116: Opcode.LOAD_GLOBAL_A,

        120: Opcode.SETUP_LOOP_A,
        121: Opcode.SETUP_EXCEPT_A,
        122: Opcode.SETUP_FINALLY_A,

        124: Opcode.LOAD_FAST_A,
        125: Opcode.STORE_FAST_A,
        126: Opcode.DELETE_FAST_A,
        127: Opcode.SET_LINENO_A,

        130: Opcode.RAISE_VARARGS_A,
        131: Opcode.CALL_FUNCTION_A,
        132: Opcode.MAKE_FUNCTION_A,
        133: Opcode.BUILD_SLICE_A,

        140: Opcode.CALL_FUNCTION_VAR_A,
        141: Opcode.CALL_FUNCTION_KW_A,
        142: Opcode.CALL_FUNCTION_VAR_KW_A,

        143: Opcode.EXTENDED_ARG_A,
    }

    return mapping.get(id_)

def python_2_1_map(id_: int) -> int:
    mapping = {
        0:  Opcode.STOP_CODE,
        1:  Opcode.POP_TOP,
        2:  Opcode.ROT_TWO,
        3:  Opcode.ROT_THREE,
        4:  Opcode.DUP_TOP,
        5:  Opcode.ROT_FOUR,

        10: Opcode.UNARY_POSITIVE,
        11: Opcode.UNARY_NEGATIVE,
        12: Opcode.UNARY_NOT,
        13: Opcode.UNARY_CONVERT,
        15: Opcode.UNARY_INVERT,

        19: Opcode.BINARY_POWER,
        20: Opcode.BINARY_MULTIPLY,
        21: Opcode.BINARY_DIVIDE,
        22: Opcode.BINARY_MODULO,
        23: Opcode.BINARY_ADD,
        24: Opcode.BINARY_SUBTRACT,
        25: Opcode.BINARY_SUBSCR,

        30: Opcode.SLICE_0,
        31: Opcode.SLICE_1,
        32: Opcode.SLICE_2,
        33: Opcode.SLICE_3,

        40: Opcode.STORE_SLICE_0,
        41: Opcode.STORE_SLICE_1,
        42: Opcode.STORE_SLICE_2,
        43: Opcode.STORE_SLICE_3,

        50: Opcode.DELETE_SLICE_0,
        51: Opcode.DELETE_SLICE_1,
        52: Opcode.DELETE_SLICE_2,
        53: Opcode.DELETE_SLICE_3,

        55: Opcode.INPLACE_ADD,
        56: Opcode.INPLACE_SUBTRACT,
        57: Opcode.INPLACE_MULTIPLY,
        58: Opcode.INPLACE_DIVIDE,
        59: Opcode.INPLACE_MODULO,

        60: Opcode.STORE_SUBSCR,
        61: Opcode.DELETE_SUBSCR,
        62: Opcode.BINARY_LSHIFT,
        63: Opcode.BINARY_RSHIFT,
        64: Opcode.BINARY_AND,
        65: Opcode.BINARY_XOR,
        66: Opcode.BINARY_OR,
        67: Opcode.INPLACE_POWER,

        70: Opcode.PRINT_EXPR,
        71: Opcode.PRINT_ITEM,
        72: Opcode.PRINT_NEWLINE,
        73: Opcode.PRINT_ITEM_TO,
        74: Opcode.PRINT_NEWLINE_TO,

        75: Opcode.INPLACE_LSHIFT,
        76: Opcode.INPLACE_RSHIFT,
        77: Opcode.INPLACE_AND,
        78: Opcode.INPLACE_XOR,
        79: Opcode.INPLACE_OR,

        80: Opcode.BREAK_LOOP,
        82: Opcode.LOAD_LOCALS,
        83: Opcode.RETURN_VALUE,
        84: Opcode.IMPORT_STAR,
        85: Opcode.EXEC_STMT,
        87: Opcode.POP_BLOCK,
        88: Opcode.END_FINALLY,
        89: Opcode.BUILD_CLASS,

        90: Opcode.STORE_NAME_A,
        91: Opcode.DELETE_NAME_A,
        92: Opcode.UNPACK_SEQUENCE_A,

        95: Opcode.STORE_ATTR_A,
        96: Opcode.DELETE_ATTR_A,
        97: Opcode.STORE_GLOBAL_A,
        98: Opcode.DELETE_GLOBAL_A,
        99: Opcode.DUP_TOPX_A,

        100: Opcode.LOAD_CONST_A,
        101: Opcode.LOAD_NAME_A,
        102: Opcode.BUILD_TUPLE_A,
        103: Opcode.BUILD_LIST_A,
        104: Opcode.BUILD_MAP_A,
        105: Opcode.LOAD_ATTR_A,
        106: Opcode.COMPARE_OP_A,
        107: Opcode.IMPORT_NAME_A,
        108: Opcode.IMPORT_FROM_A,

        110: Opcode.JUMP_FORWARD_A,
        111: Opcode.JUMP_IF_FALSE_A,
        112: Opcode.JUMP_IF_TRUE_A,
        113: Opcode.JUMP_ABSOLUTE_A,
        114: Opcode.FOR_LOOP_A,

        116: Opcode.LOAD_GLOBAL_A,
        119: Opcode.CONTINUE_LOOP_A,

        120: Opcode.SETUP_LOOP_A,
        121: Opcode.SETUP_EXCEPT_A,
        122: Opcode.SETUP_FINALLY_A,

        124: Opcode.LOAD_FAST_A,
        125: Opcode.STORE_FAST_A,
        126: Opcode.DELETE_FAST_A,
        127: Opcode.SET_LINENO_A,

        130: Opcode.RAISE_VARARGS_A,
        131: Opcode.CALL_FUNCTION_A,
        132: Opcode.MAKE_FUNCTION_A,
        133: Opcode.BUILD_SLICE_A,

        134: Opcode.MAKE_CLOSURE_A,
        135: Opcode.LOAD_CLOSURE_A,
        136: Opcode.LOAD_DEREF_A,
        137: Opcode.STORE_DEREF_A,

        140: Opcode.CALL_FUNCTION_VAR_A,
        141: Opcode.CALL_FUNCTION_KW_A,
        142: Opcode.CALL_FUNCTION_VAR_KW_A,

        143: Opcode.EXTENDED_ARG_A,
    }

    return mapping.get(id_)

def python_2_2_map(id_: int) -> int:
    mapping = {
        0:  Opcode.STOP_CODE,
        1:  Opcode.POP_TOP,
        2:  Opcode.ROT_TWO,
        3:  Opcode.ROT_THREE,
        4:  Opcode.DUP_TOP,
        5:  Opcode.ROT_FOUR,

        10: Opcode.UNARY_POSITIVE,
        11: Opcode.UNARY_NEGATIVE,
        12: Opcode.UNARY_NOT,
        13: Opcode.UNARY_CONVERT,
        15: Opcode.UNARY_INVERT,

        19: Opcode.BINARY_POWER,
        20: Opcode.BINARY_MULTIPLY,
        21: Opcode.BINARY_DIVIDE,
        22: Opcode.BINARY_MODULO,
        23: Opcode.BINARY_ADD,
        24: Opcode.BINARY_SUBTRACT,
        25: Opcode.BINARY_SUBSCR,
        26: Opcode.BINARY_FLOOR_DIVIDE,
        27: Opcode.BINARY_TRUE_DIVIDE,
        28: Opcode.INPLACE_FLOOR_DIVIDE,
        29: Opcode.INPLACE_TRUE_DIVIDE,

        30: Opcode.SLICE_0,
        31: Opcode.SLICE_1,
        32: Opcode.SLICE_2,
        33: Opcode.SLICE_3,

        40: Opcode.STORE_SLICE_0,
        41: Opcode.STORE_SLICE_1,
        42: Opcode.STORE_SLICE_2,
        43: Opcode.STORE_SLICE_3,

        50: Opcode.DELETE_SLICE_0,
        51: Opcode.DELETE_SLICE_1,
        52: Opcode.DELETE_SLICE_2,
        53: Opcode.DELETE_SLICE_3,

        55: Opcode.INPLACE_ADD,
        56: Opcode.INPLACE_SUBTRACT,
        57: Opcode.INPLACE_MULTIPLY,
        58: Opcode.INPLACE_DIVIDE,
        59: Opcode.INPLACE_MODULO,

        60: Opcode.STORE_SUBSCR,
        61: Opcode.DELETE_SUBSCR,
        62: Opcode.BINARY_LSHIFT,
        63: Opcode.BINARY_RSHIFT,
        64: Opcode.BINARY_AND,
        65: Opcode.BINARY_XOR,
        66: Opcode.BINARY_OR,
        67: Opcode.INPLACE_POWER,
        68: Opcode.GET_ITER,

        70: Opcode.PRINT_EXPR,
        71: Opcode.PRINT_ITEM,
        72: Opcode.PRINT_NEWLINE,
        73: Opcode.PRINT_ITEM_TO,
        74: Opcode.PRINT_NEWLINE_TO,

        75: Opcode.INPLACE_LSHIFT,
        76: Opcode.INPLACE_RSHIFT,
        77: Opcode.INPLACE_AND,
        78: Opcode.INPLACE_XOR,
        79: Opcode.INPLACE_OR,

        80: Opcode.BREAK_LOOP,
        82: Opcode.LOAD_LOCALS,
        83: Opcode.RETURN_VALUE,
        84: Opcode.IMPORT_STAR,
        85: Opcode.EXEC_STMT,
        86: Opcode.YIELD_VALUE,
        87: Opcode.POP_BLOCK,
        88: Opcode.END_FINALLY,
        89: Opcode.BUILD_CLASS,

        90: Opcode.STORE_NAME_A,
        91: Opcode.DELETE_NAME_A,
        92: Opcode.UNPACK_SEQUENCE_A,
        93: Opcode.FOR_ITER_A,

        95: Opcode.STORE_ATTR_A,
        96: Opcode.DELETE_ATTR_A,
        97: Opcode.STORE_GLOBAL_A,
        98: Opcode.DELETE_GLOBAL_A,
        99: Opcode.DUP_TOPX_A,

        100: Opcode.LOAD_CONST_A,
        101: Opcode.LOAD_NAME_A,
        102: Opcode.BUILD_TUPLE_A,
        103: Opcode.BUILD_LIST_A,
        104: Opcode.BUILD_MAP_A,
        105: Opcode.LOAD_ATTR_A,
        106: Opcode.COMPARE_OP_A,
        107: Opcode.IMPORT_NAME_A,
        108: Opcode.IMPORT_FROM_A,

        110: Opcode.JUMP_FORWARD_A,
        111: Opcode.JUMP_IF_FALSE_A,
        112: Opcode.JUMP_IF_TRUE_A,
        113: Opcode.JUMP_ABSOLUTE_A,
        114: Opcode.FOR_LOOP_A,

        116: Opcode.LOAD_GLOBAL_A,
        119: Opcode.CONTINUE_LOOP_A,

        120: Opcode.SETUP_LOOP_A,
        121: Opcode.SETUP_EXCEPT_A,
        122: Opcode.SETUP_FINALLY_A,

        124: Opcode.LOAD_FAST_A,
        125: Opcode.STORE_FAST_A,
        126: Opcode.DELETE_FAST_A,
        127: Opcode.SET_LINENO_A,

        130: Opcode.RAISE_VARARGS_A,
        131: Opcode.CALL_FUNCTION_A,
        132: Opcode.MAKE_FUNCTION_A,
        133: Opcode.BUILD_SLICE_A,

        134: Opcode.MAKE_CLOSURE_A,
        135: Opcode.LOAD_CLOSURE_A,
        136: Opcode.LOAD_DEREF_A,
        137: Opcode.STORE_DEREF_A,

        140: Opcode.CALL_FUNCTION_VAR_A,
        141: Opcode.CALL_FUNCTION_KW_A,
        142: Opcode.CALL_FUNCTION_VAR_KW_A,

        143: Opcode.EXTENDED_ARG_A,
    }

    return mapping.get(id_)

def python_2_3_map(id_: int) -> int:
    mapping = {
        0:  Opcode.STOP_CODE,
        1:  Opcode.POP_TOP,
        2:  Opcode.ROT_TWO,
        3:  Opcode.ROT_THREE,
        4:  Opcode.DUP_TOP,
        5:  Opcode.ROT_FOUR,

        10: Opcode.UNARY_POSITIVE,
        11: Opcode.UNARY_NEGATIVE,
        12: Opcode.UNARY_NOT,
        13: Opcode.UNARY_CONVERT,
        15: Opcode.UNARY_INVERT,

        19: Opcode.BINARY_POWER,
        20: Opcode.BINARY_MULTIPLY,
        21: Opcode.BINARY_DIVIDE,
        22: Opcode.BINARY_MODULO,
        23: Opcode.BINARY_ADD,
        24: Opcode.BINARY_SUBTRACT,
        25: Opcode.BINARY_SUBSCR,
        26: Opcode.BINARY_FLOOR_DIVIDE,
        27: Opcode.BINARY_TRUE_DIVIDE,
        28: Opcode.INPLACE_FLOOR_DIVIDE,
        29: Opcode.INPLACE_TRUE_DIVIDE,

        30: Opcode.SLICE_0,
        31: Opcode.SLICE_1,
        32: Opcode.SLICE_2,
        33: Opcode.SLICE_3,

        40: Opcode.STORE_SLICE_0,
        41: Opcode.STORE_SLICE_1,
        42: Opcode.STORE_SLICE_2,
        43: Opcode.STORE_SLICE_3,

        50: Opcode.DELETE_SLICE_0,
        51: Opcode.DELETE_SLICE_1,
        52: Opcode.DELETE_SLICE_2,
        53: Opcode.DELETE_SLICE_3,

        55: Opcode.INPLACE_ADD,
        56: Opcode.INPLACE_SUBTRACT,
        57: Opcode.INPLACE_MULTIPLY,
        58: Opcode.INPLACE_DIVIDE,
        59: Opcode.INPLACE_MODULO,

        60: Opcode.STORE_SUBSCR,
        61: Opcode.DELETE_SUBSCR,
        62: Opcode.BINARY_LSHIFT,
        63: Opcode.BINARY_RSHIFT,
        64: Opcode.BINARY_AND,
        65: Opcode.BINARY_XOR,
        66: Opcode.BINARY_OR,
        67: Opcode.INPLACE_POWER,
        68: Opcode.GET_ITER,

        70: Opcode.PRINT_EXPR,
        71: Opcode.PRINT_ITEM,
        72: Opcode.PRINT_NEWLINE,
        73: Opcode.PRINT_ITEM_TO,
        74: Opcode.PRINT_NEWLINE_TO,

        75: Opcode.INPLACE_LSHIFT,
        76: Opcode.INPLACE_RSHIFT,
        77: Opcode.INPLACE_AND,
        78: Opcode.INPLACE_XOR,
        79: Opcode.INPLACE_OR,

        80: Opcode.BREAK_LOOP,
        82: Opcode.LOAD_LOCALS,
        83: Opcode.RETURN_VALUE,
        84: Opcode.IMPORT_STAR,
        85: Opcode.EXEC_STMT,
        86: Opcode.YIELD_VALUE,
        87: Opcode.POP_BLOCK,
        88: Opcode.END_FINALLY,
        89: Opcode.BUILD_CLASS,

        90: Opcode.STORE_NAME_A,
        91: Opcode.DELETE_NAME_A,
        92: Opcode.UNPACK_SEQUENCE_A,
        93: Opcode.FOR_ITER_A,

        95: Opcode.STORE_ATTR_A,
        96: Opcode.DELETE_ATTR_A,
        97: Opcode.STORE_GLOBAL_A,
        98: Opcode.DELETE_GLOBAL_A,
        99: Opcode.DUP_TOPX_A,

        100: Opcode.LOAD_CONST_A,
        101: Opcode.LOAD_NAME_A,
        102: Opcode.BUILD_TUPLE_A,
        103: Opcode.BUILD_LIST_A,
        104: Opcode.BUILD_MAP_A,
        105: Opcode.LOAD_ATTR_A,
        106: Opcode.COMPARE_OP_A,
        107: Opcode.IMPORT_NAME_A,
        108: Opcode.IMPORT_FROM_A,

        110: Opcode.JUMP_FORWARD_A,
        111: Opcode.JUMP_IF_FALSE_A,
        112: Opcode.JUMP_IF_TRUE_A,
        113: Opcode.JUMP_ABSOLUTE_A,

        116: Opcode.LOAD_GLOBAL_A,
        119: Opcode.CONTINUE_LOOP_A,

        120: Opcode.SETUP_LOOP_A,
        121: Opcode.SETUP_EXCEPT_A,
        122: Opcode.SETUP_FINALLY_A,

        124: Opcode.LOAD_FAST_A,
        125: Opcode.STORE_FAST_A,
        126: Opcode.DELETE_FAST_A,

        130: Opcode.RAISE_VARARGS_A,
        131: Opcode.CALL_FUNCTION_A,
        132: Opcode.MAKE_FUNCTION_A,
        133: Opcode.BUILD_SLICE_A,

        134: Opcode.MAKE_CLOSURE_A,
        135: Opcode.LOAD_CLOSURE_A,
        136: Opcode.LOAD_DEREF_A,
        137: Opcode.STORE_DEREF_A,

        140: Opcode.CALL_FUNCTION_VAR_A,
        141: Opcode.CALL_FUNCTION_KW_A,
        142: Opcode.CALL_FUNCTION_VAR_KW_A,

        143: Opcode.EXTENDED_ARG_A,
    }

    return mapping.get(id_)

def python_2_4_map(id_: int) -> int:
    mapping = {
        0:  Opcode.STOP_CODE,
        1:  Opcode.POP_TOP,
        2:  Opcode.ROT_TWO,
        3:  Opcode.ROT_THREE,
        4:  Opcode.DUP_TOP,
        5:  Opcode.ROT_FOUR,
        9:  Opcode.NOP,

        10: Opcode.UNARY_POSITIVE,
        11: Opcode.UNARY_NEGATIVE,
        12: Opcode.UNARY_NOT,
        13: Opcode.UNARY_CONVERT,
        15: Opcode.UNARY_INVERT,

        18: Opcode.LIST_APPEND,
        19: Opcode.BINARY_POWER,
        20: Opcode.BINARY_MULTIPLY,
        21: Opcode.BINARY_DIVIDE,
        22: Opcode.BINARY_MODULO,
        23: Opcode.BINARY_ADD,
        24: Opcode.BINARY_SUBTRACT,
        25: Opcode.BINARY_SUBSCR,
        26: Opcode.BINARY_FLOOR_DIVIDE,
        27: Opcode.BINARY_TRUE_DIVIDE,
        28: Opcode.INPLACE_FLOOR_DIVIDE,
        29: Opcode.INPLACE_TRUE_DIVIDE,

        30: Opcode.SLICE_0,
        31: Opcode.SLICE_1,
        32: Opcode.SLICE_2,
        33: Opcode.SLICE_3,

        40: Opcode.STORE_SLICE_0,
        41: Opcode.STORE_SLICE_1,
        42: Opcode.STORE_SLICE_2,
        43: Opcode.STORE_SLICE_3,

        50: Opcode.DELETE_SLICE_0,
        51: Opcode.DELETE_SLICE_1,
        52: Opcode.DELETE_SLICE_2,
        53: Opcode.DELETE_SLICE_3,

        55: Opcode.INPLACE_ADD,
        56: Opcode.INPLACE_SUBTRACT,
        57: Opcode.INPLACE_MULTIPLY,
        58: Opcode.INPLACE_DIVIDE,
        59: Opcode.INPLACE_MODULO,

        60: Opcode.STORE_SUBSCR,
        61: Opcode.DELETE_SUBSCR,
        62: Opcode.BINARY_LSHIFT,
        63: Opcode.BINARY_RSHIFT,
        64: Opcode.BINARY_AND,
        65: Opcode.BINARY_XOR,
        66: Opcode.BINARY_OR,
        67: Opcode.INPLACE_POWER,
        68: Opcode.GET_ITER,

        70: Opcode.PRINT_EXPR,
        71: Opcode.PRINT_ITEM,
        72: Opcode.PRINT_NEWLINE,
        73: Opcode.PRINT_ITEM_TO,
        74: Opcode.PRINT_NEWLINE_TO,

        75: Opcode.INPLACE_LSHIFT,
        76: Opcode.INPLACE_RSHIFT,
        77: Opcode.INPLACE_AND,
        78: Opcode.INPLACE_XOR,
        79: Opcode.INPLACE_OR,

        80: Opcode.BREAK_LOOP,
        82: Opcode.LOAD_LOCALS,
        83: Opcode.RETURN_VALUE,
        84: Opcode.IMPORT_STAR,
        85: Opcode.EXEC_STMT,
        86: Opcode.YIELD_VALUE,
        87: Opcode.POP_BLOCK,
        88: Opcode.END_FINALLY,
        89: Opcode.BUILD_CLASS,

        90: Opcode.STORE_NAME_A,
        91: Opcode.DELETE_NAME_A,
        92: Opcode.UNPACK_SEQUENCE_A,
        93: Opcode.FOR_ITER_A,

        95: Opcode.STORE_ATTR_A,
        96: Opcode.DELETE_ATTR_A,
        97: Opcode.STORE_GLOBAL_A,
        98: Opcode.DELETE_GLOBAL_A,
        99: Opcode.DUP_TOPX_A,

        100: Opcode.LOAD_CONST_A,
        101: Opcode.LOAD_NAME_A,
        102: Opcode.BUILD_TUPLE_A,
        103: Opcode.BUILD_LIST_A,
        104: Opcode.BUILD_MAP_A,
        105: Opcode.LOAD_ATTR_A,
        106: Opcode.COMPARE_OP_A,
        107: Opcode.IMPORT_NAME_A,
        108: Opcode.IMPORT_FROM_A,

        110: Opcode.JUMP_FORWARD_A,
        111: Opcode.JUMP_IF_FALSE_A,
        112: Opcode.JUMP_IF_TRUE_A,
        113: Opcode.JUMP_ABSOLUTE_A,

        116: Opcode.LOAD_GLOBAL_A,
        119: Opcode.CONTINUE_LOOP_A,

        120: Opcode.SETUP_LOOP_A,
        121: Opcode.SETUP_EXCEPT_A,
        122: Opcode.SETUP_FINALLY_A,

        124: Opcode.LOAD_FAST_A,
        125: Opcode.STORE_FAST_A,
        126: Opcode.DELETE_FAST_A,

        130: Opcode.RAISE_VARARGS_A,
        131: Opcode.CALL_FUNCTION_A,
        132: Opcode.MAKE_FUNCTION_A,
        133: Opcode.BUILD_SLICE_A,

        134: Opcode.MAKE_CLOSURE_A,
        135: Opcode.LOAD_CLOSURE_A,
        136: Opcode.LOAD_DEREF_A,
        137: Opcode.STORE_DEREF_A,

        140: Opcode.CALL_FUNCTION_VAR_A,
        141: Opcode.CALL_FUNCTION_KW_A,
        142: Opcode.CALL_FUNCTION_VAR_KW_A,

        143: Opcode.EXTENDED_ARG_A,
    }

    return mapping.get(id_)

def python_2_5_map(id_: int) -> int:
    mapping = {
        0:  Opcode.STOP_CODE,
        1:  Opcode.POP_TOP,
        2:  Opcode.ROT_TWO,
        3:  Opcode.ROT_THREE,
        4:  Opcode.DUP_TOP,
        5:  Opcode.ROT_FOUR,
        9:  Opcode.NOP,

        10: Opcode.UNARY_POSITIVE,
        11: Opcode.UNARY_NEGATIVE,
        12: Opcode.UNARY_NOT,
        13: Opcode.UNARY_CONVERT,
        15: Opcode.UNARY_INVERT,

        18: Opcode.LIST_APPEND,
        19: Opcode.BINARY_POWER,
        20: Opcode.BINARY_MULTIPLY,
        21: Opcode.BINARY_DIVIDE,
        22: Opcode.BINARY_MODULO,
        23: Opcode.BINARY_ADD,
        24: Opcode.BINARY_SUBTRACT,
        25: Opcode.BINARY_SUBSCR,
        26: Opcode.BINARY_FLOOR_DIVIDE,
        27: Opcode.BINARY_TRUE_DIVIDE,
        28: Opcode.INPLACE_FLOOR_DIVIDE,
        29: Opcode.INPLACE_TRUE_DIVIDE,

        30: Opcode.SLICE_0,
        31: Opcode.SLICE_1,
        32: Opcode.SLICE_2,
        33: Opcode.SLICE_3,

        40: Opcode.STORE_SLICE_0,
        41: Opcode.STORE_SLICE_1,
        42: Opcode.STORE_SLICE_2,
        43: Opcode.STORE_SLICE_3,

        50: Opcode.DELETE_SLICE_0,
        51: Opcode.DELETE_SLICE_1,
        52: Opcode.DELETE_SLICE_2,
        53: Opcode.DELETE_SLICE_3,

        55: Opcode.INPLACE_ADD,
        56: Opcode.INPLACE_SUBTRACT,
        57: Opcode.INPLACE_MULTIPLY,
        58: Opcode.INPLACE_DIVIDE,
        59: Opcode.INPLACE_MODULO,

        60: Opcode.STORE_SUBSCR,
        61: Opcode.DELETE_SUBSCR,
        62: Opcode.BINARY_LSHIFT,
        63: Opcode.BINARY_RSHIFT,
        64: Opcode.BINARY_AND,
        65: Opcode.BINARY_XOR,
        66: Opcode.BINARY_OR,
        67: Opcode.INPLACE_POWER,
        68: Opcode.GET_ITER,

        70: Opcode.PRINT_EXPR,
        71: Opcode.PRINT_ITEM,
        72: Opcode.PRINT_NEWLINE,
        73: Opcode.PRINT_ITEM_TO,
        74: Opcode.PRINT_NEWLINE_TO,

        75: Opcode.INPLACE_LSHIFT,
        76: Opcode.INPLACE_RSHIFT,
        77: Opcode.INPLACE_AND,
        78: Opcode.INPLACE_XOR,
        79: Opcode.INPLACE_OR,

        80: Opcode.BREAK_LOOP,
        81: Opcode.WITH_CLEANUP,
        82: Opcode.LOAD_LOCALS,
        83: Opcode.RETURN_VALUE,
        84: Opcode.IMPORT_STAR,
        85: Opcode.EXEC_STMT,
        86: Opcode.YIELD_VALUE,
        87: Opcode.POP_BLOCK,
        88: Opcode.END_FINALLY,
        89: Opcode.BUILD_CLASS,

        90: Opcode.STORE_NAME_A,
        91: Opcode.DELETE_NAME_A,
        92: Opcode.UNPACK_SEQUENCE_A,
        93: Opcode.FOR_ITER_A,

        95: Opcode.STORE_ATTR_A,
        96: Opcode.DELETE_ATTR_A,
        97: Opcode.STORE_GLOBAL_A,
        98: Opcode.DELETE_GLOBAL_A,
        99: Opcode.DUP_TOPX_A,

        100: Opcode.LOAD_CONST_A,
        101: Opcode.LOAD_NAME_A,
        102: Opcode.BUILD_TUPLE_A,
        103: Opcode.BUILD_LIST_A,
        104: Opcode.BUILD_MAP_A,
        105: Opcode.LOAD_ATTR_A,
        106: Opcode.COMPARE_OP_A,
        107: Opcode.IMPORT_NAME_A,
        108: Opcode.IMPORT_FROM_A,

        110: Opcode.JUMP_FORWARD_A,
        111: Opcode.JUMP_IF_FALSE_A,
        112: Opcode.JUMP_IF_TRUE_A,
        113: Opcode.JUMP_ABSOLUTE_A,

        116: Opcode.LOAD_GLOBAL_A,
        119: Opcode.CONTINUE_LOOP_A,

        120: Opcode.SETUP_LOOP_A,
        121: Opcode.SETUP_EXCEPT_A,
        122: Opcode.SETUP_FINALLY_A,

        124: Opcode.LOAD_FAST_A,
        125: Opcode.STORE_FAST_A,
        126: Opcode.DELETE_FAST_A,

        130: Opcode.RAISE_VARARGS_A,
        131: Opcode.CALL_FUNCTION_A,
        132: Opcode.MAKE_FUNCTION_A,
        133: Opcode.BUILD_SLICE_A,

        134: Opcode.MAKE_CLOSURE_A,
        135: Opcode.LOAD_CLOSURE_A,
        136: Opcode.LOAD_DEREF_A,
        137: Opcode.STORE_DEREF_A,

        140: Opcode.CALL_FUNCTION_VAR_A,
        141: Opcode.CALL_FUNCTION_KW_A,
        142: Opcode.CALL_FUNCTION_VAR_KW_A,

        143: Opcode.EXTENDED_ARG_A,
    }

    return mapping.get(id_)

def python_2_6_map(id_: int) -> int:
    mapping = {
        0:  Opcode.STOP_CODE,
        1:  Opcode.POP_TOP,
        2:  Opcode.ROT_TWO,
        3:  Opcode.ROT_THREE,
        4:  Opcode.DUP_TOP,
        5:  Opcode.ROT_FOUR,
        9:  Opcode.NOP,

        10: Opcode.UNARY_POSITIVE,
        11: Opcode.UNARY_NEGATIVE,
        12: Opcode.UNARY_NOT,
        13: Opcode.UNARY_CONVERT,
        15: Opcode.UNARY_INVERT,

        18: Opcode.LIST_APPEND,
        19: Opcode.BINARY_POWER,
        20: Opcode.BINARY_MULTIPLY,
        21: Opcode.BINARY_DIVIDE,
        22: Opcode.BINARY_MODULO,
        23: Opcode.BINARY_ADD,
        24: Opcode.BINARY_SUBTRACT,
        25: Opcode.BINARY_SUBSCR,
        26: Opcode.BINARY_FLOOR_DIVIDE,
        27: Opcode.BINARY_TRUE_DIVIDE,
        28: Opcode.INPLACE_FLOOR_DIVIDE,
        29: Opcode.INPLACE_TRUE_DIVIDE,

        30: Opcode.SLICE_0,
        31: Opcode.SLICE_1,
        32: Opcode.SLICE_2,
        33: Opcode.SLICE_3,

        40: Opcode.STORE_SLICE_0,
        41: Opcode.STORE_SLICE_1,
        42: Opcode.STORE_SLICE_2,
        43: Opcode.STORE_SLICE_3,

        50: Opcode.DELETE_SLICE_0,
        51: Opcode.DELETE_SLICE_1,
        52: Opcode.DELETE_SLICE_2,
        53: Opcode.DELETE_SLICE_3,
        54: Opcode.STORE_MAP,

        55: Opcode.INPLACE_ADD,
        56: Opcode.INPLACE_SUBTRACT,
        57: Opcode.INPLACE_MULTIPLY,
        58: Opcode.INPLACE_DIVIDE,
        59: Opcode.INPLACE_MODULO,

        60: Opcode.STORE_SUBSCR,
        61: Opcode.DELETE_SUBSCR,
        62: Opcode.BINARY_LSHIFT,
        63: Opcode.BINARY_RSHIFT,
        64: Opcode.BINARY_AND,
        65: Opcode.BINARY_XOR,
        66: Opcode.BINARY_OR,
        67: Opcode.INPLACE_POWER,
        68: Opcode.GET_ITER,

        70: Opcode.PRINT_EXPR,
        71: Opcode.PRINT_ITEM,
        72: Opcode.PRINT_NEWLINE,
        73: Opcode.PRINT_ITEM_TO,
        74: Opcode.PRINT_NEWLINE_TO,

        75: Opcode.INPLACE_LSHIFT,
        76: Opcode.INPLACE_RSHIFT,
        77: Opcode.INPLACE_AND,
        78: Opcode.INPLACE_XOR,
        79: Opcode.INPLACE_OR,

        80: Opcode.BREAK_LOOP,
        81: Opcode.WITH_CLEANUP,
        82: Opcode.LOAD_LOCALS,
        83: Opcode.RETURN_VALUE,
        84: Opcode.IMPORT_STAR,
        85: Opcode.EXEC_STMT,
        86: Opcode.YIELD_VALUE,
        87: Opcode.POP_BLOCK,
        88: Opcode.END_FINALLY,
        89: Opcode.BUILD_CLASS,

        90: Opcode.STORE_NAME_A,
        91: Opcode.DELETE_NAME_A,
        92: Opcode.UNPACK_SEQUENCE_A,
        93: Opcode.FOR_ITER_A,

        95: Opcode.STORE_ATTR_A,
        96: Opcode.DELETE_ATTR_A,
        97: Opcode.STORE_GLOBAL_A,
        98: Opcode.DELETE_GLOBAL_A,
        99: Opcode.DUP_TOPX_A,

        100: Opcode.LOAD_CONST_A,
        101: Opcode.LOAD_NAME_A,
        102: Opcode.BUILD_TUPLE_A,
        103: Opcode.BUILD_LIST_A,
        104: Opcode.BUILD_MAP_A,
        105: Opcode.LOAD_ATTR_A,
        106: Opcode.COMPARE_OP_A,
        107: Opcode.IMPORT_NAME_A,
        108: Opcode.IMPORT_FROM_A,

        110: Opcode.JUMP_FORWARD_A,
        111: Opcode.JUMP_IF_FALSE_A,
        112: Opcode.JUMP_IF_TRUE_A,
        113: Opcode.JUMP_ABSOLUTE_A,

        116: Opcode.LOAD_GLOBAL_A,
        119: Opcode.CONTINUE_LOOP_A,

        120: Opcode.SETUP_LOOP_A,
        121: Opcode.SETUP_EXCEPT_A,
        122: Opcode.SETUP_FINALLY_A,

        124: Opcode.LOAD_FAST_A,
        125: Opcode.STORE_FAST_A,
        126: Opcode.DELETE_FAST_A,

        130: Opcode.RAISE_VARARGS_A,
        131: Opcode.CALL_FUNCTION_A,
        132: Opcode.MAKE_FUNCTION_A,
        133: Opcode.BUILD_SLICE_A,

        134: Opcode.MAKE_CLOSURE_A,
        135: Opcode.LOAD_CLOSURE_A,
        136: Opcode.LOAD_DEREF_A,
        137: Opcode.STORE_DEREF_A,

        140: Opcode.CALL_FUNCTION_VAR_A,
        141: Opcode.CALL_FUNCTION_KW_A,
        142: Opcode.CALL_FUNCTION_VAR_KW_A,

        143: Opcode.EXTENDED_ARG_A,
    }

    return mapping.get(id_)

def python_2_7_map(id_: int) -> int:
    mapping = {
        0:  Opcode.STOP_CODE,
        1:  Opcode.POP_TOP,
        2:  Opcode.ROT_TWO,
        3:  Opcode.ROT_THREE,
        4:  Opcode.DUP_TOP,
        5:  Opcode.ROT_FOUR,
        9:  Opcode.NOP,

        10: Opcode.UNARY_POSITIVE,
        11: Opcode.UNARY_NEGATIVE,
        12: Opcode.UNARY_NOT,
        13: Opcode.UNARY_CONVERT,
        15: Opcode.UNARY_INVERT,

        19: Opcode.BINARY_POWER,
        20: Opcode.BINARY_MULTIPLY,
        21: Opcode.BINARY_DIVIDE,
        22: Opcode.BINARY_MODULO,
        23: Opcode.BINARY_ADD,
        24: Opcode.BINARY_SUBTRACT,
        25: Opcode.BINARY_SUBSCR,
        26: Opcode.BINARY_FLOOR_DIVIDE,
        27: Opcode.BINARY_TRUE_DIVIDE,
        28: Opcode.INPLACE_FLOOR_DIVIDE,
        29: Opcode.INPLACE_TRUE_DIVIDE,

        30: Opcode.SLICE_0,
        31: Opcode.SLICE_1,
        32: Opcode.SLICE_2,
        33: Opcode.SLICE_3,

        40: Opcode.STORE_SLICE_0,
        41: Opcode.STORE_SLICE_1,
        42: Opcode.STORE_SLICE_2,
        43: Opcode.STORE_SLICE_3,

        50: Opcode.DELETE_SLICE_0,
        51: Opcode.DELETE_SLICE_1,
        52: Opcode.DELETE_SLICE_2,
        53: Opcode.DELETE_SLICE_3,
        54: Opcode.STORE_MAP,

        55: Opcode.INPLACE_ADD,
        56: Opcode.INPLACE_SUBTRACT,
        57: Opcode.INPLACE_MULTIPLY,
        58: Opcode.INPLACE_DIVIDE,
        59: Opcode.INPLACE_MODULO,

        60: Opcode.STORE_SUBSCR,
        61: Opcode.DELETE_SUBSCR,
        62: Opcode.BINARY_LSHIFT,
        63: Opcode.BINARY_RSHIFT,
        64: Opcode.BINARY_AND,
        65: Opcode.BINARY_XOR,
        66: Opcode.BINARY_OR,
        67: Opcode.INPLACE_POWER,
        68: Opcode.GET_ITER,

        70: Opcode.PRINT_EXPR,
        71: Opcode.PRINT_ITEM,
        72: Opcode.PRINT_NEWLINE,
        73: Opcode.PRINT_ITEM_TO,
        74: Opcode.PRINT_NEWLINE_TO,

        75: Opcode.INPLACE_LSHIFT,
        76: Opcode.INPLACE_RSHIFT,
        77: Opcode.INPLACE_AND,
        78: Opcode.INPLACE_XOR,
        79: Opcode.INPLACE_OR,

        80: Opcode.BREAK_LOOP,
        81: Opcode.WITH_CLEANUP,
        82: Opcode.LOAD_LOCALS,
        83: Opcode.RETURN_VALUE,
        84: Opcode.IMPORT_STAR,
        85: Opcode.EXEC_STMT,
        86: Opcode.YIELD_VALUE,
        87: Opcode.POP_BLOCK,
        88: Opcode.END_FINALLY,
        89: Opcode.BUILD_CLASS,

        90: Opcode.STORE_NAME_A,
        91: Opcode.DELETE_NAME_A,
        92: Opcode.UNPACK_SEQUENCE_A,
        93: Opcode.FOR_ITER_A,
        94: Opcode.LIST_APPEND_A,

        95: Opcode.STORE_ATTR_A,
        96: Opcode.DELETE_ATTR_A,
        97: Opcode.STORE_GLOBAL_A,
        98: Opcode.DELETE_GLOBAL_A,
        99: Opcode.DUP_TOPX_A,

        100: Opcode.LOAD_CONST_A,
        101: Opcode.LOAD_NAME_A,
        102: Opcode.BUILD_TUPLE_A,
        103: Opcode.BUILD_LIST_A,
        104: Opcode.BUILD_SET_A,
        105: Opcode.BUILD_MAP_A,
        106: Opcode.LOAD_ATTR_A,
        107: Opcode.COMPARE_OP_A,
        108: Opcode.IMPORT_NAME_A,
        109: Opcode.IMPORT_FROM_A,

        110: Opcode.JUMP_FORWARD_A,
        111: Opcode.JUMP_IF_FALSE_OR_POP_A,
        112: Opcode.JUMP_IF_TRUE_OR_POP_A,
        113: Opcode.JUMP_ABSOLUTE_A,
        114: Opcode.POP_JUMP_IF_FALSE_A,
        115: Opcode.POP_JUMP_IF_TRUE_A,

        116: Opcode.LOAD_GLOBAL_A,
        119: Opcode.CONTINUE_LOOP_A,

        120: Opcode.SETUP_LOOP_A,
        121: Opcode.SETUP_EXCEPT_A,
        122: Opcode.SETUP_FINALLY_A,

        124: Opcode.LOAD_FAST_A,
        125: Opcode.STORE_FAST_A,
        126: Opcode.DELETE_FAST_A,

        130: Opcode.RAISE_VARARGS_A,
        131: Opcode.CALL_FUNCTION_A,
        132: Opcode.MAKE_FUNCTION_A,
        133: Opcode.BUILD_SLICE_A,

        134: Opcode.MAKE_CLOSURE_A,
        135: Opcode.LOAD_CLOSURE_A,
        136: Opcode.LOAD_DEREF_A,
        137: Opcode.STORE_DEREF_A,

        140: Opcode.CALL_FUNCTION_VAR_A,
        141: Opcode.CALL_FUNCTION_KW_A,
        142: Opcode.CALL_FUNCTION_VAR_KW_A,

        143: Opcode.SETUP_WITH_A,
        145: Opcode.EXTENDED_ARG_A,
        146: Opcode.SET_ADD_A,
        147: Opcode.MAP_ADD_A,
    }

    return mapping.get(id_)

def python_3_0_map(id_: int) -> int:
    mapping = {
        0:  Opcode.STOP_CODE,
        1:  Opcode.POP_TOP,
        2:  Opcode.ROT_TWO,
        3:  Opcode.ROT_THREE,
        4:  Opcode.DUP_TOP,
        5:  Opcode.ROT_FOUR,
        9:  Opcode.NOP,

        10: Opcode.UNARY_POSITIVE,
        11: Opcode.UNARY_NEGATIVE,
        12: Opcode.UNARY_NOT,
        15: Opcode.UNARY_INVERT,

        17: Opcode.SET_ADD,
        18: Opcode.LIST_APPEND,
        19: Opcode.BINARY_POWER,
        20: Opcode.BINARY_MULTIPLY,
        22: Opcode.BINARY_MODULO,
        23: Opcode.BINARY_ADD,
        24: Opcode.BINARY_SUBTRACT,
        25: Opcode.BINARY_SUBSCR,
        26: Opcode.BINARY_FLOOR_DIVIDE,
        27: Opcode.BINARY_TRUE_DIVIDE,
        28: Opcode.INPLACE_FLOOR_DIVIDE,
        29: Opcode.INPLACE_TRUE_DIVIDE,

        54: Opcode.STORE_MAP,
        55: Opcode.INPLACE_ADD,
        56: Opcode.INPLACE_SUBTRACT,
        57: Opcode.INPLACE_MULTIPLY,
        59: Opcode.INPLACE_MODULO,

        60: Opcode.STORE_SUBSCR,
        61: Opcode.DELETE_SUBSCR,
        62: Opcode.BINARY_LSHIFT,
        63: Opcode.BINARY_RSHIFT,
        64: Opcode.BINARY_AND,
        65: Opcode.BINARY_XOR,
        66: Opcode.BINARY_OR,
        67: Opcode.INPLACE_POWER,
        68: Opcode.GET_ITER,
        69: Opcode.STORE_LOCALS,

        70: Opcode.PRINT_EXPR,
        71: Opcode.LOAD_BUILD_CLASS,

        75: Opcode.INPLACE_LSHIFT,
        76: Opcode.INPLACE_RSHIFT,
        77: Opcode.INPLACE_AND,
        78: Opcode.INPLACE_XOR,
        79: Opcode.INPLACE_OR,

        80: Opcode.BREAK_LOOP,
        81: Opcode.WITH_CLEANUP,
        83: Opcode.RETURN_VALUE,
        84: Opcode.IMPORT_STAR,
        86: Opcode.YIELD_VALUE,
        87: Opcode.POP_BLOCK,
        88: Opcode.END_FINALLY,
        89: Opcode.POP_EXCEPT,

        90: Opcode.STORE_NAME_A,
        91: Opcode.DELETE_NAME_A,
        92: Opcode.UNPACK_SEQUENCE_A,
        93: Opcode.FOR_ITER_A,
        94: Opcode.UNPACK_EX_A,
        95: Opcode.STORE_ATTR_A,
        96: Opcode.DELETE_ATTR_A,
        97: Opcode.STORE_GLOBAL_A,
        98: Opcode.DELETE_GLOBAL_A,
        99: Opcode.DUP_TOPX_A,

        100: Opcode.LOAD_CONST_A,
        101: Opcode.LOAD_NAME_A,
        102: Opcode.BUILD_TUPLE_A,
        103: Opcode.BUILD_LIST_A,
        104: Opcode.BUILD_SET_A,
        105: Opcode.BUILD_MAP_A,
        106: Opcode.LOAD_ATTR_A,
        107: Opcode.COMPARE_OP_A,
        108: Opcode.IMPORT_NAME_A,
        109: Opcode.IMPORT_FROM_A,

        110: Opcode.JUMP_FORWARD_A,
        111: Opcode.JUMP_IF_FALSE_A,
        112: Opcode.JUMP_IF_TRUE_A,
        113: Opcode.JUMP_ABSOLUTE_A,

        116: Opcode.LOAD_GLOBAL_A,
        119: Opcode.CONTINUE_LOOP_A,

        120: Opcode.SETUP_LOOP_A,
        121: Opcode.SETUP_EXCEPT_A,
        122: Opcode.SETUP_FINALLY_A,

        124: Opcode.LOAD_FAST_A,
        125: Opcode.STORE_FAST_A,
        126: Opcode.DELETE_FAST_A,

        130: Opcode.RAISE_VARARGS_A,
        131: Opcode.CALL_FUNCTION_A,
        132: Opcode.MAKE_FUNCTION_A,
        133: Opcode.BUILD_SLICE_A,
        134: Opcode.MAKE_CLOSURE_A,
        135: Opcode.LOAD_CLOSURE_A,
        136: Opcode.LOAD_DEREF_A,
        137: Opcode.STORE_DEREF_A,

        140: Opcode.CALL_FUNCTION_VAR_A,
        141: Opcode.CALL_FUNCTION_KW_A,
        142: Opcode.CALL_FUNCTION_VAR_KW_A,
        143: Opcode.EXTENDED_ARG_A,
    }

    return mapping.get(id_)

def python_3_1_map(id_: int) -> int:
    mapping = {
        0:  Opcode.STOP_CODE,
        1:  Opcode.POP_TOP,
        2:  Opcode.ROT_TWO,
        3:  Opcode.ROT_THREE,
        4:  Opcode.DUP_TOP,
        5:  Opcode.ROT_FOUR,
        9:  Opcode.NOP,

        10: Opcode.UNARY_POSITIVE,
        11: Opcode.UNARY_NEGATIVE,
        12: Opcode.UNARY_NOT,
        15: Opcode.UNARY_INVERT,

        19: Opcode.BINARY_POWER,
        20: Opcode.BINARY_MULTIPLY,
        22: Opcode.BINARY_MODULO,
        23: Opcode.BINARY_ADD,
        24: Opcode.BINARY_SUBTRACT,
        25: Opcode.BINARY_SUBSCR,
        26: Opcode.BINARY_FLOOR_DIVIDE,
        27: Opcode.BINARY_TRUE_DIVIDE,
        28: Opcode.INPLACE_FLOOR_DIVIDE,
        29: Opcode.INPLACE_TRUE_DIVIDE,

        54: Opcode.STORE_MAP,
        55: Opcode.INPLACE_ADD,
        56: Opcode.INPLACE_SUBTRACT,
        57: Opcode.INPLACE_MULTIPLY,
        59: Opcode.INPLACE_MODULO,

        60: Opcode.STORE_SUBSCR,
        61: Opcode.DELETE_SUBSCR,
        62: Opcode.BINARY_LSHIFT,
        63: Opcode.BINARY_RSHIFT,
        64: Opcode.BINARY_AND,
        65: Opcode.BINARY_XOR,
        66: Opcode.BINARY_OR,
        67: Opcode.INPLACE_POWER,
        68: Opcode.GET_ITER,
        69: Opcode.STORE_LOCALS,

        70: Opcode.PRINT_EXPR,
        71: Opcode.LOAD_BUILD_CLASS,

        75: Opcode.INPLACE_LSHIFT,
        76: Opcode.INPLACE_RSHIFT,
        77: Opcode.INPLACE_AND,
        78: Opcode.INPLACE_XOR,
        79: Opcode.INPLACE_OR,

        80: Opcode.BREAK_LOOP,
        81: Opcode.WITH_CLEANUP,
        83: Opcode.RETURN_VALUE,
        84: Opcode.IMPORT_STAR,
        86: Opcode.YIELD_VALUE,
        87: Opcode.POP_BLOCK,
        88: Opcode.END_FINALLY,
        89: Opcode.POP_EXCEPT,

        90: Opcode.STORE_NAME_A,
        91: Opcode.DELETE_NAME_A,
        92: Opcode.UNPACK_SEQUENCE_A,
        93: Opcode.FOR_ITER_A,
        94: Opcode.UNPACK_EX_A,
        95: Opcode.STORE_ATTR_A,
        96: Opcode.DELETE_ATTR_A,
        97: Opcode.STORE_GLOBAL_A,
        98: Opcode.DELETE_GLOBAL_A,
        99: Opcode.DUP_TOPX_A,

        100: Opcode.LOAD_CONST_A,
        101: Opcode.LOAD_NAME_A,
        102: Opcode.BUILD_TUPLE_A,
        103: Opcode.BUILD_LIST_A,
        104: Opcode.BUILD_SET_A,
        105: Opcode.BUILD_MAP_A,
        106: Opcode.LOAD_ATTR_A,
        107: Opcode.COMPARE_OP_A,
        108: Opcode.IMPORT_NAME_A,
        109: Opcode.IMPORT_FROM_A,

        110: Opcode.JUMP_FORWARD_A,
        111: Opcode.JUMP_IF_FALSE_OR_POP_A,
        112: Opcode.JUMP_IF_TRUE_OR_POP_A,
        113: Opcode.JUMP_ABSOLUTE_A,
        114: Opcode.POP_JUMP_IF_FALSE_A,
        115: Opcode.POP_JUMP_IF_TRUE_A,

        116: Opcode.LOAD_GLOBAL_A,
        119: Opcode.CONTINUE_LOOP_A,

        120: Opcode.SETUP_LOOP_A,
        121: Opcode.SETUP_EXCEPT_A,
        122: Opcode.SETUP_FINALLY_A,

        124: Opcode.LOAD_FAST_A,
        125: Opcode.STORE_FAST_A,
        126: Opcode.DELETE_FAST_A,

        130: Opcode.RAISE_VARARGS_A,
        131: Opcode.CALL_FUNCTION_A,
        132: Opcode.MAKE_FUNCTION_A,
        133: Opcode.BUILD_SLICE_A,
        134: Opcode.MAKE_CLOSURE_A,
        135: Opcode.LOAD_CLOSURE_A,
        136: Opcode.LOAD_DEREF_A,
        137: Opcode.STORE_DEREF_A,

        140: Opcode.CALL_FUNCTION_VAR_A,
        141: Opcode.CALL_FUNCTION_KW_A,
        142: Opcode.CALL_FUNCTION_VAR_KW_A,
        143: Opcode.EXTENDED_ARG_A,

        145: Opcode.LIST_APPEND_A,
        146: Opcode.SET_ADD_A,
        147: Opcode.MAP_ADD_A,
    }

    return mapping.get(id_)

def python_3_2_map(id_: int) -> int:
    mapping = {
        0:  Opcode.STOP_CODE,
        1:  Opcode.POP_TOP,
        2:  Opcode.ROT_TWO,
        3:  Opcode.ROT_THREE,
        4:  Opcode.DUP_TOP,
        5:  Opcode.DUP_TOP_TWO,
        9:  Opcode.NOP,

        10: Opcode.UNARY_POSITIVE,
        11: Opcode.UNARY_NEGATIVE,
        12: Opcode.UNARY_NOT,
        15: Opcode.UNARY_INVERT,

        19: Opcode.BINARY_POWER,
        20: Opcode.BINARY_MULTIPLY,
        22: Opcode.BINARY_MODULO,
        23: Opcode.BINARY_ADD,
        24: Opcode.BINARY_SUBTRACT,
        25: Opcode.BINARY_SUBSCR,
        26: Opcode.BINARY_FLOOR_DIVIDE,
        27: Opcode.BINARY_TRUE_DIVIDE,
        28: Opcode.INPLACE_FLOOR_DIVIDE,
        29: Opcode.INPLACE_TRUE_DIVIDE,

        54: Opcode.STORE_MAP,
        55: Opcode.INPLACE_ADD,
        56: Opcode.INPLACE_SUBTRACT,
        57: Opcode.INPLACE_MULTIPLY,
        59: Opcode.INPLACE_MODULO,

        60: Opcode.STORE_SUBSCR,
        61: Opcode.DELETE_SUBSCR,
        62: Opcode.BINARY_LSHIFT,
        63: Opcode.BINARY_RSHIFT,
        64: Opcode.BINARY_AND,
        65: Opcode.BINARY_XOR,
        66: Opcode.BINARY_OR,
        67: Opcode.INPLACE_POWER,
        68: Opcode.GET_ITER,
        69: Opcode.STORE_LOCALS,

        70: Opcode.PRINT_EXPR,
        71: Opcode.LOAD_BUILD_CLASS,

        75: Opcode.INPLACE_LSHIFT,
        76: Opcode.INPLACE_RSHIFT,
        77: Opcode.INPLACE_AND,
        78: Opcode.INPLACE_XOR,
        79: Opcode.INPLACE_OR,

        80: Opcode.BREAK_LOOP,
        81: Opcode.WITH_CLEANUP,
        83: Opcode.RETURN_VALUE,
        84: Opcode.IMPORT_STAR,
        86: Opcode.YIELD_VALUE,
        87: Opcode.POP_BLOCK,
        88: Opcode.END_FINALLY,
        89: Opcode.POP_EXCEPT,

        90: Opcode.STORE_NAME_A,
        91: Opcode.DELETE_NAME_A,
        92: Opcode.UNPACK_SEQUENCE_A,
        93: Opcode.FOR_ITER_A,
        94: Opcode.UNPACK_EX_A,
        95: Opcode.STORE_ATTR_A,
        96: Opcode.DELETE_ATTR_A,
        97: Opcode.STORE_GLOBAL_A,
        98: Opcode.DELETE_GLOBAL_A,

        100: Opcode.LOAD_CONST_A,
        101: Opcode.LOAD_NAME_A,
        102: Opcode.BUILD_TUPLE_A,
        103: Opcode.BUILD_LIST_A,
        104: Opcode.BUILD_SET_A,
        105: Opcode.BUILD_MAP_A,
        106: Opcode.LOAD_ATTR_A,
        107: Opcode.COMPARE_OP_A,
        108: Opcode.IMPORT_NAME_A,
        109: Opcode.IMPORT_FROM_A,

        110: Opcode.JUMP_FORWARD_A,
        111: Opcode.JUMP_IF_FALSE_OR_POP_A,
        112: Opcode.JUMP_IF_TRUE_OR_POP_A,
        113: Opcode.JUMP_ABSOLUTE_A,
        114: Opcode.POP_JUMP_IF_FALSE_A,
        115: Opcode.POP_JUMP_IF_TRUE_A,

        116: Opcode.LOAD_GLOBAL_A,
        119: Opcode.CONTINUE_LOOP_A,

        120: Opcode.SETUP_LOOP_A,
        121: Opcode.SETUP_EXCEPT_A,
        122: Opcode.SETUP_FINALLY_A,

        124: Opcode.LOAD_FAST_A,
        125: Opcode.STORE_FAST_A,
        126: Opcode.DELETE_FAST_A,

        130: Opcode.RAISE_VARARGS_A,
        131: Opcode.CALL_FUNCTION_A,
        132: Opcode.MAKE_FUNCTION_A,
        133: Opcode.BUILD_SLICE_A,
        134: Opcode.MAKE_CLOSURE_A,
        135: Opcode.LOAD_CLOSURE_A,
        136: Opcode.LOAD_DEREF_A,
        137: Opcode.STORE_DEREF_A,
        138: Opcode.DELETE_DEREF_A,

        140: Opcode.CALL_FUNCTION_VAR_A,
        141: Opcode.CALL_FUNCTION_KW_A,
        142: Opcode.CALL_FUNCTION_VAR_KW_A,
        143: Opcode.SETUP_WITH_A,
        144: Opcode.EXTENDED_ARG_A,
        145: Opcode.LIST_APPEND_A,
        146: Opcode.SET_ADD_A,
        147: Opcode.MAP_ADD_A,
    }

    return mapping.get(id_)

def python_3_3_map(id_: int) -> int:
    mapping = {
        1:  Opcode.POP_TOP,
        2:  Opcode.ROT_TWO,
        3:  Opcode.ROT_THREE,
        4:  Opcode.DUP_TOP,
        5:  Opcode.DUP_TOP_TWO,
        9:  Opcode.NOP,

        10: Opcode.UNARY_POSITIVE,
        11: Opcode.UNARY_NEGATIVE,
        12: Opcode.UNARY_NOT,
        15: Opcode.UNARY_INVERT,

        19: Opcode.BINARY_POWER,
        20: Opcode.BINARY_MULTIPLY,
        22: Opcode.BINARY_MODULO,
        23: Opcode.BINARY_ADD,
        24: Opcode.BINARY_SUBTRACT,
        25: Opcode.BINARY_SUBSCR,
        26: Opcode.BINARY_FLOOR_DIVIDE,
        27: Opcode.BINARY_TRUE_DIVIDE,
        28: Opcode.INPLACE_FLOOR_DIVIDE,
        29: Opcode.INPLACE_TRUE_DIVIDE,

        54: Opcode.STORE_MAP,
        55: Opcode.INPLACE_ADD,
        56: Opcode.INPLACE_SUBTRACT,
        57: Opcode.INPLACE_MULTIPLY,
        59: Opcode.INPLACE_MODULO,

        60: Opcode.STORE_SUBSCR,
        61: Opcode.DELETE_SUBSCR,
        62: Opcode.BINARY_LSHIFT,
        63: Opcode.BINARY_RSHIFT,
        64: Opcode.BINARY_AND,
        65: Opcode.BINARY_XOR,
        66: Opcode.BINARY_OR,
        67: Opcode.INPLACE_POWER,
        68: Opcode.GET_ITER,
        69: Opcode.STORE_LOCALS,

        70: Opcode.PRINT_EXPR,
        71: Opcode.LOAD_BUILD_CLASS,
        72: Opcode.YIELD_FROM,

        75: Opcode.INPLACE_LSHIFT,
        76: Opcode.INPLACE_RSHIFT,
        77: Opcode.INPLACE_AND,
        78: Opcode.INPLACE_XOR,
        79: Opcode.INPLACE_OR,

        80: Opcode.BREAK_LOOP,
        81: Opcode.WITH_CLEANUP,
        83: Opcode.RETURN_VALUE,
        84: Opcode.IMPORT_STAR,
        86: Opcode.YIELD_VALUE,
        87: Opcode.POP_BLOCK,
        88: Opcode.END_FINALLY,
        89: Opcode.POP_EXCEPT,

        90: Opcode.STORE_NAME_A,
        91: Opcode.DELETE_NAME_A,
        92: Opcode.UNPACK_SEQUENCE_A,
        93: Opcode.FOR_ITER_A,
        94: Opcode.UNPACK_EX_A,
        95: Opcode.STORE_ATTR_A,
        96: Opcode.DELETE_ATTR_A,
        97: Opcode.STORE_GLOBAL_A,
        98: Opcode.DELETE_GLOBAL_A,

        100: Opcode.LOAD_CONST_A,
        101: Opcode.LOAD_NAME_A,
        102: Opcode.BUILD_TUPLE_A,
        103: Opcode.BUILD_LIST_A,
        104: Opcode.BUILD_SET_A,
        105: Opcode.BUILD_MAP_A,
        106: Opcode.LOAD_ATTR_A,
        107: Opcode.COMPARE_OP_A,
        108: Opcode.IMPORT_NAME_A,
        109: Opcode.IMPORT_FROM_A,

        110: Opcode.JUMP_FORWARD_A,
        111: Opcode.JUMP_IF_FALSE_OR_POP_A,
        112: Opcode.JUMP_IF_TRUE_OR_POP_A,
        113: Opcode.JUMP_ABSOLUTE_A,
        114: Opcode.POP_JUMP_IF_FALSE_A,
        115: Opcode.POP_JUMP_IF_TRUE_A,

        116: Opcode.LOAD_GLOBAL_A,
        119: Opcode.CONTINUE_LOOP_A,

        120: Opcode.SETUP_LOOP_A,
        121: Opcode.SETUP_EXCEPT_A,
        122: Opcode.SETUP_FINALLY_A,

        124: Opcode.LOAD_FAST_A,
        125: Opcode.STORE_FAST_A,
        126: Opcode.DELETE_FAST_A,

        130: Opcode.RAISE_VARARGS_A,
        131: Opcode.CALL_FUNCTION_A,
        132: Opcode.MAKE_FUNCTION_A,
        133: Opcode.BUILD_SLICE_A,
        134: Opcode.MAKE_CLOSURE_A,
        135: Opcode.LOAD_CLOSURE_A,
        136: Opcode.LOAD_DEREF_A,
        137: Opcode.STORE_DEREF_A,
        138: Opcode.DELETE_DEREF_A,

        140: Opcode.CALL_FUNCTION_VAR_A,
        141: Opcode.CALL_FUNCTION_KW_A,
        142: Opcode.CALL_FUNCTION_VAR_KW_A,
        143: Opcode.SETUP_WITH_A,
        144: Opcode.EXTENDED_ARG_A,

        145: Opcode.LIST_APPEND_A,
        146: Opcode.SET_ADD_A,
        147: Opcode.MAP_ADD_A,
    }

    return mapping.get(id_)

def python_3_4_map(id_: int) -> int:
    mapping = {
        1:  Opcode.POP_TOP,
        2:  Opcode.ROT_TWO,
        3:  Opcode.ROT_THREE,
        4:  Opcode.DUP_TOP,
        5:  Opcode.DUP_TOP_TWO,
        9:  Opcode.NOP,

        10: Opcode.UNARY_POSITIVE,
        11: Opcode.UNARY_NEGATIVE,
        12: Opcode.UNARY_NOT,
        15: Opcode.UNARY_INVERT,

        19: Opcode.BINARY_POWER,
        20: Opcode.BINARY_MULTIPLY,
        22: Opcode.BINARY_MODULO,
        23: Opcode.BINARY_ADD,
        24: Opcode.BINARY_SUBTRACT,
        25: Opcode.BINARY_SUBSCR,
        26: Opcode.BINARY_FLOOR_DIVIDE,
        27: Opcode.BINARY_TRUE_DIVIDE,
        28: Opcode.INPLACE_FLOOR_DIVIDE,
        29: Opcode.INPLACE_TRUE_DIVIDE,

        54: Opcode.STORE_MAP,
        55: Opcode.INPLACE_ADD,
        56: Opcode.INPLACE_SUBTRACT,
        57: Opcode.INPLACE_MULTIPLY,
        59: Opcode.INPLACE_MODULO,

        60: Opcode.STORE_SUBSCR,
        61: Opcode.DELETE_SUBSCR,
        62: Opcode.BINARY_LSHIFT,
        63: Opcode.BINARY_RSHIFT,
        64: Opcode.BINARY_AND,
        65: Opcode.BINARY_XOR,
        66: Opcode.BINARY_OR,
        67: Opcode.INPLACE_POWER,
        68: Opcode.GET_ITER,

        70: Opcode.PRINT_EXPR,
        71: Opcode.LOAD_BUILD_CLASS,
        72: Opcode.YIELD_FROM,

        75: Opcode.INPLACE_LSHIFT,
        76: Opcode.INPLACE_RSHIFT,
        77: Opcode.INPLACE_AND,
        78: Opcode.INPLACE_XOR,
        79: Opcode.INPLACE_OR,

        80: Opcode.BREAK_LOOP,
        81: Opcode.WITH_CLEANUP,
        83: Opcode.RETURN_VALUE,
        84: Opcode.IMPORT_STAR,
        86: Opcode.YIELD_VALUE,
        87: Opcode.POP_BLOCK,
        88: Opcode.END_FINALLY,
        89: Opcode.POP_EXCEPT,

        90: Opcode.STORE_NAME_A,
        91: Opcode.DELETE_NAME_A,
        92: Opcode.UNPACK_SEQUENCE_A,
        93: Opcode.FOR_ITER_A,
        94: Opcode.UNPACK_EX_A,
        95: Opcode.STORE_ATTR_A,
        96: Opcode.DELETE_ATTR_A,
        97: Opcode.STORE_GLOBAL_A,
        98: Opcode.DELETE_GLOBAL_A,

        100: Opcode.LOAD_CONST_A,
        101: Opcode.LOAD_NAME_A,
        102: Opcode.BUILD_TUPLE_A,
        103: Opcode.BUILD_LIST_A,
        104: Opcode.BUILD_SET_A,
        105: Opcode.BUILD_MAP_A,
        106: Opcode.LOAD_ATTR_A,
        107: Opcode.COMPARE_OP_A,
        108: Opcode.IMPORT_NAME_A,
        109: Opcode.IMPORT_FROM_A,

        110: Opcode.JUMP_FORWARD_A,
        111: Opcode.JUMP_IF_FALSE_OR_POP_A,
        112: Opcode.JUMP_IF_TRUE_OR_POP_A,
        113: Opcode.JUMP_ABSOLUTE_A,
        114: Opcode.POP_JUMP_IF_FALSE_A,
        115: Opcode.POP_JUMP_IF_TRUE_A,

        116: Opcode.LOAD_GLOBAL_A,
        119: Opcode.CONTINUE_LOOP_A,

        120: Opcode.SETUP_LOOP_A,
        121: Opcode.SETUP_EXCEPT_A,
        122: Opcode.SETUP_FINALLY_A,

        124: Opcode.LOAD_FAST_A,
        125: Opcode.STORE_FAST_A,
        126: Opcode.DELETE_FAST_A,

        130: Opcode.RAISE_VARARGS_A,
        131: Opcode.CALL_FUNCTION_A,
        132: Opcode.MAKE_FUNCTION_A,
        133: Opcode.BUILD_SLICE_A,
        134: Opcode.MAKE_CLOSURE_A,
        135: Opcode.LOAD_CLOSURE_A,
        136: Opcode.LOAD_DEREF_A,
        137: Opcode.STORE_DEREF_A,
        138: Opcode.DELETE_DEREF_A,

        140: Opcode.CALL_FUNCTION_VAR_A,
        141: Opcode.CALL_FUNCTION_KW_A,
        142: Opcode.CALL_FUNCTION_VAR_KW_A,
        143: Opcode.SETUP_WITH_A,
        144: Opcode.EXTENDED_ARG_A,

        145: Opcode.LIST_APPEND_A,
        146: Opcode.SET_ADD_A,
        147: Opcode.MAP_ADD_A,
        148: Opcode.LOAD_CLASSDEREF_A,
    }

    return mapping.get(id_)

def python_3_5_map(id_: int) -> int:
    mapping = {
        1:  Opcode.POP_TOP,
        2:  Opcode.ROT_TWO,
        3:  Opcode.ROT_THREE,
        4:  Opcode.DUP_TOP,
        5:  Opcode.DUP_TOP_TWO,
        9:  Opcode.NOP,

        10: Opcode.UNARY_POSITIVE,
        11: Opcode.UNARY_NEGATIVE,
        12: Opcode.UNARY_NOT,
        15: Opcode.UNARY_INVERT,
        16: Opcode.BINARY_MATRIX_MULTIPLY,
        17: Opcode.INPLACE_MATRIX_MULTIPLY,

        19: Opcode.BINARY_POWER,
        20: Opcode.BINARY_MULTIPLY,
        22: Opcode.BINARY_MODULO,
        23: Opcode.BINARY_ADD,
        24: Opcode.BINARY_SUBTRACT,
        25: Opcode.BINARY_SUBSCR,
        26: Opcode.BINARY_FLOOR_DIVIDE,
        27: Opcode.BINARY_TRUE_DIVIDE,
        28: Opcode.INPLACE_FLOOR_DIVIDE,
        29: Opcode.INPLACE_TRUE_DIVIDE,

        50: Opcode.GET_AITER,
        51: Opcode.GET_ANEXT,
        52: Opcode.BEFORE_ASYNC_WITH,

        55: Opcode.INPLACE_ADD,
        56: Opcode.INPLACE_SUBTRACT,
        57: Opcode.INPLACE_MULTIPLY,
        59: Opcode.INPLACE_MODULO,

        60: Opcode.STORE_SUBSCR,
        61: Opcode.DELETE_SUBSCR,
        62: Opcode.BINARY_LSHIFT,
        63: Opcode.BINARY_RSHIFT,
        64: Opcode.BINARY_AND,
        65: Opcode.BINARY_XOR,
        66: Opcode.BINARY_OR,
        67: Opcode.INPLACE_POWER,
        68: Opcode.GET_ITER,
        69: Opcode.GET_YIELD_FROM_ITER,

        70: Opcode.PRINT_EXPR,
        71: Opcode.LOAD_BUILD_CLASS,
        72: Opcode.YIELD_FROM,
        73: Opcode.GET_AWAITABLE,

        75: Opcode.INPLACE_LSHIFT,
        76: Opcode.INPLACE_RSHIFT,
        77: Opcode.INPLACE_AND,
        78: Opcode.INPLACE_XOR,
        79: Opcode.INPLACE_OR,

        80: Opcode.BREAK_LOOP,
        81: Opcode.WITH_CLEANUP_START,
        82: Opcode.WITH_CLEANUP_FINISH,
        83: Opcode.RETURN_VALUE,
        84: Opcode.IMPORT_STAR,
        86: Opcode.YIELD_VALUE,
        87: Opcode.POP_BLOCK,
        88: Opcode.END_FINALLY,
        89: Opcode.POP_EXCEPT,

        90: Opcode.STORE_NAME_A,
        91: Opcode.DELETE_NAME_A,
        92: Opcode.UNPACK_SEQUENCE_A,
        93: Opcode.FOR_ITER_A,
        94: Opcode.UNPACK_EX_A,
        95: Opcode.STORE_ATTR_A,
        96: Opcode.DELETE_ATTR_A,
        97: Opcode.STORE_GLOBAL_A,
        98: Opcode.DELETE_GLOBAL_A,

        100: Opcode.LOAD_CONST_A,
        101: Opcode.LOAD_NAME_A,
        102: Opcode.BUILD_TUPLE_A,
        103: Opcode.BUILD_LIST_A,
        104: Opcode.BUILD_SET_A,
        105: Opcode.BUILD_MAP_A,
        106: Opcode.LOAD_ATTR_A,
        107: Opcode.COMPARE_OP_A,
        108: Opcode.IMPORT_NAME_A,
        109: Opcode.IMPORT_FROM_A,

        110: Opcode.JUMP_FORWARD_A,
        111: Opcode.JUMP_IF_FALSE_OR_POP_A,
        112: Opcode.JUMP_IF_TRUE_OR_POP_A,
        113: Opcode.JUMP_ABSOLUTE_A,
        114: Opcode.POP_JUMP_IF_FALSE_A,
        115: Opcode.POP_JUMP_IF_TRUE_A,

        116: Opcode.LOAD_GLOBAL_A,
        119: Opcode.CONTINUE_LOOP_A,

        120: Opcode.SETUP_LOOP_A,
        121: Opcode.SETUP_EXCEPT_A,
        122: Opcode.SETUP_FINALLY_A,

        124: Opcode.LOAD_FAST_A,
        125: Opcode.STORE_FAST_A,
        126: Opcode.DELETE_FAST_A,

        130: Opcode.RAISE_VARARGS_A,
        131: Opcode.CALL_FUNCTION_A,
        132: Opcode.MAKE_FUNCTION_A,
        133: Opcode.BUILD_SLICE_A,
        134: Opcode.MAKE_CLOSURE_A,
        135: Opcode.LOAD_CLOSURE_A,
        136: Opcode.LOAD_DEREF_A,
        137: Opcode.STORE_DEREF_A,
        138: Opcode.DELETE_DEREF_A,

        140: Opcode.CALL_FUNCTION_VAR_A,
        141: Opcode.CALL_FUNCTION_KW_A,
        142: Opcode.CALL_FUNCTION_VAR_KW_A,
        143: Opcode.SETUP_WITH_A,
        144: Opcode.EXTENDED_ARG_A,

        145: Opcode.LIST_APPEND_A,
        146: Opcode.SET_ADD_A,
        147: Opcode.MAP_ADD_A,
        148: Opcode.LOAD_CLASSDEREF_A,
        149: Opcode.BUILD_LIST_UNPACK_A,
        150: Opcode.BUILD_MAP_UNPACK_A,
        151: Opcode.BUILD_MAP_UNPACK_WITH_CALL_A,
        152: Opcode.BUILD_TUPLE_UNPACK_A,
        153: Opcode.BUILD_SET_UNPACK_A,
        154: Opcode.SETUP_ASYNC_WITH_A,
    }

    return mapping.get(id_)

def python_3_6_map(id_: int) -> int:
    mapping = {
        1:  Opcode.POP_TOP,
        2:  Opcode.ROT_TWO,
        3:  Opcode.ROT_THREE,
        4:  Opcode.DUP_TOP,
        5:  Opcode.DUP_TOP_TWO,
        9:  Opcode.NOP,

        10: Opcode.UNARY_POSITIVE,
        11: Opcode.UNARY_NEGATIVE,
        12: Opcode.UNARY_NOT,
        15: Opcode.UNARY_INVERT,
        16: Opcode.BINARY_MATRIX_MULTIPLY,
        17: Opcode.INPLACE_MATRIX_MULTIPLY,

        19: Opcode.BINARY_POWER,
        20: Opcode.BINARY_MULTIPLY,
        22: Opcode.BINARY_MODULO,
        23: Opcode.BINARY_ADD,
        24: Opcode.BINARY_SUBTRACT,
        25: Opcode.BINARY_SUBSCR,
        26: Opcode.BINARY_FLOOR_DIVIDE,
        27: Opcode.BINARY_TRUE_DIVIDE,
        28: Opcode.INPLACE_FLOOR_DIVIDE,
        29: Opcode.INPLACE_TRUE_DIVIDE,

        50: Opcode.GET_AITER,
        51: Opcode.GET_ANEXT,
        52: Opcode.BEFORE_ASYNC_WITH,

        55: Opcode.INPLACE_ADD,
        56: Opcode.INPLACE_SUBTRACT,
        57: Opcode.INPLACE_MULTIPLY,
        59: Opcode.INPLACE_MODULO,

        60: Opcode.STORE_SUBSCR,
        61: Opcode.DELETE_SUBSCR,
        62: Opcode.BINARY_LSHIFT,
        63: Opcode.BINARY_RSHIFT,
        64: Opcode.BINARY_AND,
        65: Opcode.BINARY_XOR,
        66: Opcode.BINARY_OR,
        67: Opcode.INPLACE_POWER,
        68: Opcode.GET_ITER,
        69: Opcode.GET_YIELD_FROM_ITER,

        70: Opcode.PRINT_EXPR,
        71: Opcode.LOAD_BUILD_CLASS,
        72: Opcode.YIELD_FROM,
        73: Opcode.GET_AWAITABLE,

        75: Opcode.INPLACE_LSHIFT,
        76: Opcode.INPLACE_RSHIFT,
        77: Opcode.INPLACE_AND,
        78: Opcode.INPLACE_XOR,
        79: Opcode.INPLACE_OR,

        80: Opcode.BREAK_LOOP,
        81: Opcode.WITH_CLEANUP_START,
        82: Opcode.WITH_CLEANUP_FINISH,
        83: Opcode.RETURN_VALUE,
        84: Opcode.IMPORT_STAR,
        85: Opcode.SETUP_ANNOTATIONS,
        86: Opcode.YIELD_VALUE,
        87: Opcode.POP_BLOCK,
        88: Opcode.END_FINALLY,
        89: Opcode.POP_EXCEPT,

        90: Opcode.STORE_NAME_A,
        91: Opcode.DELETE_NAME_A,
        92: Opcode.UNPACK_SEQUENCE_A,
        93: Opcode.FOR_ITER_A,
        94: Opcode.UNPACK_EX_A,
        95: Opcode.STORE_ATTR_A,
        96: Opcode.DELETE_ATTR_A,
        97: Opcode.STORE_GLOBAL_A,
        98: Opcode.DELETE_GLOBAL_A,

        100: Opcode.LOAD_CONST_A,
        101: Opcode.LOAD_NAME_A,
        102: Opcode.BUILD_TUPLE_A,
        103: Opcode.BUILD_LIST_A,
        104: Opcode.BUILD_SET_A,
        105: Opcode.BUILD_MAP_A,
        106: Opcode.LOAD_ATTR_A,
        107: Opcode.COMPARE_OP_A,
        108: Opcode.IMPORT_NAME_A,
        109: Opcode.IMPORT_FROM_A,

        110: Opcode.JUMP_FORWARD_A,
        111: Opcode.JUMP_IF_FALSE_OR_POP_A,
        112: Opcode.JUMP_IF_TRUE_OR_POP_A,
        113: Opcode.JUMP_ABSOLUTE_A,
        114: Opcode.POP_JUMP_IF_FALSE_A,
        115: Opcode.POP_JUMP_IF_TRUE_A,

        116: Opcode.LOAD_GLOBAL_A,
        119: Opcode.CONTINUE_LOOP_A,

        120: Opcode.SETUP_LOOP_A,
        121: Opcode.SETUP_EXCEPT_A,
        122: Opcode.SETUP_FINALLY_A,

        124: Opcode.LOAD_FAST_A,
        125: Opcode.STORE_FAST_A,
        126: Opcode.DELETE_FAST_A,
        127: Opcode.STORE_ANNOTATION_A,

        130: Opcode.RAISE_VARARGS_A,
        131: Opcode.CALL_FUNCTION_A,
        132: Opcode.MAKE_FUNCTION_A,
        133: Opcode.BUILD_SLICE_A,
        135: Opcode.LOAD_CLOSURE_A,
        136: Opcode.LOAD_DEREF_A,
        137: Opcode.STORE_DEREF_A,
        138: Opcode.DELETE_DEREF_A,

        141: Opcode.CALL_FUNCTION_KW_A,
        142: Opcode.CALL_FUNCTION_EX_A,
        143: Opcode.SETUP_WITH_A,
        144: Opcode.EXTENDED_ARG_A,

        145: Opcode.LIST_APPEND_A,
        146: Opcode.SET_ADD_A,
        147: Opcode.MAP_ADD_A,
        148: Opcode.LOAD_CLASSDEREF_A,
        149: Opcode.BUILD_LIST_UNPACK_A,
        150: Opcode.BUILD_MAP_UNPACK_A,
        151: Opcode.BUILD_MAP_UNPACK_WITH_CALL_A,
        152: Opcode.BUILD_TUPLE_UNPACK_A,
        153: Opcode.BUILD_SET_UNPACK_A,
        154: Opcode.SETUP_ASYNC_WITH_A,
        155: Opcode.FORMAT_VALUE_A,
        156: Opcode.BUILD_CONST_KEY_MAP_A,
        157: Opcode.BUILD_STRING_A,
        158: Opcode.BUILD_TUPLE_UNPACK_WITH_CALL_A,
    }

    return mapping.get(id_)

def python_3_7_map(id_: int) -> int:
    mapping = {
        1:  Opcode.POP_TOP,
        2:  Opcode.ROT_TWO,
        3:  Opcode.ROT_THREE,
        4:  Opcode.DUP_TOP,
        5:  Opcode.DUP_TOP_TWO,
        9:  Opcode.NOP,

        10: Opcode.UNARY_POSITIVE,
        11: Opcode.UNARY_NEGATIVE,
        12: Opcode.UNARY_NOT,
        15: Opcode.UNARY_INVERT,
        16: Opcode.BINARY_MATRIX_MULTIPLY,
        17: Opcode.INPLACE_MATRIX_MULTIPLY,

        19: Opcode.BINARY_POWER,
        20: Opcode.BINARY_MULTIPLY,
        22: Opcode.BINARY_MODULO,
        23: Opcode.BINARY_ADD,
        24: Opcode.BINARY_SUBTRACT,
        25: Opcode.BINARY_SUBSCR,
        26: Opcode.BINARY_FLOOR_DIVIDE,
        27: Opcode.BINARY_TRUE_DIVIDE,
        28: Opcode.INPLACE_FLOOR_DIVIDE,
        29: Opcode.INPLACE_TRUE_DIVIDE,

        50: Opcode.GET_AITER,
        51: Opcode.GET_ANEXT,
        52: Opcode.BEFORE_ASYNC_WITH,

        55: Opcode.INPLACE_ADD,
        56: Opcode.INPLACE_SUBTRACT,
        57: Opcode.INPLACE_MULTIPLY,
        59: Opcode.INPLACE_MODULO,

        60: Opcode.STORE_SUBSCR,
        61: Opcode.DELETE_SUBSCR,
        62: Opcode.BINARY_LSHIFT,
        63: Opcode.BINARY_RSHIFT,
        64: Opcode.BINARY_AND,
        65: Opcode.BINARY_XOR,
        66: Opcode.BINARY_OR,
        67: Opcode.INPLACE_POWER,
        68: Opcode.GET_ITER,
        69: Opcode.GET_YIELD_FROM_ITER,

        70: Opcode.PRINT_EXPR,
        71: Opcode.LOAD_BUILD_CLASS,
        72: Opcode.YIELD_FROM,
        73: Opcode.GET_AWAITABLE,

        75: Opcode.INPLACE_LSHIFT,
        76: Opcode.INPLACE_RSHIFT,
        77: Opcode.INPLACE_AND,
        78: Opcode.INPLACE_XOR,
        79: Opcode.INPLACE_OR,

        80: Opcode.BREAK_LOOP,
        81: Opcode.WITH_CLEANUP_START,
        82: Opcode.WITH_CLEANUP_FINISH,
        83: Opcode.RETURN_VALUE,
        84: Opcode.IMPORT_STAR,
        85: Opcode.SETUP_ANNOTATIONS,
        86: Opcode.YIELD_VALUE,
        87: Opcode.POP_BLOCK,
        88: Opcode.END_FINALLY,
        89: Opcode.POP_EXCEPT,

        90: Opcode.STORE_NAME_A,
        91: Opcode.DELETE_NAME_A,
        92: Opcode.UNPACK_SEQUENCE_A,
        93: Opcode.FOR_ITER_A,
        94: Opcode.UNPACK_EX_A,
        95: Opcode.STORE_ATTR_A,
        96: Opcode.DELETE_ATTR_A,
        97: Opcode.STORE_GLOBAL_A,
        98: Opcode.DELETE_GLOBAL_A,

        100: Opcode.LOAD_CONST_A,
        101: Opcode.LOAD_NAME_A,
        102: Opcode.BUILD_TUPLE_A,
        103: Opcode.BUILD_LIST_A,
        104: Opcode.BUILD_SET_A,
        105: Opcode.BUILD_MAP_A,
        106: Opcode.LOAD_ATTR_A,
        107: Opcode.COMPARE_OP_A,
        108: Opcode.IMPORT_NAME_A,
        109: Opcode.IMPORT_FROM_A,

        110: Opcode.JUMP_FORWARD_A,
        111: Opcode.JUMP_IF_FALSE_OR_POP_A,
        112: Opcode.JUMP_IF_TRUE_OR_POP_A,
        113: Opcode.JUMP_ABSOLUTE_A,
        114: Opcode.POP_JUMP_IF_FALSE_A,
        115: Opcode.POP_JUMP_IF_TRUE_A,

        116: Opcode.LOAD_GLOBAL_A,
        119: Opcode.CONTINUE_LOOP_A,

        120: Opcode.SETUP_LOOP_A,
        121: Opcode.SETUP_EXCEPT_A,
        122: Opcode.SETUP_FINALLY_A,

        124: Opcode.LOAD_FAST_A,
        125: Opcode.STORE_FAST_A,
        126: Opcode.DELETE_FAST_A,
        127: Opcode.STORE_ANNOTATION_A,

        130: Opcode.RAISE_VARARGS_A,
        131: Opcode.CALL_FUNCTION_A,
        132: Opcode.MAKE_FUNCTION_A,
        133: Opcode.BUILD_SLICE_A,
        135: Opcode.LOAD_CLOSURE_A,
        136: Opcode.LOAD_DEREF_A,
        137: Opcode.STORE_DEREF_A,
        138: Opcode.DELETE_DEREF_A,

        141: Opcode.CALL_FUNCTION_KW_A,
        142: Opcode.CALL_FUNCTION_EX_A,
        143: Opcode.SETUP_WITH_A,
        144: Opcode.EXTENDED_ARG_A,

        145: Opcode.LIST_APPEND_A,
        146: Opcode.SET_ADD_A,
        147: Opcode.MAP_ADD_A,
        148: Opcode.LOAD_CLASSDEREF_A,
        149: Opcode.BUILD_LIST_UNPACK_A,
        150: Opcode.BUILD_MAP_UNPACK_A,
        151: Opcode.BUILD_MAP_UNPACK_WITH_CALL_A,
        152: Opcode.BUILD_TUPLE_UNPACK_A,
        153: Opcode.BUILD_SET_UNPACK_A,
        154: Opcode.SETUP_ASYNC_WITH_A,
        155: Opcode.FORMAT_VALUE_A,
        156: Opcode.BUILD_CONST_KEY_MAP_A,
        157: Opcode.BUILD_STRING_A,
        158: Opcode.BUILD_TUPLE_UNPACK_WITH_CALL_A,

        160: Opcode.LOAD_METHOD_A,
        161: Opcode.CALL_METHOD_A,
    }

    return mapping.get(id_)

def python_3_8_map(id_: int) -> int:
    mapping = {
        1:  Opcode.POP_TOP,
        2:  Opcode.ROT_TWO,
        3:  Opcode.ROT_THREE,
        4:  Opcode.DUP_TOP,
        5:  Opcode.DUP_TOP_TWO,
        6:  Opcode.ROT_FOUR,
        9:  Opcode.NOP,

        10: Opcode.UNARY_POSITIVE,
        11: Opcode.UNARY_NEGATIVE,
        12: Opcode.UNARY_NOT,
        15: Opcode.UNARY_INVERT,
        16: Opcode.BINARY_MATRIX_MULTIPLY,
        17: Opcode.INPLACE_MATRIX_MULTIPLY,

        19: Opcode.BINARY_POWER,
        20: Opcode.BINARY_MULTIPLY,
        22: Opcode.BINARY_MODULO,
        23: Opcode.BINARY_ADD,
        24: Opcode.BINARY_SUBTRACT,
        25: Opcode.BINARY_SUBSCR,
        26: Opcode.BINARY_FLOOR_DIVIDE,
        27: Opcode.BINARY_TRUE_DIVIDE,
        28: Opcode.INPLACE_FLOOR_DIVIDE,
        29: Opcode.INPLACE_TRUE_DIVIDE,

        50: Opcode.GET_AITER,
        51: Opcode.GET_ANEXT,
        52: Opcode.BEFORE_ASYNC_WITH,
        53: Opcode.BEGIN_FINALLY,
        54: Opcode.END_ASYNC_FOR,

        55: Opcode.INPLACE_ADD,
        56: Opcode.INPLACE_SUBTRACT,
        57: Opcode.INPLACE_MULTIPLY,
        59: Opcode.INPLACE_MODULO,

        60: Opcode.STORE_SUBSCR,
        61: Opcode.DELETE_SUBSCR,
        62: Opcode.BINARY_LSHIFT,
        63: Opcode.BINARY_RSHIFT,
        64: Opcode.BINARY_AND,
        65: Opcode.BINARY_XOR,
        66: Opcode.BINARY_OR,
        67: Opcode.INPLACE_POWER,
        68: Opcode.GET_ITER,
        69: Opcode.GET_YIELD_FROM_ITER,

        70: Opcode.PRINT_EXPR,
        71: Opcode.LOAD_BUILD_CLASS,
        72: Opcode.YIELD_FROM,
        73: Opcode.GET_AWAITABLE,

        75: Opcode.INPLACE_LSHIFT,
        76: Opcode.INPLACE_RSHIFT,
        77: Opcode.INPLACE_AND,
        78: Opcode.INPLACE_XOR,
        79: Opcode.INPLACE_OR,

        81: Opcode.WITH_CLEANUP_START,
        82: Opcode.WITH_CLEANUP_FINISH,
        83: Opcode.RETURN_VALUE,
        84: Opcode.IMPORT_STAR,
        85: Opcode.SETUP_ANNOTATIONS,
        86: Opcode.YIELD_VALUE,
        87: Opcode.POP_BLOCK,
        88: Opcode.END_FINALLY,
        89: Opcode.POP_EXCEPT,

        90: Opcode.STORE_NAME_A,
        91: Opcode.DELETE_NAME_A,
        92: Opcode.UNPACK_SEQUENCE_A,
        93: Opcode.FOR_ITER_A,
        94: Opcode.UNPACK_EX_A,
        95: Opcode.STORE_ATTR_A,
        96: Opcode.DELETE_ATTR_A,
        97: Opcode.STORE_GLOBAL_A,
        98: Opcode.DELETE_GLOBAL_A,

        100: Opcode.LOAD_CONST_A,
        101: Opcode.LOAD_NAME_A,
        102: Opcode.BUILD_TUPLE_A,
        103: Opcode.BUILD_LIST_A,
        104: Opcode.BUILD_SET_A,
        105: Opcode.BUILD_MAP_A,
        106: Opcode.LOAD_ATTR_A,
        107: Opcode.COMPARE_OP_A,
        108: Opcode.IMPORT_NAME_A,
        109: Opcode.IMPORT_FROM_A,

        110: Opcode.JUMP_FORWARD_A,
        111: Opcode.JUMP_IF_FALSE_OR_POP_A,
        112: Opcode.JUMP_IF_TRUE_OR_POP_A,
        113: Opcode.JUMP_ABSOLUTE_A,
        114: Opcode.POP_JUMP_IF_FALSE_A,
        115: Opcode.POP_JUMP_IF_TRUE_A,

        116: Opcode.LOAD_GLOBAL_A,
        122: Opcode.SETUP_FINALLY_A,

        124: Opcode.LOAD_FAST_A,
        125: Opcode.STORE_FAST_A,
        126: Opcode.DELETE_FAST_A,

        130: Opcode.RAISE_VARARGS_A,
        131: Opcode.CALL_FUNCTION_A,
        132: Opcode.MAKE_FUNCTION_A,
        133: Opcode.BUILD_SLICE_A,
        135: Opcode.LOAD_CLOSURE_A,
        136: Opcode.LOAD_DEREF_A,
        137: Opcode.STORE_DEREF_A,
        138: Opcode.DELETE_DEREF_A,

        141: Opcode.CALL_FUNCTION_KW_A,
        142: Opcode.CALL_FUNCTION_EX_A,
        143: Opcode.SETUP_WITH_A,
        144: Opcode.EXTENDED_ARG_A,

        145: Opcode.LIST_APPEND_A,
        146: Opcode.SET_ADD_A,
        147: Opcode.MAP_ADD_A,
        148: Opcode.LOAD_CLASSDEREF_A,
        149: Opcode.BUILD_LIST_UNPACK_A,
        150: Opcode.BUILD_MAP_UNPACK_A,
        151: Opcode.BUILD_MAP_UNPACK_WITH_CALL_A,
        152: Opcode.BUILD_TUPLE_UNPACK_A,
        153: Opcode.BUILD_SET_UNPACK_A,
        154: Opcode.SETUP_ASYNC_WITH_A,
        155: Opcode.FORMAT_VALUE_A,
        156: Opcode.BUILD_CONST_KEY_MAP_A,
        157: Opcode.BUILD_STRING_A,
        158: Opcode.BUILD_TUPLE_UNPACK_WITH_CALL_A,

        160: Opcode.LOAD_METHOD_A,
        161: Opcode.CALL_METHOD_A,
        162: Opcode.CALL_FINALLY_A,
        163: Opcode.POP_FINALLY_A,
    }

    return mapping.get(id_)

def python_3_9_map(id_: int) -> int:
    mapping = {
        1:  Opcode.POP_TOP,
        2:  Opcode.ROT_TWO,
        3:  Opcode.ROT_THREE,
        4:  Opcode.DUP_TOP,
        5:  Opcode.DUP_TOP_TWO,
        6:  Opcode.ROT_FOUR,
        9:  Opcode.NOP,

        10: Opcode.UNARY_POSITIVE,
        11: Opcode.UNARY_NEGATIVE,
        12: Opcode.UNARY_NOT,
        15: Opcode.UNARY_INVERT,
        16: Opcode.BINARY_MATRIX_MULTIPLY,
        17: Opcode.INPLACE_MATRIX_MULTIPLY,

        19: Opcode.BINARY_POWER,
        20: Opcode.BINARY_MULTIPLY,
        22: Opcode.BINARY_MODULO,
        23: Opcode.BINARY_ADD,
        24: Opcode.BINARY_SUBTRACT,
        25: Opcode.BINARY_SUBSCR,
        26: Opcode.BINARY_FLOOR_DIVIDE,
        27: Opcode.BINARY_TRUE_DIVIDE,
        28: Opcode.INPLACE_FLOOR_DIVIDE,
        29: Opcode.INPLACE_TRUE_DIVIDE,

        48: Opcode.RERAISE,
        49: Opcode.WITH_EXCEPT_START,
        50: Opcode.GET_AITER,
        51: Opcode.GET_ANEXT,
        52: Opcode.BEFORE_ASYNC_WITH,
        54: Opcode.END_ASYNC_FOR,

        55: Opcode.INPLACE_ADD,
        56: Opcode.INPLACE_SUBTRACT,
        57: Opcode.INPLACE_MULTIPLY,
        59: Opcode.INPLACE_MODULO,

        60: Opcode.STORE_SUBSCR,
        61: Opcode.DELETE_SUBSCR,
        62: Opcode.BINARY_LSHIFT,
        63: Opcode.BINARY_RSHIFT,
        64: Opcode.BINARY_AND,
        65: Opcode.BINARY_XOR,
        66: Opcode.BINARY_OR,
        67: Opcode.INPLACE_POWER,
        68: Opcode.GET_ITER,
        69: Opcode.GET_YIELD_FROM_ITER,

        70: Opcode.PRINT_EXPR,
        71: Opcode.LOAD_BUILD_CLASS,
        72: Opcode.YIELD_FROM,
        73: Opcode.GET_AWAITABLE,
        74: Opcode.LOAD_ASSERTION_ERROR,

        75: Opcode.INPLACE_LSHIFT,
        76: Opcode.INPLACE_RSHIFT,
        77: Opcode.INPLACE_AND,
        78: Opcode.INPLACE_XOR,
        79: Opcode.INPLACE_OR,

        82: Opcode.LIST_TO_TUPLE,
        83: Opcode.RETURN_VALUE,
        84: Opcode.IMPORT_STAR,
        85: Opcode.SETUP_ANNOTATIONS,
        86: Opcode.YIELD_VALUE,
        87: Opcode.POP_BLOCK,
        89: Opcode.POP_EXCEPT,

        90: Opcode.STORE_NAME_A,
        91: Opcode.DELETE_NAME_A,
        92: Opcode.UNPACK_SEQUENCE_A,
        93: Opcode.FOR_ITER_A,
        94: Opcode.UNPACK_EX_A,
        95: Opcode.STORE_ATTR_A,
        96: Opcode.DELETE_ATTR_A,
        97: Opcode.STORE_GLOBAL_A,
        98: Opcode.DELETE_GLOBAL_A,

        100: Opcode.LOAD_CONST_A,
        101: Opcode.LOAD_NAME_A,
        102: Opcode.BUILD_TUPLE_A,
        103: Opcode.BUILD_LIST_A,
        104: Opcode.BUILD_SET_A,
        105: Opcode.BUILD_MAP_A,
        106: Opcode.LOAD_ATTR_A,
        107: Opcode.COMPARE_OP_A,
        108: Opcode.IMPORT_NAME_A,
        109: Opcode.IMPORT_FROM_A,

        110: Opcode.JUMP_FORWARD_A,
        111: Opcode.JUMP_IF_FALSE_OR_POP_A,
        112: Opcode.JUMP_IF_TRUE_OR_POP_A,
        113: Opcode.JUMP_ABSOLUTE_A,
        114: Opcode.POP_JUMP_IF_FALSE_A,
        115: Opcode.POP_JUMP_IF_TRUE_A,

        116: Opcode.LOAD_GLOBAL_A,
        117: Opcode.IS_OP_A,
        118: Opcode.CONTAINS_OP_A,
        121: Opcode.JUMP_IF_NOT_EXC_MATCH_A,
        122: Opcode.SETUP_FINALLY_A,

        124: Opcode.LOAD_FAST_A,
        125: Opcode.STORE_FAST_A,
        126: Opcode.DELETE_FAST_A,

        130: Opcode.RAISE_VARARGS_A,
        131: Opcode.CALL_FUNCTION_A,
        132: Opcode.MAKE_FUNCTION_A,
        133: Opcode.BUILD_SLICE_A,
        135: Opcode.LOAD_CLOSURE_A,
        136: Opcode.LOAD_DEREF_A,
        137: Opcode.STORE_DEREF_A,
        138: Opcode.DELETE_DEREF_A,

        141: Opcode.CALL_FUNCTION_KW_A,
        142: Opcode.CALL_FUNCTION_EX_A,
        143: Opcode.SETUP_WITH_A,
        144: Opcode.EXTENDED_ARG_A,

        145: Opcode.LIST_APPEND_A,
        146: Opcode.SET_ADD_A,
        147: Opcode.MAP_ADD_A,
        148: Opcode.LOAD_CLASSDEREF_A,
        154: Opcode.SETUP_ASYNC_WITH_A,
        155: Opcode.FORMAT_VALUE_A,
        156: Opcode.BUILD_CONST_KEY_MAP_A,
        157: Opcode.BUILD_STRING_A,

        160: Opcode.LOAD_METHOD_A,
        161: Opcode.CALL_METHOD_A,
        162: Opcode.LIST_EXTEND_A,
        163: Opcode.SET_UPDATE_A,
        164: Opcode.DICT_MERGE_A,
        165: Opcode.DICT_UPDATE_A,
    }

    return mapping.get(id_)

def python_3_10_map(id_: int) -> int:
    mapping = {
        1:  Opcode.POP_TOP,
        2:  Opcode.ROT_TWO,
        3:  Opcode.ROT_THREE,
        4:  Opcode.DUP_TOP,
        5:  Opcode.DUP_TOP_TWO,
        6:  Opcode.ROT_FOUR,
        9:  Opcode.NOP,

        10: Opcode.UNARY_POSITIVE,
        11: Opcode.UNARY_NEGATIVE,
        12: Opcode.UNARY_NOT,
        15: Opcode.UNARY_INVERT,
        16: Opcode.BINARY_MATRIX_MULTIPLY,
        17: Opcode.INPLACE_MATRIX_MULTIPLY,

        19: Opcode.BINARY_POWER,
        20: Opcode.BINARY_MULTIPLY,
        22: Opcode.BINARY_MODULO,
        23: Opcode.BINARY_ADD,
        24: Opcode.BINARY_SUBTRACT,
        25: Opcode.BINARY_SUBSCR,
        26: Opcode.BINARY_FLOOR_DIVIDE,
        27: Opcode.BINARY_TRUE_DIVIDE,
        28: Opcode.INPLACE_FLOOR_DIVIDE,
        29: Opcode.INPLACE_TRUE_DIVIDE,

        30: Opcode.GET_LEN,
        31: Opcode.MATCH_MAPPING,
        32: Opcode.MATCH_SEQUENCE,
        33: Opcode.MATCH_KEYS,
        34: Opcode.COPY_DICT_WITHOUT_KEYS,

        49: Opcode.WITH_EXCEPT_START,
        50: Opcode.GET_AITER,
        51: Opcode.GET_ANEXT,
        52: Opcode.BEFORE_ASYNC_WITH,
        54: Opcode.END_ASYNC_FOR,

        55: Opcode.INPLACE_ADD,
        56: Opcode.INPLACE_SUBTRACT,
        57: Opcode.INPLACE_MULTIPLY,
        59: Opcode.INPLACE_MODULO,

        60: Opcode.STORE_SUBSCR,
        61: Opcode.DELETE_SUBSCR,
        62: Opcode.BINARY_LSHIFT,
        63: Opcode.BINARY_RSHIFT,
        64: Opcode.BINARY_AND,
        65: Opcode.BINARY_XOR,
        66: Opcode.BINARY_OR,
        67: Opcode.INPLACE_POWER,
        68: Opcode.GET_ITER,
        69: Opcode.GET_YIELD_FROM_ITER,

        70: Opcode.PRINT_EXPR,
        71: Opcode.LOAD_BUILD_CLASS,
        72: Opcode.YIELD_FROM,
        73: Opcode.GET_AWAITABLE,
        74: Opcode.LOAD_ASSERTION_ERROR,

        75: Opcode.INPLACE_LSHIFT,
        76: Opcode.INPLACE_RSHIFT,
        77: Opcode.INPLACE_AND,
        78: Opcode.INPLACE_XOR,
        79: Opcode.INPLACE_OR,

        82: Opcode.LIST_TO_TUPLE,
        83: Opcode.RETURN_VALUE,
        84: Opcode.IMPORT_STAR,
        85: Opcode.SETUP_ANNOTATIONS,
        86: Opcode.YIELD_VALUE,
        87: Opcode.POP_BLOCK,
        89: Opcode.POP_EXCEPT,

        90: Opcode.STORE_NAME_A,
        91: Opcode.DELETE_NAME_A,
        92: Opcode.UNPACK_SEQUENCE_A,
        93: Opcode.FOR_ITER_A,
        94: Opcode.UNPACK_EX_A,
        95: Opcode.STORE_ATTR_A,
        96: Opcode.DELETE_ATTR_A,
        97: Opcode.STORE_GLOBAL_A,
        98: Opcode.DELETE_GLOBAL_A,
        99: Opcode.ROT_N_A,

        100: Opcode.LOAD_CONST_A,
        101: Opcode.LOAD_NAME_A,
        102: Opcode.BUILD_TUPLE_A,
        103: Opcode.BUILD_LIST_A,
        104: Opcode.BUILD_SET_A,
        105: Opcode.BUILD_MAP_A,
        106: Opcode.LOAD_ATTR_A,
        107: Opcode.COMPARE_OP_A,
        108: Opcode.IMPORT_NAME_A,
        109: Opcode.IMPORT_FROM_A,

        110: Opcode.JUMP_FORWARD_A,
        111: Opcode.JUMP_IF_FALSE_OR_POP_A,
        112: Opcode.JUMP_IF_TRUE_OR_POP_A,
        113: Opcode.JUMP_ABSOLUTE_A,
        114: Opcode.POP_JUMP_IF_FALSE_A,
        115: Opcode.POP_JUMP_IF_TRUE_A,

        116: Opcode.LOAD_GLOBAL_A,
        117: Opcode.IS_OP_A,
        118: Opcode.CONTAINS_OP_A,
        119: Opcode.RERAISE_A,
        121: Opcode.JUMP_IF_NOT_EXC_MATCH_A,
        122: Opcode.SETUP_FINALLY_A,

        124: Opcode.LOAD_FAST_A,
        125: Opcode.STORE_FAST_A,
        126: Opcode.DELETE_FAST_A,
        129: Opcode.GEN_START_A,

        130: Opcode.RAISE_VARARGS_A,
        131: Opcode.CALL_FUNCTION_A,
        132: Opcode.MAKE_FUNCTION_A,
        133: Opcode.BUILD_SLICE_A,
        135: Opcode.LOAD_CLOSURE_A,
        136: Opcode.LOAD_DEREF_A,
        137: Opcode.STORE_DEREF_A,
        138: Opcode.DELETE_DEREF_A,

        141: Opcode.CALL_FUNCTION_KW_A,
        142: Opcode.CALL_FUNCTION_EX_A,
        143: Opcode.SETUP_WITH_A,
        144: Opcode.EXTENDED_ARG_A,

        145: Opcode.LIST_APPEND_A,
        146: Opcode.SET_ADD_A,
        147: Opcode.MAP_ADD_A,
        148: Opcode.LOAD_CLASSDEREF_A,
        152: Opcode.MATCH_CLASS_A,
        154: Opcode.SETUP_ASYNC_WITH_A,
        155: Opcode.FORMAT_VALUE_A,
        156: Opcode.BUILD_CONST_KEY_MAP_A,
        157: Opcode.BUILD_STRING_A,

        160: Opcode.LOAD_METHOD_A,
        161: Opcode.CALL_METHOD_A,
        162: Opcode.LIST_EXTEND_A,
        163: Opcode.SET_UPDATE_A,
        164: Opcode.DICT_MERGE_A,
        165: Opcode.DICT_UPDATE_A,
    }

    return mapping.get(id_)

def python_3_11_map(id_: int):
    mapping = {
        0:   Opcode.CACHE,
        1:   Opcode.POP_TOP,
        2:   Opcode.PUSH_NULL,
        9:   Opcode.NOP,

        10:  Opcode.UNARY_POSITIVE,
        11:  Opcode.UNARY_NEGATIVE,
        12:  Opcode.UNARY_NOT,
        15:  Opcode.UNARY_INVERT,
        25:  Opcode.BINARY_SUBSCR,
        30:  Opcode.GET_LEN,
        31:  Opcode.MATCH_MAPPING,
        32:  Opcode.MATCH_SEQUENCE,
        33:  Opcode.MATCH_KEYS,
        35:  Opcode.PUSH_EXC_INFO,
        36:  Opcode.CHECK_EXC_MATCH,
        37:  Opcode.CHECK_EG_MATCH,

        49:  Opcode.WITH_EXCEPT_START,
        50:  Opcode.GET_AITER,
        51:  Opcode.GET_ANEXT,
        52:  Opcode.BEFORE_ASYNC_WITH,
        53:  Opcode.BEFORE_WITH,
        54:  Opcode.END_ASYNC_FOR,

        60:  Opcode.STORE_SUBSCR,
        61:  Opcode.DELETE_SUBSCR,
        68:  Opcode.GET_ITER,
        69:  Opcode.GET_YIELD_FROM_ITER,
        70:  Opcode.PRINT_EXPR,
        71:  Opcode.LOAD_BUILD_CLASS,
        74:  Opcode.LOAD_ASSERTION_ERROR,
        75:  Opcode.RETURN_GENERATOR,
        82:  Opcode.LIST_TO_TUPLE,
        83:  Opcode.RETURN_VALUE,
        84:  Opcode.IMPORT_STAR,
        85:  Opcode.SETUP_ANNOTATIONS,
        86:  Opcode.YIELD_VALUE,
        87:  Opcode.ASYNC_GEN_WRAP,
        88:  Opcode.PREP_RERAISE_STAR,
        89:  Opcode.POP_EXCEPT,

        90:  Opcode.STORE_NAME_A,
        91:  Opcode.DELETE_NAME_A,
        92:  Opcode.UNPACK_SEQUENCE_A,
        93:  Opcode.FOR_ITER_A,
        94:  Opcode.UNPACK_EX_A,
        95:  Opcode.STORE_ATTR_A,
        96:  Opcode.DELETE_ATTR_A,
        97:  Opcode.STORE_GLOBAL_A,
        98:  Opcode.DELETE_GLOBAL_A,
        99:  Opcode.SWAP_A,

        100: Opcode.LOAD_CONST_A,
        101: Opcode.LOAD_NAME_A,
        102: Opcode.BUILD_TUPLE_A,
        103: Opcode.BUILD_LIST_A,
        104: Opcode.BUILD_SET_A,
        105: Opcode.BUILD_MAP_A,
        106: Opcode.LOAD_ATTR_A,
        107: Opcode.COMPARE_OP_A,
        108: Opcode.IMPORT_NAME_A,
        109: Opcode.IMPORT_FROM_A,

        110: Opcode.JUMP_FORWARD_A,
        111: Opcode.JUMP_IF_FALSE_OR_POP_A,
        112: Opcode.JUMP_IF_TRUE_OR_POP_A,
        114: Opcode.POP_JUMP_FORWARD_IF_FALSE_A,
        115: Opcode.POP_JUMP_FORWARD_IF_TRUE_A,

        116: Opcode.LOAD_GLOBAL_A,
        117: Opcode.IS_OP_A,
        118: Opcode.CONTAINS_OP_A,
        119: Opcode.RERAISE_A,
        120: Opcode.COPY_A,
        122: Opcode.BINARY_OP_A,
        123: Opcode.SEND_A,

        124: Opcode.LOAD_FAST_A,
        125: Opcode.STORE_FAST_A,
        126: Opcode.DELETE_FAST_A,
        128: Opcode.POP_JUMP_FORWARD_IF_NOT_NONE_A,
        129: Opcode.POP_JUMP_FORWARD_IF_NONE_A,
        130: Opcode.RAISE_VARARGS_A,
        131: Opcode.GET_AWAITABLE_A,
        132: Opcode.MAKE_FUNCTION_A,
        133: Opcode.BUILD_SLICE_A,
        134: Opcode.JUMP_BACKWARD_NO_INTERRUPT_A,
        135: Opcode.MAKE_CELL_A,
        136: Opcode.LOAD_CLOSURE_A,
        137: Opcode.LOAD_DEREF_A,
        138: Opcode.STORE_DEREF_A,
        139: Opcode.DELETE_DEREF_A,
        140: Opcode.JUMP_BACKWARD_A,
        142: Opcode.CALL_FUNCTION_EX_A,
        144: Opcode.EXTENDED_ARG_A,
        145: Opcode.LIST_APPEND_A,
        146: Opcode.SET_ADD_A,
        147: Opcode.MAP_ADD_A,
        148: Opcode.LOAD_CLASSDEREF_A,
        149: Opcode.COPY_FREE_VARS_A,
        151: Opcode.RESUME_A,
        152: Opcode.MATCH_CLASS_A,
        155: Opcode.FORMAT_VALUE_A,
        156: Opcode.BUILD_CONST_KEY_MAP_A,
        157: Opcode.BUILD_STRING_A,
        160: Opcode.LOAD_METHOD_A,
        162: Opcode.LIST_EXTEND_A,
        163: Opcode.SET_UPDATE_A,
        164: Opcode.DICT_MERGE_A,
        165: Opcode.DICT_UPDATE_A,
        166: Opcode.PRECALL_A,
        171: Opcode.CALL_A,
        172: Opcode.KW_NAMES_A,
        173: Opcode.POP_JUMP_BACKWARD_IF_NOT_NONE_A,
        174: Opcode.POP_JUMP_BACKWARD_IF_NONE_A,
        175: Opcode.POP_JUMP_BACKWARD_IF_FALSE_A,
        176: Opcode.POP_JUMP_BACKWARD_IF_TRUE_A,
    }

    return mapping.get(id_)

def python_3_12_map(id_: int) -> int:
    mapping = {
        0: Opcode.CACHE,
        1: Opcode.POP_TOP,
        2: Opcode.PUSH_NULL,
        3: Opcode.INTERPRETER_EXIT,
        4: Opcode.END_FOR,
        5: Opcode.END_SEND,
        9: Opcode.NOP,
        11: Opcode.UNARY_NEGATIVE,
        12: Opcode.UNARY_NOT,
        15: Opcode.UNARY_INVERT,
        # 17: RESERVED (Mapped to INVALID by default)
        25: Opcode.BINARY_SUBSCR,
        26: Opcode.BINARY_SLICE,
        27: Opcode.STORE_SLICE,
        30: Opcode.GET_LEN,
        31: Opcode.MATCH_MAPPING,
        32: Opcode.MATCH_SEQUENCE,
        33: Opcode.MATCH_KEYS,
        35: Opcode.PUSH_EXC_INFO,
        36: Opcode.CHECK_EXC_MATCH,
        37: Opcode.CHECK_EG_MATCH,
        49: Opcode.WITH_EXCEPT_START,
        50: Opcode.GET_AITER,
        51: Opcode.GET_ANEXT,
        52: Opcode.BEFORE_ASYNC_WITH,
        53: Opcode.BEFORE_WITH,
        54: Opcode.END_ASYNC_FOR,
        55: Opcode.CLEANUP_THROW,
        60: Opcode.STORE_SUBSCR,
        61: Opcode.DELETE_SUBSCR,
        68: Opcode.GET_ITER,
        69: Opcode.GET_YIELD_FROM_ITER,
        71: Opcode.LOAD_BUILD_CLASS,
        74: Opcode.LOAD_ASSERTION_ERROR,
        75: Opcode.RETURN_GENERATOR,
        83: Opcode.RETURN_VALUE,
        85: Opcode.SETUP_ANNOTATIONS,
        87: Opcode.LOAD_LOCALS,
        89: Opcode.POP_EXCEPT,
        90: Opcode.STORE_NAME_A,
        91: Opcode.DELETE_NAME_A,
        92: Opcode.UNPACK_SEQUENCE_A,
        93: Opcode.FOR_ITER_A,
        94: Opcode.UNPACK_EX_A,
        95: Opcode.STORE_ATTR_A,
        96: Opcode.DELETE_ATTR_A,
        97: Opcode.STORE_GLOBAL_A,
        98: Opcode.DELETE_GLOBAL_A,
        99: Opcode.SWAP_A,
        100: Opcode.LOAD_CONST_A,
        101: Opcode.LOAD_NAME_A,
        102: Opcode.BUILD_TUPLE_A,
        103: Opcode.BUILD_LIST_A,
        104: Opcode.BUILD_SET_A,
        105: Opcode.BUILD_MAP_A,
        106: Opcode.LOAD_ATTR_A,
        107: Opcode.COMPARE_OP_A,
        108: Opcode.IMPORT_NAME_A,
        109: Opcode.IMPORT_FROM_A,
        110: Opcode.JUMP_FORWARD_A,
        114: Opcode.POP_JUMP_IF_FALSE_A,
        115: Opcode.POP_JUMP_IF_TRUE_A,
        116: Opcode.LOAD_GLOBAL_A,
        117: Opcode.IS_OP_A,
        118: Opcode.CONTAINS_OP_A,
        119: Opcode.RERAISE_A,
        120: Opcode.COPY_A,
        121: Opcode.RETURN_CONST_A,
        122: Opcode.BINARY_OP_A,
        123: Opcode.SEND_A,
        124: Opcode.LOAD_FAST_A,
        125: Opcode.STORE_FAST_A,
        126: Opcode.DELETE_FAST_A,
        127: Opcode.LOAD_FAST_CHECK_A,
        128: Opcode.POP_JUMP_IF_NOT_NONE_A,
        129: Opcode.POP_JUMP_IF_NONE_A,
        130: Opcode.RAISE_VARARGS_A,
        131: Opcode.GET_AWAITABLE_A,
        132: Opcode.MAKE_FUNCTION_A,
        133: Opcode.BUILD_SLICE_A,
        134: Opcode.JUMP_BACKWARD_NO_INTERRUPT_A,
        135: Opcode.MAKE_CELL_A,
        136: Opcode.LOAD_CLOSURE_A,
        137: Opcode.LOAD_DEREF_A,
        138: Opcode.STORE_DEREF_A,
        139: Opcode.DELETE_DEREF_A,
        140: Opcode.JUMP_BACKWARD_A,
        141: Opcode.LOAD_SUPER_ATTR_A,
        142: Opcode.CALL_FUNCTION_EX_A,
        143: Opcode.LOAD_FAST_AND_CLEAR_A,
        144: Opcode.EXTENDED_ARG_A,
        145: Opcode.LIST_APPEND_A,
        146: Opcode.SET_ADD_A,
        147: Opcode.MAP_ADD_A,
        149: Opcode.COPY_FREE_VARS_A,
        150: Opcode.YIELD_VALUE_A,
        151: Opcode.RESUME_A,
        152: Opcode.MATCH_CLASS_A,
        155: Opcode.FORMAT_VALUE_A,
        156: Opcode.BUILD_CONST_KEY_MAP_A,
        157: Opcode.BUILD_STRING_A,
        162: Opcode.LIST_EXTEND_A,
        163: Opcode.SET_UPDATE_A,
        164: Opcode.DICT_MERGE_A,
        165: Opcode.DICT_UPDATE_A,
        171: Opcode.CALL_A,
        172: Opcode.KW_NAMES_A,
        173: Opcode.CALL_INTRINSIC_1_A,
        174: Opcode.CALL_INTRINSIC_2_A,
        175: Opcode.LOAD_FROM_DICT_OR_GLOBALS_A,
        176: Opcode.LOAD_FROM_DICT_OR_DEREF_A,
        237: Opcode.INSTRUMENTED_LOAD_SUPER_ATTR_A,
        238: Opcode.INSTRUMENTED_POP_JUMP_IF_NONE_A,
        239: Opcode.INSTRUMENTED_POP_JUMP_IF_NOT_NONE_A,
        240: Opcode.INSTRUMENTED_RESUME_A,
        241: Opcode.INSTRUMENTED_CALL_A,
        242: Opcode.INSTRUMENTED_RETURN_VALUE_A,
        243: Opcode.INSTRUMENTED_YIELD_VALUE_A,
        244: Opcode.INSTRUMENTED_CALL_FUNCTION_EX_A,
        245: Opcode.INSTRUMENTED_JUMP_FORWARD_A,
        246: Opcode.INSTRUMENTED_JUMP_BACKWARD_A,
        247: Opcode.INSTRUMENTED_RETURN_CONST_A,
        248: Opcode.INSTRUMENTED_FOR_ITER_A,
        249: Opcode.INSTRUMENTED_POP_JUMP_IF_FALSE_A,
        250: Opcode.INSTRUMENTED_POP_JUMP_IF_TRUE_A,
        251: Opcode.INSTRUMENTED_END_FOR_A,
        252: Opcode.INSTRUMENTED_END_SEND_A,
        253: Opcode.INSTRUMENTED_INSTRUCTION_A,
        254: Opcode.INSTRUMENTED_LINE_A,
    }
    return mapping.get(id_, Opcode.PYC_INVALID_OPCODE)

def python_3_13_map(id_: int):
    mapping = {
        0:   Opcode.CACHE,
        1:   Opcode.BEFORE_ASYNC_WITH,
        2:   Opcode.BEFORE_WITH,
        4:   Opcode.BINARY_SLICE,
        5:   Opcode.BINARY_SUBSCR,
        6:   Opcode.CHECK_EG_MATCH,
        7:   Opcode.CHECK_EXC_MATCH,
        8:   Opcode.CLEANUP_THROW,
        9:   Opcode.DELETE_SUBSCR,
        10:  Opcode.END_ASYNC_FOR,
        11:  Opcode.END_FOR,
        12:  Opcode.END_SEND,
        13:  Opcode.EXIT_INIT_CHECK,
        14:  Opcode.FORMAT_SIMPLE,
        15:  Opcode.FORMAT_WITH_SPEC,
        16:  Opcode.GET_AITER,
        17:  Opcode.RESERVED,
        18:  Opcode.GET_ANEXT,
        19:  Opcode.GET_ITER,
        20:  Opcode.GET_LEN,
        21:  Opcode.GET_YIELD_FROM_ITER,
        22:  Opcode.INTERPRETER_EXIT,
        23:  Opcode.LOAD_ASSERTION_ERROR,
        24:  Opcode.LOAD_BUILD_CLASS,
        25:  Opcode.LOAD_LOCALS,
        26:  Opcode.MAKE_FUNCTION,
        27:  Opcode.MATCH_KEYS,
        28:  Opcode.MATCH_MAPPING,
        29:  Opcode.MATCH_SEQUENCE,
        30:  Opcode.NOP,
        31:  Opcode.POP_EXCEPT,
        32:  Opcode.POP_TOP,
        33:  Opcode.PUSH_EXC_INFO,
        34:  Opcode.PUSH_NULL,
        35:  Opcode.RETURN_GENERATOR,
        36:  Opcode.RETURN_VALUE,
        37:  Opcode.SETUP_ANNOTATIONS,
        38:  Opcode.STORE_SLICE,
        39:  Opcode.STORE_SUBSCR,
        40:  Opcode.TO_BOOL,
        41:  Opcode.UNARY_INVERT,
        42:  Opcode.UNARY_NEGATIVE,
        43:  Opcode.UNARY_NOT,
        44:  Opcode.WITH_EXCEPT_START,
        45:  Opcode.BINARY_OP_A,
        46:  Opcode.BUILD_CONST_KEY_MAP_A,
        47:  Opcode.BUILD_LIST_A,
        48:  Opcode.BUILD_MAP_A,
        49:  Opcode.BUILD_SET_A,
        50:  Opcode.BUILD_SLICE_A,
        51:  Opcode.BUILD_STRING_A,
        52:  Opcode.BUILD_TUPLE_A,
        53:  Opcode.CALL_A,
        54:  Opcode.CALL_FUNCTION_EX_A,
        55:  Opcode.CALL_INTRINSIC_1_A,
        56:  Opcode.CALL_INTRINSIC_2_A,
        57:  Opcode.CALL_KW_A,
        58:  Opcode.COMPARE_OP_A,
        59:  Opcode.CONTAINS_OP_A,
        60:  Opcode.CONVERT_VALUE_A,
        61:  Opcode.COPY_A,
        62:  Opcode.COPY_FREE_VARS_A,
        63:  Opcode.DELETE_ATTR_A,
        64:  Opcode.DELETE_DEREF_A,
        65:  Opcode.DELETE_FAST_A,
        66:  Opcode.DELETE_GLOBAL_A,
        67:  Opcode.DELETE_NAME_A,
        68:  Opcode.DICT_MERGE_A,
        69:  Opcode.DICT_UPDATE_A,
        70:  Opcode.ENTER_EXECUTOR_A,
        71:  Opcode.EXTENDED_ARG_A,
        72:  Opcode.FOR_ITER_A,
        73:  Opcode.GET_AWAITABLE_A,
        74:  Opcode.IMPORT_FROM_A,
        75:  Opcode.IMPORT_NAME_A,
        76:  Opcode.IS_OP_A,
        77:  Opcode.JUMP_BACKWARD_A,
        78:  Opcode.JUMP_BACKWARD_NO_INTERRUPT_A,
        79:  Opcode.JUMP_FORWARD_A,
        80:  Opcode.LIST_APPEND_A,
        81:  Opcode.LIST_EXTEND_A,
        82:  Opcode.LOAD_ATTR_A,
        83:  Opcode.LOAD_CONST_A,
        84:  Opcode.LOAD_DEREF_A,
        85:  Opcode.LOAD_FAST_A,
        86:  Opcode.LOAD_FAST_AND_CLEAR_A,
        87:  Opcode.LOAD_FAST_CHECK_A,
        88:  Opcode.LOAD_FAST_LOAD_FAST_A,
        89:  Opcode.LOAD_FROM_DICT_OR_DEREF_A,
        90:  Opcode.LOAD_FROM_DICT_OR_GLOBALS_A,
        91:  Opcode.LOAD_GLOBAL_A,
        92:  Opcode.LOAD_NAME_A,
        93:  Opcode.LOAD_SUPER_ATTR_A,
        94:  Opcode.MAKE_CELL_A,
        95:  Opcode.MAP_ADD_A,
        96:  Opcode.MATCH_CLASS_A,
        97:  Opcode.POP_JUMP_IF_FALSE_A,
        98:  Opcode.POP_JUMP_IF_NONE_A,
        99:  Opcode.POP_JUMP_IF_NOT_NONE_A,
        100: Opcode.POP_JUMP_IF_TRUE_A,
        101: Opcode.RAISE_VARARGS_A,
        102: Opcode.RERAISE_A,
        103: Opcode.RETURN_CONST_A,
        104: Opcode.SEND_A,
        105: Opcode.SET_ADD_A,
        106: Opcode.SET_FUNCTION_ATTRIBUTE_A,
        107: Opcode.SET_UPDATE_A,
        108: Opcode.STORE_ATTR_A,
        109: Opcode.STORE_DEREF_A,
        110: Opcode.STORE_FAST_A,
        111: Opcode.STORE_FAST_LOAD_FAST_A,
        112: Opcode.STORE_FAST_STORE_FAST_A,
        113: Opcode.STORE_GLOBAL_A,
        114: Opcode.STORE_NAME_A,
        115: Opcode.SWAP_A,
        116: Opcode.UNPACK_EX_A,
        117: Opcode.UNPACK_SEQUENCE_A,
        118: Opcode.YIELD_VALUE_A,
        149: Opcode.RESUME_A,
        236: Opcode.INSTRUMENTED_RESUME_A,
        237: Opcode.INSTRUMENTED_END_FOR_A,
        238: Opcode.INSTRUMENTED_END_SEND_A,
        239: Opcode.INSTRUMENTED_RETURN_VALUE_A,
        240: Opcode.INSTRUMENTED_RETURN_CONST_A,
        241: Opcode.INSTRUMENTED_YIELD_VALUE_A,
        242: Opcode.INSTRUMENTED_LOAD_SUPER_ATTR_A,
        243: Opcode.INSTRUMENTED_FOR_ITER_A,
        244: Opcode.INSTRUMENTED_CALL_A,
        245: Opcode.INSTRUMENTED_CALL_KW_A,
        246: Opcode.INSTRUMENTED_CALL_FUNCTION_EX_A,
        247: Opcode.INSTRUMENTED_INSTRUCTION_A,
        248: Opcode.INSTRUMENTED_JUMP_FORWARD_A,
        249: Opcode.INSTRUMENTED_JUMP_BACKWARD_A,
        250: Opcode.INSTRUMENTED_POP_JUMP_IF_TRUE_A,
        251: Opcode.INSTRUMENTED_POP_JUMP_IF_FALSE_A,
        252: Opcode.INSTRUMENTED_POP_JUMP_IF_NONE_A,
        253: Opcode.INSTRUMENTED_POP_JUMP_IF_NOT_NONE_A,
        254: Opcode.INSTRUMENTED_LINE_A,
    }

    return mapping.get(id_)

def python_3_14_map(id_: int):
    mapping = {
        0: CACHE,
        1: POP_TOP,
        2: PUSH_NULL,
        3: INTERPRETER_EXIT,
        4: END_FOR,
        5: END_SEND,
        9: NOP,
        11: UNARY_NEGATIVE,
        12: UNARY_NOT,
        15: UNARY_INVERT,
        17: RESERVED,
        25: BINARY_SUBSCR,
        26: BINARY_SLICE,
        27: STORE_SLICE,
        30: GET_LEN,
        31: MATCH_MAPPING,
        32: MATCH_SEQUENCE,
        33: MATCH_KEYS,
        35: PUSH_EXC_INFO,
        36: CHECK_EXC_MATCH,
        37: CHECK_EG_MATCH,
        49: WITH_EXCEPT_START,
        50: GET_AITER,
        51: GET_ANEXT,
        52: BEFORE_ASYNC_WITH,
        53: BEFORE_WITH,
        54: END_ASYNC_FOR,
        55: CLEANUP_THROW,
        60: STORE_SUBSCR,
        61: DELETE_SUBSCR,
        68: GET_ITER,
        69: GET_YIELD_FROM_ITER,
        71: LOAD_BUILD_CLASS,
        74: LOAD_ASSERTION_ERROR,
        75: RETURN_GENERATOR,
        83: RETURN_VALUE,
        85: SETUP_ANNOTATIONS,
        87: LOAD_LOCALS,
        89: POP_EXCEPT,
        90: STORE_NAME,
        91: DELETE_NAME,
        92: UNPACK_SEQUENCE,
        93: FOR_ITER,
        94: UNPACK_EX,
        95: STORE_ATTR,
        96: DELETE_ATTR,
        97: STORE_GLOBAL,
        98: DELETE_GLOBAL,
        99: SWAP,
        100: LOAD_CONST,
        101: LOAD_NAME,
        102: BUILD_TUPLE,
        103: BUILD_LIST,
        104: BUILD_SET,
        105: BUILD_MAP,
        106: LOAD_ATTR,
        107: COMPARE_OP,
        108: IMPORT_NAME,
        109: IMPORT_FROM,
        110: JUMP_FORWARD,
        114: POP_JUMP_IF_FALSE,
        115: POP_JUMP_IF_TRUE,
        116: LOAD_GLOBAL,
        117: IS_OP,
        118: CONTAINS_OP,
        119: RERAISE,
        120: COPY,
        121: RETURN_CONST,
        122: BINARY_OP,
        123: SEND,
        124: LOAD_FAST,
        125: STORE_FAST,
        126: DELETE_FAST,
        127: LOAD_FAST_CHECK,
        128: POP_JUMP_IF_NOT_NONE,
        129: POP_JUMP_IF_NONE,
        130: RAISE_VARARGS,
        131: GET_AWAITABLE,
        132: MAKE_FUNCTION,
        133: BUILD_SLICE,
        134: JUMP_BACKWARD_NO_INTERRUPT,
        135: MAKE_CELL,
        136: LOAD_CLOSURE,
        137: LOAD_DEREF,
        138: STORE_DEREF,
        139: DELETE_DEREF,
        140: JUMP_BACKWARD,
        141: LOAD_SUPER_ATTR,
        142: CALL_FUNCTION_EX,
        143: LOAD_FAST_AND_CLEAR,
        144: EXTENDED_ARG,
        145: LIST_APPEND,
        146: SET_ADD,
        147: MAP_ADD,
        149: COPY_FREE_VARS,
        150: YIELD_VALUE,
        151: RESUME,
        152: MATCH_CLASS,
        155: FORMAT_VALUE,
        156: BUILD_CONST_KEY_MAP,
        157: BUILD_STRING,
        162: LIST_EXTEND,
        163: SET_UPDATE,
        164: DICT_MERGE,
        165: DICT_UPDATE,
        171: CALL,
        172: KW_NAMES,
        173: CALL_INTRINSIC_1,
        174: CALL_INTRINSIC_2,
        175: LOAD_FROM_DICT_OR_GLOBALS,
        176: LOAD_FROM_DICT_OR_DEREF,
        237: INSTRUMENTED_LOAD_SUPER_ATTR,
        238: INSTRUMENTED_POP_JUMP_IF_NONE,
        239: INSTRUMENTED_POP_JUMP_IF_NOT_NONE,
        240: INSTRUMENTED_RESUME,
        241: INSTRUMENTED_CALL,
        242: INSTRUMENTED_RETURN_VALUE,
        243: INSTRUMENTED_YIELD_VALUE,
        244: INSTRUMENTED_CALL_FUNCTION_EX,
        245: INSTRUMENTED_JUMP_FORWARD,
        246: INSTRUMENTED_JUMP_BACKWARD,
        247: INSTRUMENTED_RETURN_CONST,
        248: INSTRUMENTED_FOR_ITER,
        249: INSTRUMENTED_POP_JUMP_IF_FALSE,
        250: INSTRUMENTED_POP_JUMP_IF_TRUE,
        251: INSTRUMENTED_END_FOR,
        252: INSTRUMENTED_END_SEND,
        253: INSTRUMENTED_INSTRUCTION,
        254: INSTRUMENTED_LINE,
        256: SETUP_FINALLY,
        257: SETUP_CLEANUP,
        258: SETUP_WITH,
        259: POP_BLOCK,
        260: JUMP,
        261: JUMP_NO_INTERRUPT,
        262: LOAD_METHOD,
        263: LOAD_SUPER_METHOD,
        264: LOAD_ZERO_SUPER_METHOD,
        265: LOAD_ZERO_SUPER_ATTR,
        266: STORE_FAST_MAYBE_NULL,    
    }
def byte_to_opcode(maj: int, min_: int, opcode: int) -> int:
    if maj == 1 and min_ == 0:
        return python_1_0_map(opcode)
    elif maj == 3 and min_ >= 12:
        return python_3_12_map(opcode)
    
    # Placeholder for other versions
    return python_1_0_map(opcode)

def bc_next(source: 'PycBuffer', mod: 'PycModule') -> Tuple[int, int, int]:
    opcode_byte = source.get_byte()
    opcode = byte_to_opcode(mod.major_ver, mod.minor_ver, opcode_byte)
    operand = 0
    pos_inc = 0
    
    if mod.major_ver == 3 and mod.minor_ver >= 11:
        # Python 3.11+ uses fixed 2-byte instructions (opcode + operand)
        # Operand is always present, though sometimes unused
        operand = source.get_byte()
        pos_inc = 2
        
        if opcode == Opcode.EXTENDED_ARG_A:
            # Handle recursive extended args
            next_op_byte = source.get_byte()
            next_operand = source.get_byte()
            operand = (operand << 8) | next_operand
            opcode = byte_to_opcode(mod.major_ver, mod.minor_ver, next_op_byte)
            pos_inc += 2
            
            # Allow for multiple extensions
            while opcode == Opcode.EXTENDED_ARG_A:
                next_op_byte = source.get_byte()
                next_operand = source.get_byte()
                operand = (operand << 8) | next_operand
                opcode = byte_to_opcode(mod.major_ver, mod.minor_ver, next_op_byte)
                pos_inc += 2
                
    elif mod.ver_compare(3, 6) >= 0:
        operand = source.get_byte()
        pos_inc = 2
        if opcode == Opcode.EXTENDED_ARG_A:
            next_op_byte = source.get_byte()
            opcode = byte_to_opcode(mod.major_ver, mod.minor_ver, next_op_byte)
            operand = (operand << 8) | source.get_byte()
            pos_inc += 2
    else:
        operand = 0
        pos_inc = 1
        if opcode == Opcode.EXTENDED_ARG_A:
            operand = source.get16() << 16
            opcode_byte = source.get_byte()
            opcode = byte_to_opcode(mod.major_ver, mod.minor_ver, opcode_byte)
            pos_inc += 3
            
        if opcode >= Opcode.PYC_HAVE_ARG:
            operand |= source.get16()
            pos_inc += 2

    return opcode, operand, pos_inc

def bc_disasm(pyc_output: TextIO, code: 'PycCode', mod: 'PycModule', indent: int, flags: int):
# Static string tables defined in C++
    cmp_strings = [
        "<", "<=", "==", "!=", ">", ">=", "in", "not in", "is", "is not",
        "<EXCEPTION MATCH>", "<BAD>"
    ]
    
    binop_strings = [
        "+", "&", "//", "<<", "@", "*", "%", "|", "**", ">>", "-", "/", "^",
        "+=", "&=", "//=", "<<=", "@=", "*=", "%=", "|=", "**=", ">>=", "-=", "/=", "^="
    ]
    
    intrinsic1_names = [
        "INTRINSIC_1_INVALID", "INTRINSIC_PRINT", "INTRINSIC_IMPORT_STAR",
        "INTRINSIC_STOPITERATION_ERROR", "INTRINSIC_ASYNC_GEN_WRAP",
        "INTRINSIC_UNARY_POSITIVE", "INTRINSIC_LIST_TO_TUPLE", "INTRINSIC_TYPEVAR",
        "INTRINSIC_PARAMSPEC", "INTRINSIC_TYPEVARTUPLE",
        "INTRINSIC_SUBSCRIPT_GENERIC", "INTRINSIC_TYPEALIAS"
    ]
    
    intrinsic2_names = [
        "INTRINSIC_2_INVALID", "INTRINSIC_PREP_RERAISE_STAR",
        "INTRINSIC_TYPEVAR_WITH_BOUND", "INTRINSIC_TYPEVAR_WITH_CONSTRAINTS",
        "INTRINSIC_SET_FUNCTION_TYPE_PARAMS", "INTRINSIC_SET_TYPEPARAM_DEFAULT"
    ]
    
    format_value_names = [
        "FVC_NONE", "FVC_STR", "FVC_REPR", "FVC_ASCII"
    ]

    # Initialize PycBuffer from code object
    # Assuming code.code is the raw PycString or bytes
    if hasattr(code.code, 'value'):
        from data import PycBuffer
        source = PycBuffer(code.code.value)
    else:
        # Fallback if code.code is raw bytes
        from data import PycBuffer
        source = PycBuffer(code.code)

    opcode = 0
    operand = 0
    pos = 0
    
    while not source.at_eof():
        start_pos = pos
        opcode_val, operand, pos_inc = bc_next(source, mod)
        opcode = Opcode(opcode_val)
        pos += pos_inc
        
        # CACHE skipping logic
        if opcode == Opcode.CACHE and (flags & DISASM_SHOW_CACHES) == 0:
            continue

        # Indentation
        pyc_output.write("    " * indent)
        
        # Print Offset and Opcode Name
        # Using .name if available, otherwise int value
        op_name = opcode.name if hasattr(opcode, 'name') else str(opcode_val)
        formatted_print(pyc_output, "%-7d %-30s  ", start_pos, op_name)

        if opcode >= Opcode.PYC_HAVE_ARG:
            # --- Switch equivalent logic ---
            
            if opcode in (Opcode.LOAD_CONST_A, Opcode.RESERVE_FAST_A, Opcode.KW_NAMES_A,
                          Opcode.RETURN_CONST_A, Opcode.INSTRUMENTED_RETURN_CONST_A):
                try:
                    constParam = code.getConst(operand)
                    formatted_print(pyc_output, "%d: ", operand)
                    # print_const equivalent:
                    constParam.print(pyc_output, mod)
                except (IndexError, AttributeError):
                    formatted_print(pyc_output, "%d <INVALID>", operand)

            elif opcode == Opcode.LOAD_GLOBAL_A:
                try:
                    if mod.ver_compare(3, 11) >= 0:
                        name_val = code.getName(operand >> 1).value.decode('utf-8', 'replace')
                        if operand & 1:
                            formatted_print(pyc_output, "%d: NULL + %s", operand, name_val)
                        else:
                            formatted_print(pyc_output, "%d: %s", operand, name_val)
                    else:
                        name_val = code.getName(operand).value.decode('utf-8', 'replace')
                        formatted_print(pyc_output, "%d: %s", operand, name_val)
                except (IndexError, AttributeError):
                    formatted_print(pyc_output, "%d <INVALID>", operand)

            elif opcode in (Opcode.DELETE_ATTR_A, Opcode.DELETE_GLOBAL_A, Opcode.DELETE_NAME_A,
                            Opcode.IMPORT_FROM_A, Opcode.IMPORT_NAME_A, Opcode.LOAD_ATTR_A,
                            Opcode.LOAD_LOCAL_A, Opcode.LOAD_NAME_A, Opcode.STORE_ATTR_A,
                            Opcode.STORE_GLOBAL_A, Opcode.STORE_NAME_A, Opcode.STORE_ANNOTATION_A,
                            Opcode.LOAD_METHOD_A, Opcode.LOAD_FROM_DICT_OR_GLOBALS_A):
                try:
                    arg = operand
                    if opcode == Opcode.LOAD_ATTR_A and mod.ver_compare(3, 12) >= 0:
                        arg >>= 1
                    
                    name_val = code.getName(arg).value.decode('utf-8', 'replace')
                    formatted_print(pyc_output, "%d: %s", operand, name_val)
                except (IndexError, AttributeError):
                    formatted_print(pyc_output, "%d <INVALID>", operand)

            elif opcode in (Opcode.LOAD_SUPER_ATTR_A, Opcode.INSTRUMENTED_LOAD_SUPER_ATTR_A):
                try:
                    name_val = code.getName(operand >> 2).value.decode('utf-8', 'replace')
                    formatted_print(pyc_output, "%d: %s", operand, name_val)
                except (IndexError, AttributeError):
                    formatted_print(pyc_output, "%d <INVALID>", operand)

            elif opcode in (Opcode.DELETE_FAST_A, Opcode.LOAD_FAST_A, Opcode.STORE_FAST_A,
                            Opcode.LOAD_FAST_CHECK_A, Opcode.LOAD_FAST_AND_CLEAR_A):
                try:
                    local_val = code.getLocal(operand).value.decode('utf-8', 'replace')
                    formatted_print(pyc_output, "%d: %s", operand, local_val)
                except (IndexError, AttributeError):
                    formatted_print(pyc_output, "%d <INVALID>", operand)

            elif opcode in (Opcode.LOAD_FAST_LOAD_FAST_A, Opcode.STORE_FAST_LOAD_FAST_A,
                            Opcode.STORE_FAST_STORE_FAST_A):
                try:
                    val1 = code.getLocal(operand >> 4).value.decode('utf-8', 'replace')
                    val2 = code.getLocal(operand & 0xF).value.decode('utf-8', 'replace')
                    formatted_print(pyc_output, "%d: %s, %s", operand, val1, val2)
                except (IndexError, AttributeError):
                    formatted_print(pyc_output, "%d <INVALID>", operand)

            elif opcode in (Opcode.LOAD_CLOSURE_A, Opcode.LOAD_DEREF_A, Opcode.STORE_DEREF_A,
                            Opcode.DELETE_DEREF_A, Opcode.MAKE_CELL_A, Opcode.CALL_FINALLY_A,
                            Opcode.LOAD_FROM_DICT_OR_DEREF_A):
                try:
                    cell_val = code.getCellVar(mod, operand).value.decode('utf-8', 'replace')
                    formatted_print(pyc_output, "%d: %s", operand, cell_val)
                except (IndexError, AttributeError):
                    formatted_print(pyc_output, "%d <INVALID>", operand)

            elif opcode in (Opcode.JUMP_FORWARD_A, Opcode.JUMP_IF_FALSE_A, Opcode.JUMP_IF_TRUE_A,
                            Opcode.SETUP_LOOP_A, Opcode.SETUP_FINALLY_A, Opcode.SETUP_EXCEPT_A,
                            Opcode.FOR_LOOP_A, Opcode.FOR_ITER_A, Opcode.SETUP_WITH_A,
                            Opcode.SETUP_ASYNC_WITH_A, Opcode.POP_JUMP_FORWARD_IF_FALSE_A,
                            Opcode.POP_JUMP_FORWARD_IF_TRUE_A, Opcode.SEND_A,
                            Opcode.POP_JUMP_FORWARD_IF_NOT_NONE_A, Opcode.POP_JUMP_FORWARD_IF_NONE_A,
                            Opcode.POP_JUMP_IF_NOT_NONE_A, Opcode.POP_JUMP_IF_NONE_A,
                            Opcode.INSTRUMENTED_POP_JUMP_IF_NOT_NONE_A,
                            Opcode.INSTRUMENTED_POP_JUMP_IF_NONE_A, Opcode.INSTRUMENTED_JUMP_FORWARD_A,
                            Opcode.INSTRUMENTED_FOR_ITER_A, Opcode.INSTRUMENTED_POP_JUMP_IF_FALSE_A,
                            Opcode.INSTRUMENTED_POP_JUMP_IF_TRUE_A):
                offs = operand
                if mod.ver_compare(3, 10) >= 0:
                    offs *= 2 # sizeof(uint16_t)
                formatted_print(pyc_output, "%d (to %d)", operand, pos + offs)

            elif opcode in (Opcode.JUMP_BACKWARD_NO_INTERRUPT_A, Opcode.JUMP_BACKWARD_A,
                            Opcode.POP_JUMP_BACKWARD_IF_NOT_NONE_A, Opcode.POP_JUMP_BACKWARD_IF_NONE_A,
                            Opcode.POP_JUMP_BACKWARD_IF_FALSE_A, Opcode.POP_JUMP_BACKWARD_IF_TRUE_A,
                            Opcode.INSTRUMENTED_JUMP_BACKWARD_A):
                offs = operand * 2 # sizeof(uint16_t)
                formatted_print(pyc_output, "%d (to %d)", operand, pos - offs)

            elif opcode in (Opcode.POP_JUMP_IF_FALSE_A, Opcode.POP_JUMP_IF_TRUE_A,
                            Opcode.JUMP_IF_FALSE_OR_POP_A, Opcode.JUMP_IF_TRUE_OR_POP_A,
                            Opcode.JUMP_ABSOLUTE_A, Opcode.JUMP_IF_NOT_EXC_MATCH_A):
                if mod.ver_compare(3, 12) >= 0:
                    offs = operand * 2
                    formatted_print(pyc_output, "%d (to %d)", operand, pos + offs)
                elif mod.ver_compare(3, 10) >= 0:
                    formatted_print(pyc_output, "%d (to %d)", operand, operand * 2)
                else:
                    formatted_print(pyc_output, "%d", operand)

            elif opcode == Opcode.COMPARE_OP_A:
                arg = operand
                if mod.ver_compare(3, 12) == 0:
                    arg >>= 4
                elif mod.ver_compare(3, 13) >= 0:
                    arg >>= 5
                
                if arg < len(cmp_strings):
                    formatted_print(pyc_output, "%d (%s)", operand, cmp_strings[arg])
                else:
                    formatted_print(pyc_output, "%d (UNKNOWN)", operand)

            elif opcode == Opcode.BINARY_OP_A:
                if operand < len(binop_strings):
                    formatted_print(pyc_output, "%d (%s)", operand, binop_strings[operand])
                else:
                    formatted_print(pyc_output, "%d (UNKNOWN)", operand)

            elif opcode == Opcode.IS_OP_A:
                op_str = "is" if operand == 0 else ("is not" if operand == 1 else "UNKNOWN")
                formatted_print(pyc_output, "%d (%s)", operand, op_str)

            elif opcode == Opcode.CONTAINS_OP_A:
                op_str = "in" if operand == 0 else ("not in" if operand == 1 else "UNKNOWN")
                formatted_print(pyc_output, "%d (%s)", operand, op_str)

            elif opcode == Opcode.CALL_INTRINSIC_1_A:
                if operand < len(intrinsic1_names):
                    formatted_print(pyc_output, "%d (%s)", operand, intrinsic1_names[operand])
                else:
                    formatted_print(pyc_output, "%d (UNKNOWN)", operand)

            elif opcode == Opcode.CALL_INTRINSIC_2_A:
                if operand < len(intrinsic2_names):
                    formatted_print(pyc_output, "%d (%s)", operand, intrinsic2_names[operand])
                else:
                    formatted_print(pyc_output, "%d (UNKNOWN)", operand)

            elif opcode == Opcode.FORMAT_VALUE_A:
                conv = operand & 0x03
                flag = " | FVS_HAVE_SPEC" if (operand & 0x04) else ""
                if conv < len(format_value_names):
                    formatted_print(pyc_output, "%d (%s%s)", operand, format_value_names[conv], flag)
                else:
                    formatted_print(pyc_output, "%d (UNKNOWN)", operand)

            elif opcode == Opcode.CONVERT_VALUE_A:
                if operand < len(format_value_names):
                    formatted_print(pyc_output, "%d (%s)", operand, format_value_names[operand])
                else:
                    formatted_print(pyc_output, "%d (UNKNOWN)", operand)

            elif opcode == Opcode.SET_FUNCTION_ATTRIBUTE_A:
                if operand == 0x01:
                    formatted_print(pyc_output, "%d (MAKE_FUNCTION_DEFAULTS)", operand)
                elif operand == 0x02:
                    formatted_print(pyc_output, "%d (MAKE_FUNCTION_KWDEFAULTS)", operand)
                elif operand == 0x04:
                    formatted_print(pyc_output, "%d (MAKE_FUNCTION_ANNOTATIONS)", operand)
                elif operand == 0x08:
                    formatted_print(pyc_output, "%d (MAKE_FUNCTION_CLOSURE)", operand)
                else:
                    formatted_print(pyc_output, "%d (UNKNOWN)", operand)

            else:
                formatted_print(pyc_output, "%d", operand)

        pyc_output.write("\n")