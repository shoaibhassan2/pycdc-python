import enum
from typing import List, Optional, Any, Union, Tuple
import bytecode  # Assumed to be the converted bytecode.py module

class ASTNodeType(enum.IntEnum):
    NODE_INVALID = 0
    NODE_NODELIST = 1
    NODE_OBJECT = 2
    NODE_UNARY = 3
    NODE_BINARY = 4
    NODE_COMPARE = 5
    NODE_SLICE = 6
    NODE_STORE = 7
    NODE_RETURN = 8
    NODE_NAME = 9
    NODE_DELETE = 10
    NODE_FUNCTION = 11
    NODE_CLASS = 12
    NODE_CALL = 13
    NODE_IMPORT = 14
    NODE_TUPLE = 15
    NODE_LIST = 16
    NODE_SET = 17
    NODE_MAP = 18
    NODE_SUBSCR = 19
    NODE_PRINT = 20
    NODE_CONVERT = 21
    NODE_KEYWORD = 22
    NODE_RAISE = 23
    NODE_EXEC = 24
    NODE_BLOCK = 25
    NODE_COMPREHENSION = 26
    NODE_LOADBUILDCLASS = 27
    NODE_AWAITABLE = 28
    NODE_FORMATTEDVALUE = 29
    NODE_JOINEDSTR = 30
    NODE_CONST_MAP = 31
    NODE_ANNOTATED_VAR = 32
    NODE_CHAINSTORE = 33
    NODE_TERNARY = 34
    NODE_KW_NAMES_MAP = 35
    NODE_LOCALS = 36

class ASTNode:
    def __init__(self, type_: int = ASTNodeType.NODE_INVALID):
        self.m_type = type_
        self.m_processed = False
    
    @property
    def type(self) -> int:
        return self.m_type
        
    @property
    def processed(self) -> bool:
        return self.m_processed
    
    def set_processed(self):
        self.m_processed = True

class ASTNodeList(ASTNode):
    def __init__(self, nodes: List['ASTNode'], type_: int = ASTNodeType.NODE_NODELIST):
        super().__init__(type_)
        self.m_nodes = nodes

    @property
    def nodes(self) -> List['ASTNode']:
        return self.m_nodes

    def remove_first(self):
        if self.m_nodes:
            self.m_nodes.pop(0)

    def remove_last(self):
        if self.m_nodes:
            self.m_nodes.pop()

    def append(self, node: 'ASTNode'):
        self.m_nodes.append(node)

class ASTChainStore(ASTNodeList):
    def __init__(self, nodes: List['ASTNode'], src: 'ASTNode'):
        super().__init__(nodes, ASTNodeType.NODE_CHAINSTORE)
        self.m_src = src

    @property
    def src(self) -> 'ASTNode':
        return self.m_src

class ASTObject(ASTNode):
    def __init__(self, obj: Any): # obj is PycObject
        super().__init__(ASTNodeType.NODE_OBJECT)
        self.m_obj = obj

    @property
    def object(self) -> Any:
        return self.m_obj

class ASTUnary(ASTNode):
    class UnOp(enum.IntEnum):
        UN_POSITIVE = 0
        UN_NEGATIVE = 1
        UN_INVERT = 2
        UN_NOT = 3

    def __init__(self, operand: 'ASTNode', op: int):
        super().__init__(ASTNodeType.NODE_UNARY)
        self.m_op = op
        self.m_operand = operand

    @property
    def operand(self) -> 'ASTNode':
        return self.m_operand

    @property
    def op(self) -> int:
        return self.m_op

    def op_str(self) -> str:
        s_op_strings = ["+", "-", "~", "not "]
        if 0 <= self.m_op < len(s_op_strings):
            return s_op_strings[self.m_op]
        return "<INVALID>"

