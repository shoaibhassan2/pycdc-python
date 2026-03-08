import sys
import enum
from typing import Optional, TYPE_CHECKING, Any

# Forward declarations
if TYPE_CHECKING:
    from pyc_module import PycModule
    from data import PycData

# Define Enum for easier management
class PycObjectType(enum.IntEnum):
    TYPE_NULL = ord('0')
    TYPE_NONE = ord('N')
    TYPE_FALSE = ord('F')
    TYPE_TRUE = ord('T')
    TYPE_STOPITER = ord('S')
    TYPE_ELLIPSIS = ord('.')
    TYPE_INT = ord('i')
    TYPE_INT64 = ord('I')
    TYPE_FLOAT = ord('f')
    TYPE_BINARY_FLOAT = ord('g')
    TYPE_COMPLEX = ord('x')
    TYPE_BINARY_COMPLEX = ord('y')
    TYPE_LONG = ord('l')
    TYPE_STRING = ord('s')
    TYPE_INTERNED = ord('t')
    TYPE_STRINGREF = ord('R')
    TYPE_OBREF = ord('r')
    TYPE_TUPLE = ord('(')
    TYPE_LIST = ord('[')
    TYPE_DICT = ord('{')
    TYPE_CODE = ord('c')
    TYPE_CODE2 = ord('C')
    TYPE_UNICODE = ord('u')
    TYPE_UNKNOWN = ord('?')
    TYPE_SET = ord('<')
    TYPE_FROZENSET = ord('>')
    TYPE_ASCII = ord('a')
    TYPE_ASCII_INTERNED = ord('A')
    TYPE_SMALL_TUPLE = ord(')')
    TYPE_SHORT_ASCII = ord('z')
    TYPE_SHORT_ASCII_INTERNED = ord('Z')

class PycObject:
    # Expose Enum members as class attributes to match C++ static access
    TYPE_NULL = PycObjectType.TYPE_NULL
    TYPE_NONE = PycObjectType.TYPE_NONE
    TYPE_FALSE = PycObjectType.TYPE_FALSE
    TYPE_TRUE = PycObjectType.TYPE_TRUE
    TYPE_STOPITER = PycObjectType.TYPE_STOPITER
    TYPE_ELLIPSIS = PycObjectType.TYPE_ELLIPSIS
    TYPE_INT = PycObjectType.TYPE_INT
    TYPE_INT64 = PycObjectType.TYPE_INT64
    TYPE_FLOAT = PycObjectType.TYPE_FLOAT
    TYPE_BINARY_FLOAT = PycObjectType.TYPE_BINARY_FLOAT
    TYPE_COMPLEX = PycObjectType.TYPE_COMPLEX
    TYPE_BINARY_COMPLEX = PycObjectType.TYPE_BINARY_COMPLEX
    TYPE_LONG = PycObjectType.TYPE_LONG
    TYPE_STRING = PycObjectType.TYPE_STRING
    TYPE_INTERNED = PycObjectType.TYPE_INTERNED
    TYPE_STRINGREF = PycObjectType.TYPE_STRINGREF
    TYPE_OBREF = PycObjectType.TYPE_OBREF
    TYPE_TUPLE = PycObjectType.TYPE_TUPLE
    TYPE_LIST = PycObjectType.TYPE_LIST
    TYPE_DICT = PycObjectType.TYPE_DICT
    TYPE_CODE = PycObjectType.TYPE_CODE
    TYPE_CODE2 = PycObjectType.TYPE_CODE2
    TYPE_UNICODE = PycObjectType.TYPE_UNICODE
    TYPE_UNKNOWN = PycObjectType.TYPE_UNKNOWN
    TYPE_SET = PycObjectType.TYPE_SET
    TYPE_FROZENSET = PycObjectType.TYPE_FROZENSET
    TYPE_ASCII = PycObjectType.TYPE_ASCII
    TYPE_ASCII_INTERNED = PycObjectType.TYPE_ASCII_INTERNED
    TYPE_SMALL_TUPLE = PycObjectType.TYPE_SMALL_TUPLE
    TYPE_SHORT_ASCII = PycObjectType.TYPE_SHORT_ASCII
    TYPE_SHORT_ASCII_INTERNED = PycObjectType.TYPE_SHORT_ASCII_INTERNED

    def __init__(self, type_id: int = TYPE_UNKNOWN):
        self.m_type = type_id

    @property
    def type(self) -> int:
        return self.m_type

    def load(self, stream: 'PycData', mod: 'PycModule'):
        pass

    def is_equal(self, obj: 'PycObject') -> bool:
        return self is obj
    
    def print(self, stream, mod: 'PycModule', triple: bool = False, parent_quote=None):
        if self.m_type == self.TYPE_NONE:
            stream.write("None")
        elif self.m_type == self.TYPE_FALSE:
            stream.write("False")
        elif self.m_type == self.TYPE_TRUE:
            stream.write("True")
        elif self.m_type == self.TYPE_ELLIPSIS:
            stream.write("...")
        else:
            # Fallback for unhandled types
            pass
