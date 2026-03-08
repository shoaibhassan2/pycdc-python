import sys
import struct
import math
from typing import List, Optional, Any, TYPE_CHECKING
from pyc_object import PycObject, PycRef

if TYPE_CHECKING:
    from pyc_module import PycModule
    from data import PycData

class PycInt(PycObject):
    def __init__(self, value: int = 0, type_id: int = PycObject.TYPE_INT):
        super().__init__(type_id)
        self.m_value = value

    def load(self, stream: 'PycData', mod: 'PycModule'):
        self.m_value = stream.get32()
        # In Python, integers are arbitrary precision, but standard 32-bit load implies signed 32-bit usually?
        # C++ get32 returns unsigned usually, but PycInt might be signed.
        # Let's assume standard behavior: if it's > 2^31-1, it might be negative in 32-bit sense?
        # Actually PycInt usually stores standard Python ints.
        # Check if we need to interpret as signed 32-bit:
        if self.m_value >= 0x80000000:
            self.m_value -= 0x100000000

    def is_equal(self, obj: 'PycObject') -> bool:
        if self.type != obj.type:
            return False
        return self.m_value == obj.value

    @property
    def value(self) -> int:
        return self.m_value


class PycLong(PycObject):
    def __init__(self, type_id: int = PycObject.TYPE_LONG):
        super().__init__(type_id)
        self.m_size = 0
        self.m_value: List[int] = [] # Storing 16-bit digits

    def load(self, stream: 'PycData', mod: 'PycModule'):
        if self.type == PycObject.TYPE_INT64:
            # [cite: 548-550]
            lo = stream.get32()
            hi = stream.get32()
            self.m_value = [
                lo & 0xFFFF, (lo >> 16) & 0xFFFF,
                hi & 0xFFFF, (hi >> 16) & 0xFFFF
            ]
            self.m_size = -4 if (hi & 0x80000000) else 4
        else:
            # [cite: 551-553]
            self.m_size = stream.get32()
            # Convert unsigned 32-bit to signed 32-bit for size
            if self.m_size >= 0x80000000:
                self.m_size -= 0x100000000
                
            actual_size = abs(self.m_size)
            self.m_value = []
            for _ in range(actual_size):
                self.m_value.append(stream.get16())

    def is_equal(self, obj: 'PycObject') -> bool:
        if self.type != obj.type:
            return False
        # Cast to PycLong in python is just duck typing or instance check
        if not isinstance(obj, PycLong):
            return False
        if self.m_size != obj.m_size:
            return False
        return self.m_value == obj.m_value

    @property
    def value(self) -> List[int]:
        return self.m_value
    
    @property
    def size(self) -> int:
        return self.m_size

    def __repr__(self):
        # Helper to convert internal 15-bit/16-bit representation to Python int
        # Python longs are stored as base-2^15 digits (usually) in marshal?
        # C++ source 559 mentions 15 bits.
        val = 0
        for digit in reversed(self.m_value):
            val = (val << 15) | digit
        if self.m_size < 0:
            val = -val
        return str(val)

    def repr(self, mod: 'PycModule') -> str:
        # [cite: 557-568]
        # Allow Python to handle the formatting since it supports arbitrary precision natively
        val = 0
        # Reconstruct the value from 15-bit digits
        for i, digit in enumerate(self.m_value):
            val |= (digit & 0xFFFF) << (i * 15)
        
        if self.m_size < 0:
            val = -val
            
        suffix = "L" if mod.ver_compare(3, 0) < 0 else ""
        return f"{hex(val)}{suffix}".replace("0x", "0x" if val >= 0 else "-0x")


class PycFloat(PycObject):
    def __init__(self, type_id: int = PycObject.TYPE_FLOAT):
        super().__init__(type_id)
        self.m_value = "" # Floats stored as strings in older marshal format

    def load(self, stream: 'PycData', mod: 'PycModule'):
        # [cite: 569-571]
        length = stream.get_byte()
        if length < 0:
            raise MemoryError("Bad alloc")
        if length > 0:
            self.m_value = stream.get_buffer(length).decode('latin1') # Usually ASCII representation

    def is_equal(self, obj: 'PycObject') -> bool:
        if self.type != obj.type:
            return False
        return self.m_value == obj.m_value

    @property
    def value(self) -> str:
        return self.m_value


class PycComplex(PycFloat):
    def __init__(self, type_id: int = PycObject.TYPE_COMPLEX):
        super().__init__(type_id)
        self.m_imag = ""

    def load(self, stream: 'PycData', mod: 'PycModule'):
        # [cite: 573-575]
        super().load(stream, mod) # Load real part
        length = stream.get_byte()
        if length < 0:
            raise MemoryError("Bad alloc")
        if length > 0:
            self.m_imag = stream.get_buffer(length).decode('latin1')

    def is_equal(self, obj: 'PycObject') -> bool:
        if not super().is_equal(obj):
            return False
        return self.m_imag == obj.m_imag

    @property
    def imag(self) -> str:
        return self.m_imag


class PycCFloat(PycObject):
    def __init__(self, type_id: int = PycObject.TYPE_BINARY_FLOAT):
        super().__init__(type_id)
        self.m_value = 0.0

    def load(self, stream: 'PycData', mod: 'PycModule'):
        # [cite: 577]
        # Read 64-bit float (double)
        buffer = stream.get_buffer(8)
        self.m_value = struct.unpack('<d', buffer)[0]

    def is_equal(self, obj: 'PycObject') -> bool:
        if self.type != obj.type:
            return False
        return self.m_value == obj.m_value

    @property
    def value(self) -> float:
        return self.m_value


class PycCComplex(PycCFloat):
    def __init__(self, type_id: int = PycObject.TYPE_BINARY_COMPLEX):
        super().__init__(type_id)
        self.m_imag = 0.0

    def load(self, stream: 'PycData', mod: 'PycModule'):
        # [cite: 578]
        super().load(stream, mod)
        buffer = stream.get_buffer(8)
        self.m_imag = struct.unpack('<d', buffer)[0]

    def is_equal(self, obj: 'PycObject') -> bool:
        if not super().is_equal(obj):
            return False
        return self.m_imag == obj.m_imag

    @property
    def imag(self) -> float:
        return self.m_imag