class ASTBinary(ASTNode):
    class BinOp(enum.IntEnum):
        BIN_ATTR = 0
        BIN_POWER = 1
        BIN_MULTIPLY = 2
        BIN_DIVIDE = 3
        BIN_FLOOR_DIVIDE = 4
        BIN_MODULO = 5
        BIN_ADD = 6
        BIN_SUBTRACT = 7
        BIN_LSHIFT = 8
        BIN_RSHIFT = 9
        BIN_AND = 10
        BIN_XOR = 11
        BIN_OR = 12
        BIN_LOG_AND = 13
        BIN_LOG_OR = 14
        BIN_MAT_MULTIPLY = 15
        # Inplace operations
        BIN_IP_ADD = 16
        BIN_IP_SUBTRACT = 17
        BIN_IP_MULTIPLY = 18
        BIN_IP_DIVIDE = 19
        BIN_IP_MODULO = 20
        BIN_IP_POWER = 21
        BIN_IP_LSHIFT = 22
        BIN_IP_RSHIFT = 23
        BIN_IP_AND = 24
        BIN_IP_XOR = 25
        BIN_IP_OR = 26
        BIN_IP_FLOOR_DIVIDE = 27
        BIN_IP_MAT_MULTIPLY = 28
        BIN_INVALID = 29

    def __init__(self, left: 'ASTNode', right: 'ASTNode', op: int, type_: int = ASTNodeType.NODE_BINARY):
        super().__init__(type_)
        self.m_op = op
        self.m_left = left
        self.m_right = right

    @property
    def left(self) -> 'ASTNode':
        return self.m_left

    @property
    def right(self) -> 'ASTNode':
        return self.m_right
    
    @property
    def op(self) -> int:
        return self.m_op

    def is_inplace(self) -> bool:
        return self.m_op >= self.BinOp.BIN_IP_ADD

    def op_str(self) -> str:
        s_op_strings = [
            ".", " ** ", " * ", " / ", " // ", " % ", " + ", " - ",
            " << ", " >> ", " & ", " ^ ", " | ", " and ", " or ", " @ ",
            " += ", " -= ", " *= ", " /= ", " %= ", " **= ", " <<= ",
            " >>= ", " &= ", " ^= ", " |= ", " //= ", " @= ", " <INVALID> "
        ]
        if 0 <= self.m_op < len(s_op_strings):
            return s_op_strings[self.m_op]
        return "<INVALID>"

    @staticmethod
    def from_opcode(opcode: int) -> 'ASTBinary.BinOp':
        mapping = {
            bytecode.BINARY_ADD: ASTBinary.BinOp.BIN_ADD,
            bytecode.BINARY_AND: ASTBinary.BinOp.BIN_AND,
            bytecode.BINARY_DIVIDE: ASTBinary.BinOp.BIN_DIVIDE,
            bytecode.BINARY_FLOOR_DIVIDE: ASTBinary.BinOp.BIN_FLOOR_DIVIDE,
            bytecode.BINARY_LSHIFT: ASTBinary.BinOp.BIN_LSHIFT,
            bytecode.BINARY_MODULO: ASTBinary.BinOp.BIN_MODULO,
            bytecode.BINARY_MULTIPLY: ASTBinary.BinOp.BIN_MULTIPLY,
            bytecode.BINARY_OR: ASTBinary.BinOp.BIN_OR,
            bytecode.BINARY_POWER: ASTBinary.BinOp.BIN_POWER,
            bytecode.BINARY_RSHIFT: ASTBinary.BinOp.BIN_RSHIFT,
            bytecode.BINARY_SUBTRACT: ASTBinary.BinOp.BIN_SUBTRACT,
            bytecode.BINARY_TRUE_DIVIDE: ASTBinary.BinOp.BIN_DIVIDE,
            bytecode.BINARY_XOR: ASTBinary.BinOp.BIN_XOR,
            bytecode.BINARY_MATRIX_MULTIPLY: ASTBinary.BinOp.BIN_MAT_MULTIPLY,
            bytecode.INPLACE_ADD: ASTBinary.BinOp.BIN_IP_ADD,
            bytecode.INPLACE_AND: ASTBinary.BinOp.BIN_IP_AND,
            bytecode.INPLACE_DIVIDE: ASTBinary.BinOp.BIN_IP_DIVIDE,
            bytecode.INPLACE_FLOOR_DIVIDE: ASTBinary.BinOp.BIN_IP_FLOOR_DIVIDE,
            bytecode.INPLACE_LSHIFT: ASTBinary.BinOp.BIN_IP_LSHIFT,
            bytecode.INPLACE_MODULO: ASTBinary.BinOp.BIN_IP_MODULO,
            bytecode.INPLACE_MULTIPLY: ASTBinary.BinOp.BIN_IP_MULTIPLY,
            bytecode.INPLACE_OR: ASTBinary.BinOp.BIN_IP_OR,
            bytecode.INPLACE_POWER: ASTBinary.BinOp.BIN_IP_POWER,
            bytecode.INPLACE_RSHIFT: ASTBinary.BinOp.BIN_IP_RSHIFT,
            bytecode.INPLACE_SUBTRACT: ASTBinary.BinOp.BIN_IP_SUBTRACT,
            bytecode.INPLACE_TRUE_DIVIDE: ASTBinary.BinOp.BIN_IP_DIVIDE,
            bytecode.INPLACE_XOR: ASTBinary.BinOp.BIN_IP_XOR,
            bytecode.INPLACE_MATRIX_MULTIPLY: ASTBinary.BinOp.BIN_IP_MAT_MULTIPLY,
        }
        return mapping.get(opcode, ASTBinary.BinOp.BIN_INVALID)

    @staticmethod
    def from_binary_op(operand: int) -> 'ASTBinary.BinOp':
        # Mapping from numeric operand in Py3.11+ BINARY_OP
        mapping = {
            0: ASTBinary.BinOp.BIN_ADD,
            1: ASTBinary.BinOp.BIN_AND,
            2: ASTBinary.BinOp.BIN_FLOOR_DIVIDE,
            3: ASTBinary.BinOp.BIN_LSHIFT,
            4: ASTBinary.BinOp.BIN_MAT_MULTIPLY,
            5: ASTBinary.BinOp.BIN_MULTIPLY,
            6: ASTBinary.BinOp.BIN_MODULO,
            7: ASTBinary.BinOp.BIN_OR,
            8: ASTBinary.BinOp.BIN_POWER,
            9: ASTBinary.BinOp.BIN_RSHIFT,
            10: ASTBinary.BinOp.BIN_SUBTRACT,
            11: ASTBinary.BinOp.BIN_DIVIDE,
            12: ASTBinary.BinOp.BIN_XOR,
            13: ASTBinary.BinOp.BIN_IP_ADD,
            14: ASTBinary.BinOp.BIN_IP_AND,
            15: ASTBinary.BinOp.BIN_IP_FLOOR_DIVIDE,
            16: ASTBinary.BinOp.BIN_IP_LSHIFT,
            17: ASTBinary.BinOp.BIN_MAT_MULTIPLY,
            18: ASTBinary.BinOp.BIN_IP_MULTIPLY,
            19: ASTBinary.BinOp.BIN_IP_MODULO,
            20: ASTBinary.BinOp.BIN_IP_OR,
            21: ASTBinary.BinOp.BIN_IP_POWER,
            22: ASTBinary.BinOp.BIN_IP_RSHIFT,
            23: ASTBinary.BinOp.BIN_IP_SUBTRACT,
            24: ASTBinary.BinOp.BIN_IP_DIVIDE,
            25: ASTBinary.BinOp.BIN_IP_XOR,
        }
        return mapping.get(operand, ASTBinary.BinOp.BIN_INVALID)