# Singleton Objects
Pyc_None = PycObject(PycObjectType.TYPE_NONE)
Pyc_Ellipsis = PycObject(PycObjectType.TYPE_ELLIPSIS)
Pyc_StopIteration = PycObject(PycObjectType.TYPE_STOPITER)
Pyc_False = PycObject(PycObjectType.TYPE_FALSE)
Pyc_True = PycObject(PycObjectType.TYPE_TRUE)

def CreateObject(type_id: int) -> Optional[PycObject]:
    # Lazy imports to avoid circular dependency
    from pyc_numeric import PycInt, PycLong, PycFloat, PycCFloat, PycComplex, PycCComplex
    from pyc_string import PycString
    from pyc_sequence import PycTuple, PycList, PycDict, PycSet
    from pyc_code import PycCode

    if type_id == PycObjectType.TYPE_NULL:
        return None
    elif type_id == PycObjectType.TYPE_NONE:
        return Pyc_None
    elif type_id == PycObjectType.TYPE_FALSE:
        return Pyc_False
    elif type_id == PycObjectType.TYPE_TRUE:
        return Pyc_True
    elif type_id == PycObjectType.TYPE_STOPITER:
        return Pyc_StopIteration
    elif type_id == PycObjectType.TYPE_ELLIPSIS:
        return Pyc_Ellipsis
    elif type_id == PycObjectType.TYPE_INT:
        return PycInt(type_id=type_id)
    elif type_id == PycObjectType.TYPE_INT64:
        return PycLong(type_id=type_id)
    elif type_id == PycObjectType.TYPE_FLOAT:
        return PycFloat(type_id=type_id)
    elif type_id == PycObjectType.TYPE_BINARY_FLOAT:
        return PycCFloat(type_id=type_id)
    elif type_id == PycObjectType.TYPE_COMPLEX:
        return PycComplex(type_id=type_id)
    elif type_id == PycObjectType.TYPE_BINARY_COMPLEX:
        return PycCComplex(type_id=type_id)
    elif type_id == PycObjectType.TYPE_LONG:
        return PycLong(type_id=type_id)
    elif type_id in (PycObjectType.TYPE_STRING, PycObjectType.TYPE_INTERNED,
                     PycObjectType.TYPE_STRINGREF, PycObjectType.TYPE_UNICODE,
                     PycObjectType.TYPE_ASCII, PycObjectType.TYPE_ASCII_INTERNED,
                     PycObjectType.TYPE_SHORT_ASCII, PycObjectType.TYPE_SHORT_ASCII_INTERNED):
        return PycString(type_id=type_id)
    elif type_id in (PycObjectType.TYPE_TUPLE, PycObjectType.TYPE_SMALL_TUPLE):
        return PycTuple(type_id=type_id)
    elif type_id == PycObjectType.TYPE_LIST:
        return PycList(type_id=type_id)
    elif type_id == PycObjectType.TYPE_DICT:
        return PycDict(type_id=type_id)
    elif type_id in (PycObjectType.TYPE_CODE, PycObjectType.TYPE_CODE2):
        return PycCode(type_id=type_id)
    elif type_id in (PycObjectType.TYPE_SET, PycObjectType.TYPE_FROZENSET):
        return PycSet(type_id=type_id)
    else:
        sys.stderr.write(f"CreateObject: Got unsupported type 0x{type_id:X}\n")
        return None

def LoadObject(stream: 'PycData', mod: 'PycModule') -> Optional[PycObject]:
    type_byte = stream.get_byte()
    
    if type_byte == PycObjectType.TYPE_OBREF:
        index = stream.get32()
        return mod.get_ref(index)
    
    obj = CreateObject(type_byte & 0x7F)
    
    if obj is not None:
        if type_byte & 0x80:
            mod.ref_object(obj)
        obj.load(stream, mod)
        
    return obj

PycRef = Any