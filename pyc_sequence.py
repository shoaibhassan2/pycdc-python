import sys
from typing import List, Tuple, Optional, Any, TYPE_CHECKING
from pyc_object import PycObject, LoadObject, PycObjectType

if TYPE_CHECKING:
    from pyc_module import PycModule
    from data import PycData

class PycSequence(PycObject):
    def __init__(self, type_id: int):
        super().__init__(type_id)
        self.m_size = 0

    @property
    def size(self) -> int:
        return self.m_size

    def get(self, idx: int) -> 'PycObject':
        raise NotImplementedError

class PycSimpleSequence(PycSequence):
    def __init__(self, type_id: int):
        super().__init__(type_id)
        self.m_values: List['PycObject'] = []

    def load(self, stream: 'PycData', mod: 'PycModule'):
        # [cite: 657-658]
        self.m_size = stream.get32()
        self.m_values = []
        for _ in range(self.m_size):
            obj = LoadObject(stream, mod)
            if obj is not None:
                self.m_values.append(obj)

    def is_equal(self, obj: 'PycObject') -> bool:
        # [cite: 659-661]
        if self.type != obj.type:
            return False
        if not isinstance(obj, PycSimpleSequence):
            return False
        if self.m_size != obj.m_size:
            return False
        
        for v1, v2 in zip(self.m_values, obj.m_values):
            if not v1.is_equal(v2):
                return False
        return True

    @property
    def values(self) -> List['PycObject']:
        return self.m_values

    def get(self, idx: int) -> 'PycObject':
        if 0 <= idx < len(self.m_values):
            return self.m_values[idx]
        raise IndexError(f"Sequence index out of range: {idx}")

class PycTuple(PycSimpleSequence):
    def __init__(self, type_id: int = PycObjectType.TYPE_TUPLE):
        super().__init__(type_id)

    def load(self, stream: 'PycData', mod: 'PycModule'):
        # [cite: 662-664]
        if self.type == PycObjectType.TYPE_SMALL_TUPLE:
            self.m_size = stream.get_byte()
        else:
            self.m_size = stream.get32()

        self.m_values = []
        for _ in range(self.m_size):
            obj = LoadObject(stream, mod)
            if obj is not None:
                self.m_values.append(obj)

class PycList(PycSimpleSequence):
    def __init__(self, type_id: int = PycObjectType.TYPE_LIST):
        super().__init__(type_id)

class PycSet(PycSimpleSequence):
    def __init__(self, type_id: int = PycObjectType.TYPE_SET):
        super().__init__(type_id)

class PycDict(PycObject):
    def __init__(self, type_id: int = PycObjectType.TYPE_DICT):
        super().__init__(type_id)
        self.m_values: List[Tuple['PycObject', 'PycObject']] = []

    def load(self, stream: 'PycData', mod: 'PycModule'):
        # [cite: 665-667]
        while True:
            key = LoadObject(stream, mod)
            if key is None or key.type == PycObjectType.TYPE_NULL: # NULL check depends on LoadObject impl
                break
            val = LoadObject(stream, mod)
            self.m_values.append((key, val))

    def is_equal(self, obj: 'PycObject') -> bool:
        # [cite: 668-671]
        if self.type != obj.type:
            return False
        if not isinstance(obj, PycDict):
            return False
        if len(self.m_values) != len(obj.m_values):
            return False
        
        # Order matters in marshalled dicts usually? The C++ impl compares sequentially.
        for (k1, v1), (k2, v2) in zip(self.m_values, obj.m_values):
            if not k1.is_equal(k2):
                return False
            if not v1.is_equal(v2):
                return False
        return True

    @property
    def values(self) -> List[Tuple['PycObject', 'PycObject']]:
        return self.m_values