class ASTCompare(ASTBinary):
    class CompareOp(enum.IntEnum):
        CMP_LESS = 0
        CMP_LESS_EQUAL = 1
        CMP_EQUAL = 2
        CMP_NOT_EQUAL = 3
        CMP_GREATER = 4
        CMP_GREATER_EQUAL = 5
        CMP_IN = 6
        CMP_NOT_IN = 7
        CMP_IS = 8
        CMP_IS_NOT = 9
        CMP_EXCEPTION = 10
        CMP_BAD = 11

    def __init__(self, left: 'ASTNode', right: 'ASTNode', op: int):
        super().__init__(left, right, op, ASTNodeType.NODE_COMPARE)

    def op_str(self) -> str:
        s_cmp_strings = [
            " < ", " <= ", " == ", " != ", " > ", " >= ", " in ", " not in ", " is ", " is not ",
            "<EXCEPTION MATCH>", "<BAD>"
        ]
        if 0 <= self.m_op < len(s_cmp_strings):
            return s_cmp_strings[self.m_op]
        return "<BAD>"

class ASTSlice(ASTBinary):
    class SliceOp(enum.IntEnum):
        SLICE0 = 0
        SLICE1 = 1
        SLICE2 = 2
        SLICE3 = 3

    def __init__(self, op: int, left: Optional['ASTNode'] = None, right: Optional['ASTNode'] = None):
        super().__init__(left, right, op, ASTNodeType.NODE_SLICE)

