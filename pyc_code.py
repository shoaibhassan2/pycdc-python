import enum
from typing import List, Optional, Any, TYPE_CHECKING

# Forward declarations
if TYPE_CHECKING:
    from pyc_module import PycModule
    from data import PycData
    from pyc_string import PycString
    from pyc_sequence import PycSequence

from pyc_object import PycObject, LoadObject, PycRef

class PycCode(PycObject):
    class CodeFlags(enum.IntEnum):
        CO_OPTIMIZED = 0x1
        CO_NEWLOCALS = 0x2
        CO_VARARGS = 0x4
        CO_VARKEYWORDS = 0x8
        CO_NESTED = 0x10
        CO_GENERATOR = 0x20
        CO_NOFREE = 0x40
        CO_COROUTINE = 0x80
        CO_ITERABLE_COROUTINE = 0x100
        CO_ASYNC_GENERATOR = 0x200
        CO_GENERATOR_ALLOWED = 0x1000

        # Future flags
        CO_FUTURE_DIVISION = 0x20000
        CO_FUTURE_ABSOLUTE_IMPORT = 0x40000
        CO_FUTURE_WITH_STATEMENT = 0x80000
        CO_FUTURE_PRINT_FUNCTION = 0x100000
        CO_FUTURE_UNICODE_LITERALS = 0x200000
        CO_FUTURE_BARRY_AS_BDFL = 0x400000
        CO_FUTURE_GENERATOR_STOP = 0x800000
        CO_FUTURE_ANNOTATIONS = 0x1000000
        CO_NO_MONITORING_EVENTS = 0x2000000

    def __init__(self, type_id: int = PycObject.TYPE_CODE):
        super().__init__(type_id)
        self.m_argCount = 0
        self.m_posOnlyArgCount = 0
        self.m_kwOnlyArgCount = 0
        self.m_numLocals = 0
        self.m_stackSize = 0
        self.m_flags = 0
        self.m_firstLine = 0
        
        # Using Optional for references that are loaded later
        self.m_code: Optional['PycString'] = None
        self.m_consts: Optional['PycSequence'] = None
        self.m_names: Optional['PycSequence'] = None
        self.m_localNames: Optional['PycSequence'] = None
        self.m_localKinds: Optional['PycString'] = None
        self.m_freeVars: Optional['PycSequence'] = None
        self.m_cellVars: Optional['PycSequence'] = None
        self.m_fileName: Optional['PycString'] = None
        self.m_name: Optional['PycString'] = None
        self.m_qualName: Optional['PycString'] = None
        self.m_lnTable: Optional['PycString'] = None
        self.m_exceptTable: Optional['PycString'] = None
        
        self.m_globalsUsed: List['PycString'] = []

    def load(self, stream: 'PycData', mod: 'PycModule'):
        # [cite: 413-446]
        # Arg Count
        if mod.ver_compare(1, 3) >= 0 and mod.ver_compare(2, 3) < 0:
            self.m_argCount = stream.get16()
        elif mod.ver_compare(2, 3) >= 0:
            self.m_argCount = stream.get32()

        # Positional Only Arg Count (Python 3.8+)
        if mod.ver_compare(3, 8) >= 0:
            self.m_posOnlyArgCount = stream.get32()
        else:
            self.m_posOnlyArgCount = 0

        # Keyword Only Arg Count (Python 3.0+)
        if mod.major_ver >= 3:
            self.m_kwOnlyArgCount = stream.get32()
        else:
            self.m_kwOnlyArgCount = 0

        # Num Locals
        if mod.ver_compare(1, 3) >= 0 and mod.ver_compare(2, 3) < 0:
            self.m_numLocals = stream.get16()
        elif mod.ver_compare(2, 3) >= 0 and mod.ver_compare(3, 11) < 0:
            self.m_numLocals = stream.get32()
        else:
            self.m_numLocals = 0

        # Stack Size
        if mod.ver_compare(1, 5) >= 0 and mod.ver_compare(2, 3) < 0:
            self.m_stackSize = stream.get16()
        elif mod.ver_compare(2, 3) >= 0:
            self.m_stackSize = stream.get32()
        else:
            self.m_stackSize = 0

        # Flags
        if mod.ver_compare(1, 3) >= 0 and mod.ver_compare(2, 3) < 0:
            self.m_flags = stream.get16()
        elif mod.ver_compare(2, 3) >= 0:
            self.m_flags = stream.get32()
        else:
            self.m_flags = 0

        # Remap flags for Python < 3.8
        if mod.ver_compare(3, 8) < 0:
            if self.m_flags & 0xF0000000:
                raise RuntimeError("Cannot remap unexpected flags")
            self.m_flags = (self.m_flags & 0xFFFF) | ((self.m_flags & 0xFFF0000) << 4)

        # Load Objects
        # Casting is implicit in Python, but we expect specific types
        self.m_code = LoadObject(stream, mod) 
        self.m_consts = LoadObject(stream, mod)
        self.m_names = LoadObject(stream, mod)

        if mod.ver_compare(1, 3) >= 0:
            self.m_localNames = LoadObject(stream, mod)
        else:
            # Emulate creating a new empty Tuple
            from pyc_sequence import PycTuple
            self.m_localNames = PycTuple()

        if mod.ver_compare(3, 11) >= 0:
            self.m_localKinds = LoadObject(stream, mod)
        else:
            from pyc_string import PycString
            self.m_localKinds = PycString() # Empty string equivalent

        if mod.ver_compare(2, 1) >= 0 and mod.ver_compare(3, 11) < 0:
            self.m_freeVars = LoadObject(stream, mod)
        else:
            from pyc_sequence import PycTuple
            self.m_freeVars = PycTuple()

        if mod.ver_compare(2, 1) >= 0 and mod.ver_compare(3, 11) < 0:
            self.m_cellVars = LoadObject(stream, mod)
        else:
            from pyc_sequence import PycTuple
            self.m_cellVars = PycTuple()

        self.m_fileName = LoadObject(stream, mod)
        self.m_name = LoadObject(stream, mod)

        if mod.ver_compare(3, 11) >= 0:
            self.m_qualName = LoadObject(stream, mod)
        else:
            from pyc_string import PycString
            self.m_qualName = PycString()

        if mod.ver_compare(1, 5) >= 0 and mod.ver_compare(2, 3) < 0:
            self.m_firstLine = stream.get16()
        elif mod.ver_compare(2, 3) >= 0:
            self.m_firstLine = stream.get32()

        if mod.ver_compare(1, 5) >= 0:
            self.m_lnTable = LoadObject(stream, mod)
        else:
            from pyc_string import PycString
            self.m_lnTable = PycString()

        if mod.ver_compare(3, 11) >= 0:
            self.m_exceptTable = LoadObject(stream, mod)
        else:
            from pyc_string import PycString
            self.m_exceptTable = PycString()

    # Getters
    @property
    def argCount(self) -> int: return self.m_argCount
    @property
    def posOnlyArgCount(self) -> int: return self.m_posOnlyArgCount
    @property
    def kwOnlyArgCount(self) -> int: return self.m_kwOnlyArgCount
    @property
    def numLocals(self) -> int: return self.m_numLocals
    @property
    def stackSize(self) -> int: return self.m_stackSize
    @property
    def flags(self) -> int: return self.m_flags
    @property
    def code(self) -> 'PycString': return self.m_code
    @property
    def consts(self) -> 'PycSequence': return self.m_consts
    @property
    def names(self) -> 'PycSequence': return self.m_names
    @property
    def localNames(self) -> 'PycSequence': return self.m_localNames
    @property
    def localKinds(self) -> 'PycString': return self.m_localKinds
    @property
    def freeVars(self) -> 'PycSequence': return self.m_freeVars
    @property
    def cellVars(self) -> 'PycSequence': return self.m_cellVars
    @property
    def fileName(self) -> 'PycString': return self.m_fileName
    @property
    def name(self) -> 'PycString': return self.m_name
    @property
    def qualName(self) -> 'PycString': return self.m_qualName
    @property
    def firstLine(self) -> int: return self.m_firstLine
    @property
    def lnTable(self) -> 'PycString': return self.m_lnTable
    @property
    def exceptTable(self) -> 'PycString': return self.m_exceptTable

    def getConst(self, idx: int) -> 'PycObject':
        return self.m_consts.get(idx)

    def getName(self, idx: int) -> 'PycString':
        # Cast to PycString assumed safe based on usage
        return self.m_names.get(idx)

    def getLocal(self, idx: int) -> 'PycString':
        return self.m_localNames.get(idx)

    def getCellVar(self, mod: 'PycModule', idx: int) -> 'PycString':
        # [cite: 446-448]
        if mod.ver_compare(3, 11) >= 0:
            return self.getLocal(idx)
        
        # cellvars come first, then freevars
        if idx >= self.m_cellVars.size():
            return self.m_freeVars.get(idx - self.m_cellVars.size())
        else:
            return self.m_cellVars.get(idx)

    @property
    def globalsUsed(self) -> List['PycString']:
        return self.m_globalsUsed

    def markGlobal(self, varname: 'PycString'):
        self.m_globalsUsed.append(varname)