class ASTStore(ASTNode):
    def __init__(self, src: 'ASTNode', dest: 'ASTNode'):
        super().__init__(ASTNodeType.NODE_STORE)
        self.m_src = src
        self.m_dest = dest

    @property
    def src(self) -> 'ASTNode':
        return self.m_src
    
    @property
    def dest(self) -> 'ASTNode':
        return self.m_dest

class ASTReturn(ASTNode):
    class RetType(enum.IntEnum):
        RETURN = 0
        YIELD = 1
        YIELD_FROM = 2

    def __init__(self, value: Optional['ASTNode'], rettype: int = RetType.RETURN):
        super().__init__(ASTNodeType.NODE_RETURN)
        self.m_value = value
        self.m_rettype = rettype

    @property
    def value(self) -> Optional['ASTNode']:
        return self.m_value
    
    @property
    def rettype(self) -> int:
        return self.m_rettype

class ASTName(ASTNode):
    def __init__(self, name: Any): # name is PycString
        super().__init__(ASTNodeType.NODE_NAME)
        self.m_name = name

    @property
    def name(self) -> Any:
        return self.m_name

class ASTDelete(ASTNode):
    def __init__(self, value: 'ASTNode'):
        super().__init__(ASTNodeType.NODE_DELETE)
        self.m_value = value

    @property
    def value(self) -> 'ASTNode':
        return self.m_value

class ASTFunction(ASTNode):
    def __init__(self, code: 'ASTNode', defArgs: List['ASTNode'], kwDefArgs: List['ASTNode']):
        super().__init__(ASTNodeType.NODE_FUNCTION)
        self.m_code = code
        self.m_defargs = defArgs
        self.m_kwdefargs = kwDefArgs

    @property
    def code(self) -> 'ASTNode':
        return self.m_code

    @property
    def defargs(self) -> List['ASTNode']:
        return self.m_defargs
    
    @property
    def kwdefargs(self) -> List['ASTNode']:
        return self.m_kwdefargs

class ASTClass(ASTNode):
    def __init__(self, code: 'ASTNode', bases: 'ASTNode', name: 'ASTNode'):
        super().__init__(ASTNodeType.NODE_CLASS)
        self.m_code = code
        self.m_bases = bases
        self.m_name = name

    @property
    def code(self) -> 'ASTNode':
        return self.m_code
    
    @property
    def bases(self) -> 'ASTNode':
        return self.m_bases
    
    @property
    def name(self) -> 'ASTNode':
        return self.m_name

class ASTCall(ASTNode):
    # pparams: List[ASTNode]
    # kwparams: List[Tuple[ASTNode, ASTNode]]
    def __init__(self, func: 'ASTNode', pparams: List['ASTNode'], kwparams: List[Tuple['ASTNode', 'ASTNode']]):
        super().__init__(ASTNodeType.NODE_CALL)
        self.m_func = func
        self.m_pparams = pparams
        self.m_kwparams = kwparams
        self.m_var: Optional['ASTNode'] = None
        self.m_kw: Optional['ASTNode'] = None

    @property
    def func(self) -> 'ASTNode':
        return self.m_func
    
    @property
    def pparams(self) -> List['ASTNode']:
        return self.m_pparams
    
    @property
    def kwparams(self) -> List[Tuple['ASTNode', 'ASTNode']]:
        return self.m_kwparams
    
    @property
    def var(self) -> Optional['ASTNode']:
        return self.m_var

    @property
    def kw(self) -> Optional['ASTNode']:
        return self.m_kw

    def has_var(self) -> bool:
        return self.m_var is not None

    def has_kw(self) -> bool:
        return self.m_kw is not None
    
    def set_var(self, var: 'ASTNode'):
        self.m_var = var

    def set_kw(self, kw: 'ASTNode'):
        self.m_kw = kw

class ASTImport(ASTNode):
    def __init__(self, name: Optional['ASTNode'], fromlist: Optional['ASTNode']):
        super().__init__(ASTNodeType.NODE_IMPORT)
        self.m_name = name
        self.m_fromlist = fromlist
        self.m_stores: List['ASTStore'] = []

    @property
    def name(self) -> Optional['ASTNode']:
        return self.m_name
    
    @property
    def stores(self) -> List['ASTStore']:
        return self.m_stores

    def add_store(self, store: 'ASTStore'):
        self.m_stores.append(store)
    
    @property
    def fromlist(self) -> Optional['ASTNode']:
        return self.m_fromlist

class ASTTuple(ASTNode):
    def __init__(self, values: List['ASTNode']):
        super().__init__(ASTNodeType.NODE_TUPLE)
        self.m_values = values
        self.m_requireParens = True

    @property
    def values(self) -> List['ASTNode']:
        return self.m_values

    def add(self, name: 'ASTNode'):
        self.m_values.append(name)
    
    def set_require_parens(self, require: bool):
        self.m_requireParens = require
    
    def require_parens(self) -> bool:
        return self.m_requireParens

class ASTList(ASTNode):
    def __init__(self, values: List['ASTNode']):
        super().__init__(ASTNodeType.NODE_LIST)
        self.m_values = values

    @property
    def values(self) -> List['ASTNode']:
        return self.m_values

class ASTSet(ASTNode):
    def __init__(self, values: List['ASTNode']):
        super().__init__(ASTNodeType.NODE_SET)
        self.m_values = values # Using List instead of deque for simplicity

    @property
    def values(self) -> List['ASTNode']:
        return self.m_values

class ASTMap(ASTNode):
    def __init__(self):
        super().__init__(ASTNodeType.NODE_MAP)
        self.m_values: List[Tuple['ASTNode', 'ASTNode']] = []

    def add(self, key: 'ASTNode', value: 'ASTNode'):
        self.m_values.append((key, value))

    @property
    def values(self) -> List[Tuple['ASTNode', 'ASTNode']]:
        return self.m_values

class ASTKwNamesMap(ASTNode):
    def __init__(self):
        super().__init__(ASTNodeType.NODE_KW_NAMES_MAP)
        self.m_values: List[Tuple['ASTNode', 'ASTNode']] = []

    def add(self, key: 'ASTNode', value: 'ASTNode'):
        self.m_values.append((key, value))

    @property
    def values(self) -> List[Tuple['ASTNode', 'ASTNode']]:
        return self.m_values

class ASTConstMap(ASTNode):
    def __init__(self, keys: 'ASTNode', values: List['ASTNode']):
        super().__init__(ASTNodeType.NODE_CONST_MAP)
        self.m_keys = keys
        self.m_values = values

    @property
    def keys(self) -> 'ASTNode':
        return self.m_keys

    @property
    def values(self) -> List['ASTNode']:
        return self.m_values

class ASTSubscr(ASTNode):
    def __init__(self, name: 'ASTNode', key: 'ASTNode'):
        super().__init__(ASTNodeType.NODE_SUBSCR)
        self.m_name = name
        self.m_key = key

    @property
    def name(self) -> 'ASTNode':
        return self.m_name
    
    @property
    def key(self) -> 'ASTNode':
        return self.m_key

class ASTPrint(ASTNode):
    def __init__(self, value: Optional['ASTNode'], stream: Optional['ASTNode'] = None):
        super().__init__(ASTNodeType.NODE_PRINT)
        self.m_stream = stream
        self.m_eol = False
        self.m_values: List['ASTNode'] = []
        if value is not None:
            self.m_values.append(value)
        else:
            self.m_eol = True

    @property
    def values(self) -> List['ASTNode']:
        return self.m_values
    
    @property
    def stream(self) -> Optional['ASTNode']:
        return self.m_stream
    
    @property
    def eol(self) -> bool:
        return self.m_eol
    
    def add(self, value: 'ASTNode'):
        self.m_values.append(value)
    
    def set_eol(self, eol: bool):
        self.m_eol = eol

class ASTConvert(ASTNode):
    def __init__(self, name: 'ASTNode'):
        super().__init__(ASTNodeType.NODE_CONVERT)
        self.m_name = name
    
    @property
    def name(self) -> 'ASTNode':
        return self.m_name

class ASTKeyword(ASTNode):
    class Word(enum.IntEnum):
        KW_PASS = 0
        KW_BREAK = 1
        KW_CONTINUE = 2

    def __init__(self, key: int):
        super().__init__(ASTNodeType.NODE_KEYWORD)
        self.m_key = key

    @property
    def key(self) -> int:
        return self.m_key

    def word_str(self) -> str:
        s_word_strings = ["pass", "break", "continue"]
        if 0 <= self.m_key < len(s_word_strings):
            return s_word_strings[self.m_key]
        return ""

class ASTRaise(ASTNode):
    def __init__(self, params: List['ASTNode']):
        super().__init__(ASTNodeType.NODE_RAISE)
        self.m_params = params

    @property
    def params(self) -> List['ASTNode']:
        return self.m_params

class ASTExec(ASTNode):
    def __init__(self, stmt: 'ASTNode', glob: 'ASTNode', loc: 'ASTNode'):
        super().__init__(ASTNodeType.NODE_EXEC)
        self.m_stmt = stmt
        self.m_glob = glob
        self.m_loc = loc

    @property
    def statement(self) -> 'ASTNode':
        return self.m_stmt
    
    @property
    def globals(self) -> 'ASTNode':
        return self.m_glob
    
    @property
    def locals(self) -> 'ASTNode':
        return self.m_loc

class ASTBlock(ASTNode):
    class BlkType(enum.IntEnum):
        BLK_MAIN = 0
        BLK_IF = 1
        BLK_ELSE = 2
        BLK_ELIF = 3
        BLK_TRY = 4
        BLK_CONTAINER = 5
        BLK_EXCEPT = 6
        BLK_FINALLY = 7
        BLK_WHILE = 8
        BLK_FOR = 9
        BLK_WITH = 10
        BLK_ASYNCFOR = 11

    def __init__(self, blktype: int, end: int = 0, inited: int = 0):
        super().__init__(ASTNodeType.NODE_BLOCK)
        self.m_blktype = blktype
        self.m_end = end
        self.m_inited = inited
        self.m_nodes: List['ASTNode'] = []

    @property
    def blktype(self) -> int:
        return self.m_blktype
    
    @property
    def end(self) -> int:
        return self.m_end
    
    @property
    def nodes(self) -> List['ASTNode']:
        return self.m_nodes
    
    def size(self) -> int:
        return len(self.m_nodes)
    
    def remove_first(self):
        if self.m_nodes:
            self.m_nodes.pop(0)

    def remove_last(self):
        if self.m_nodes:
            self.m_nodes.pop()

    def append(self, node: 'ASTNode'):
        self.m_nodes.append(node)
    
    def type_str(self) -> str:
        s_type_strings = [
            "", "if", "else", "elif", "try", "CONTAINER", "except",
            "finally", "while", "for", "with", "async for"
        ]
        if 0 <= self.m_blktype < len(s_type_strings):
            return s_type_strings[self.m_blktype]
        return ""

    @property
    def inited(self) -> int:
        return self.m_inited
    
    def init(self, val: int = 1):
        self.m_inited = val

    def set_end(self, end: int):
        self.m_end = end

class ASTCondBlock(ASTBlock):
    class PopType(enum.IntEnum):
        UNINITED = 0
        POPPED = 1
        PRE_POPPED = 2

    def __init__(self, blktype: int, end: int, cond: 'ASTNode', negative: bool = False):
        super().__init__(blktype, end)
        self.m_cond = cond
        self.m_negative = negative
        # Ensure the base class m_inited starts as UNINITED
        self.m_inited = self.PopType.UNINITED

    @property
    def cond(self) -> 'ASTNode':
        return self.m_cond
    
    @property
    def negative(self) -> bool:
        return self.m_negative

    # Helper method to match C++ usage if needed
    def init(self, type=PopType.POPPED):
        self.m_inited = type

class ASTIterBlock(ASTBlock):
    def __init__(self, blktype: int, start: int, end: int, iter_: 'ASTNode'):
        super().__init__(blktype, end)
        self.m_iter = iter_
        self.m_start = start
        self.m_idx: Optional['ASTNode'] = None
        self.m_cond: Optional['ASTNode'] = None
        self.m_comp = False

    @property
    def iter(self) -> 'ASTNode':
        return self.m_iter

    @property
    def index(self) -> Optional['ASTNode']:
        return self.m_idx
    
    @property
    def condition(self) -> Optional['ASTNode']:
        return self.m_cond
    
    def is_comprehension(self) -> bool:
        return self.m_comp
    
    @property
    def start(self) -> int:
        return self.m_start

    def set_index(self, idx: 'ASTNode'):
        self.m_idx = idx
        self.init()

    def set_condition(self, cond: 'ASTNode'):
        self.m_cond = cond
    
    def set_comprehension(self, comp: bool):
        self.m_comp = comp

class ASTContainerBlock(ASTBlock):
    def __init__(self, finally_: int, except_: int = 0):
        super().__init__(ASTBlock.BlkType.BLK_CONTAINER, 0)
        self.m_finally = finally_
        self.m_except = except_

    def has_finally(self) -> bool:
        return self.m_finally != 0
    
    def has_except(self) -> bool:
        return self.m_except != 0
    
    @property
    def finally_(self) -> int:
        return self.m_finally
    
    @property
    def except_(self) -> int:
        return self.m_except
    
    def set_except(self, except_: int):
        self.m_except = except_

class ASTWithBlock(ASTBlock):
    def __init__(self, end: int):
        super().__init__(ASTBlock.BlkType.BLK_WITH, end)
        self.m_expr: Optional['ASTNode'] = None
        self.m_var: Optional['ASTNode'] = None

    @property
    def expr(self) -> Optional['ASTNode']:
        return self.m_expr
    
    @property
    def var(self) -> Optional['ASTNode']:
        return self.m_var
    
    def set_expr(self, expr: 'ASTNode'):
        self.m_expr = expr
        self.init()
    
    def set_var(self, var: 'ASTNode'):
        self.m_var = var

class ASTComprehension(ASTNode):
    def __init__(self, result: 'ASTNode'):
        super().__init__(ASTNodeType.NODE_COMPREHENSION)
        self.m_result = result
        self.m_generators: List['ASTIterBlock'] = [] # Using List acting as front-insert list

    @property
    def result(self) -> 'ASTNode':
        return self.m_result
    
    @property
    def generators(self) -> List['ASTIterBlock']:
        return self.m_generators

    def add_generator(self, gen: 'ASTIterBlock'):
        # Emulate push_front
        self.m_generators.insert(0, gen)

class ASTLoadBuildClass(ASTNode):
    def __init__(self, obj: Any): # obj is PycObject
        super().__init__(ASTNodeType.NODE_LOADBUILDCLASS)
        self.m_obj = obj

    @property
    def object(self) -> Any:
        return self.m_obj

class ASTAwaitable(ASTNode):
    def __init__(self, expr: 'ASTNode'):
        super().__init__(ASTNodeType.NODE_AWAITABLE)
        self.m_expr = expr
    
    @property
    def expression(self) -> 'ASTNode':
        return self.m_expr

class ASTFormattedValue(ASTNode):
    class ConversionFlag(enum.IntEnum):
        NONE = 0
        STR = 1
        REPR = 2
        ASCII = 3
        CONVERSION_MASK = 0x03
        HAVE_FMT_SPEC = 4

    def __init__(self, val: 'ASTNode', conversion: int, format_spec: Optional['ASTNode']):
        super().__init__(ASTNodeType.NODE_FORMATTEDVALUE)
        self.m_val = val
        self.m_conversion = conversion
        self.m_format_spec = format_spec
    
    @property
    def val(self) -> 'ASTNode':
        return self.m_val
    
    @property
    def conversion(self) -> int:
        return self.m_conversion
    
    @property
    def format_spec(self) -> Optional['ASTNode']:
        return self.m_format_spec

class ASTJoinedStr(ASTNode):
    def __init__(self, values: List['ASTNode']):
        super().__init__(ASTNodeType.NODE_JOINEDSTR)
        self.m_values = values

    @property
    def values(self) -> List['ASTNode']:
        return self.m_values

class ASTAnnotatedVar(ASTNode):
    def __init__(self, name: 'ASTNode', type_: 'ASTNode'):
        super().__init__(ASTNodeType.NODE_ANNOTATED_VAR)
        self.m_name = name
        self.m_type = type_

    @property
    def name(self) -> 'ASTNode':
        return self.m_name

    @property
    def annotation(self) -> 'ASTNode':
        return self.m_type

class ASTTernary(ASTNode):
    def __init__(self, if_block: 'ASTNode', if_expr: 'ASTNode', else_expr: 'ASTNode'):
        super().__init__(ASTNodeType.NODE_TERNARY)
        self.m_if_block = if_block
        self.m_if_expr = if_expr
        self.m_else_expr = else_expr

    @property
    def if_block(self) -> 'ASTNode':
        return self.m_if_block

    @property
    def if_expr(self) -> 'ASTNode':
        return self.m_if_expr

    @property
    def else_expr(self) -> 'ASTNode':
        return self.m_else_expr

class ASTLoadBuildClass(ASTNode):
    def __init__(self, obj):
        super().__init__(ASTNodeType.NODE_LOADBUILDCLASS)
        self.object = obj # Wrapper, usually around a PycObject

class ASTKwNamesMap(ASTNode):
    def __init__(self, values=None):
        super().__init__(ASTNodeType.NODE_KW_NAMES_MAP)
        # Store as a list of (key, value) tuples to preserve order
        self.values = values if values is not None else []

    def add(self, key, value):
        self.values.append((key, value))