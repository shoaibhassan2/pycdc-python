import sys
from typing import List, Optional, TYPE_CHECKING
import enum
from pyc_code import PycCode
from pyc_string import PycString
from pyc_object import PycObject

# Magic numbers [cite: 534]
class PycMagic(enum.IntEnum):
    MAGIC_1_0   = 0x00999902
    MAGIC_1_1   = 0x00999903
    MAGIC_1_3   = 0x0A0D2E89
    MAGIC_1_4   = 0x0A0D1704
    MAGIC_1_5   = 0x0A0D4E99
    MAGIC_1_6   = 0x0A0DC4FC
    MAGIC_2_0   = 0x0A0DC687
    MAGIC_2_1   = 0x0A0DEB2A
    MAGIC_2_2   = 0x0A0DED2D
    MAGIC_2_3   = 0x0A0DF23B
    MAGIC_2_4   = 0x0A0DF26D
    MAGIC_2_5   = 0x0A0DF2B3
    MAGIC_2_6   = 0x0A0DF2D1
    MAGIC_2_7   = 0x0A0DF303
    MAGIC_3_0   = 0x0A0D0C3A
    MAGIC_3_1   = 0x0A0D0C4E
    MAGIC_3_2   = 0x0A0D0C6C
    MAGIC_3_3   = 0x0A0D0C9E
    MAGIC_3_4   = 0x0A0D0CEE
    MAGIC_3_5   = 0x0A0D0D16
    MAGIC_3_5_3 = 0x0A0D0D17
    MAGIC_3_6   = 0x0A0D0D33
    MAGIC_3_7   = 0x0A0D0D42
    MAGIC_3_8   = 0x0A0D0D55
    MAGIC_3_9   = 0x0A0D0D61
    MAGIC_3_10  = 0x0A0D0D6F
    MAGIC_3_11  = 0x0A0D0DA7
    MAGIC_3_12  = 0x0A0D0DCB
    MAGIC_3_13  = 0x0A0D0DF3
    MAGIC_3_14  = 0x0A0D0E2B
    INVALID     = 0

class PycModule:
    def __init__(self):
        self.m_maj = -1
        self.m_min = -1
        self.m_unicode = False
        self.m_code: Optional['PycCode'] = None
        self.m_interns: List['PycString'] = []
        self.m_refs: List['PycObject'] = []

    def set_version(self, magic: int):
        self.m_unicode = False  # Default
        
        if magic == PycMagic.MAGIC_1_0:
            self.m_maj, self.m_min = 1, 0
        elif magic == PycMagic.MAGIC_1_1:
            self.m_maj, self.m_min = 1, 1
        elif magic == PycMagic.MAGIC_1_3:
            self.m_maj, self.m_min = 1, 3
        elif magic == PycMagic.MAGIC_1_4:
            self.m_maj, self.m_min = 1, 4
        elif magic == PycMagic.MAGIC_1_5:
            self.m_maj, self.m_min = 1, 5
        elif magic == PycMagic.MAGIC_1_6 + 1:
            self.m_unicode = True
            self.m_maj, self.m_min = 1, 6
        elif magic == PycMagic.MAGIC_1_6:
            self.m_maj, self.m_min = 1, 6
        elif magic == PycMagic.MAGIC_2_0 + 1:
            self.m_unicode = True
            self.m_maj, self.m_min = 2, 0
        elif magic == PycMagic.MAGIC_2_0:
            self.m_maj, self.m_min = 2, 0
        elif magic == PycMagic.MAGIC_2_1 + 1:
            self.m_unicode = True
            self.m_maj, self.m_min = 2, 1
        elif magic == PycMagic.MAGIC_2_1:
            self.m_maj, self.m_min = 2, 1
        elif magic == PycMagic.MAGIC_2_2 + 1:
            self.m_unicode = True
            self.m_maj, self.m_min = 2, 2
        elif magic == PycMagic.MAGIC_2_2:
            self.m_maj, self.m_min = 2, 2
        elif magic == PycMagic.MAGIC_2_3 + 1:
            self.m_unicode = True
            self.m_maj, self.m_min = 2, 3
        elif magic == PycMagic.MAGIC_2_3:
            self.m_maj, self.m_min = 2, 3
        elif magic == PycMagic.MAGIC_2_4 + 1:
            self.m_unicode = True
            self.m_maj, self.m_min = 2, 4
        elif magic == PycMagic.MAGIC_2_4:
            self.m_maj, self.m_min = 2, 4
        elif magic == PycMagic.MAGIC_2_5 + 1:
            self.m_unicode = True
            self.m_maj, self.m_min = 2, 5
        elif magic == PycMagic.MAGIC_2_5:
            self.m_maj, self.m_min = 2, 5
        elif magic == PycMagic.MAGIC_2_6 + 1:
            self.m_unicode = True
            self.m_maj, self.m_min = 2, 6
        elif magic == PycMagic.MAGIC_2_6:
            self.m_maj, self.m_min = 2, 6
        elif magic == PycMagic.MAGIC_2_7 + 1:
            self.m_unicode = True
            self.m_maj, self.m_min = 2, 7
        elif magic == PycMagic.MAGIC_2_7:
            self.m_maj, self.m_min = 2, 7
        # 3.0+ are always unicode
        elif magic == PycMagic.MAGIC_3_0 + 1:
            self.m_maj, self.m_min, self.m_unicode = 3, 0, True
        elif magic == PycMagic.MAGIC_3_1 + 1:
            self.m_maj, self.m_min, self.m_unicode = 3, 1, True
        elif magic == PycMagic.MAGIC_3_2:
            self.m_maj, self.m_min, self.m_unicode = 3, 2, True
        elif magic == PycMagic.MAGIC_3_3:
            self.m_maj, self.m_min, self.m_unicode = 3, 3, True
        elif magic == PycMagic.MAGIC_3_4:
            self.m_maj, self.m_min, self.m_unicode = 3, 4, True
        elif magic == PycMagic.MAGIC_3_5 or magic == PycMagic.MAGIC_3_5_3:
            self.m_maj, self.m_min, self.m_unicode = 3, 5, True
        elif magic == PycMagic.MAGIC_3_6:
            self.m_maj, self.m_min, self.m_unicode = 3, 6, True
        elif magic == PycMagic.MAGIC_3_7:
            self.m_maj, self.m_min, self.m_unicode = 3, 7, True
        elif magic == PycMagic.MAGIC_3_8:
            self.m_maj, self.m_min, self.m_unicode = 3, 8, True
        elif magic == PycMagic.MAGIC_3_9:
            self.m_maj, self.m_min, self.m_unicode = 3, 9, True
        elif magic == PycMagic.MAGIC_3_10:
            self.m_maj, self.m_min, self.m_unicode = 3, 10, True
        elif magic == PycMagic.MAGIC_3_11:
            self.m_maj, self.m_min, self.m_unicode = 3, 11, True
        elif magic == PycMagic.MAGIC_3_12:
            self.m_maj, self.m_min, self.m_unicode = 3, 12, True
        elif magic == PycMagic.MAGIC_3_13:
            self.m_maj, self.m_min, self.m_unicode = 3, 13, True
        elif magic == PycMagic.MAGIC_3_14:
            self.m_maj, self.m_min, self.m_unicode = 3, 14, True
        else:
            self.m_maj, self.m_min = -1, -1 # Invalid

    @staticmethod
    def is_supported_version(major: int, minor: int) -> bool:
        # [cite: 516-519]
        if major == 1:
            return 0 <= minor <= 6
        elif major == 2:
            return 0 <= minor <= 7
        elif major == 3:
            return 0 <= minor <= 14 # Updated to 13 based on magic
        return False

    def is_valid(self) -> bool:
        return self.m_maj >= 0 and self.m_min >= 0

    @property
    def major_ver(self) -> int:
        return self.m_maj
    
    @property
    def minor_ver(self) -> int:
        return self.m_min
    
    @property
    def code(self) -> 'PycCode':
        return self.m_code

    def ver_compare(self, maj: int, min_: int) -> int:
        if self.m_maj == maj:
            return self.m_min - min_
        return self.m_maj - maj

    def is_unicode(self) -> bool:
        return self.m_unicode

    def str_is_unicode(self) -> bool:
        # [cite: 540]
        # Circular dep: requires PycCode definition of flags. 
        # We assume usage happens after loading where m_code is valid.
        from pyc_code import PycCode
        return (self.m_maj >= 3) or \
               ((self.m_code.flags & PycCode.CodeFlags.CO_FUTURE_UNICODE_LITERALS) != 0)

    def intern_is_bytes(self) -> bool:
        # [cite: 542]
        from pyc_code import PycCode
        return (self.m_maj < 3) and \
               ((self.m_code.flags & PycCode.CodeFlags.CO_FUTURE_UNICODE_LITERALS) != 0)

    def load_from_file(self, filename: str):
        # [cite: 520-527]
        from data import PycFile
        from pyc_object import LoadObject, PycObject
        
        infile = PycFile(filename)
        if not infile.is_open():
            raise IOError(f"Error opening file {filename}")
        
        self.set_version(infile.get32())
        if not self.is_valid():
            raise ValueError("Bad MAGIC!")
        
        flags = 0
        if self.ver_compare(3, 7) >= 0:
            flags = infile.get32()
        
        if flags & 0x1:
            # Skip checksum (optional in 3.7+)
            infile.get32()
            infile.get32()
        else:
            infile.get32() # Timestamp
            if self.ver_compare(3, 3) >= 0:
                infile.get32() # Size parameter (3.3+)
        
        # Load the main code object
        # In C++: m_code = LoadObject(&in, this).cast<PycCode>();
        obj = LoadObject(infile, self)
        if obj and obj.type == PycObject.TYPE_CODE:
             self.m_code = obj
        else:
             raise ValueError("Failed to load code object")

    def load_from_marshalled_file(self, filename: str, major: int, minor: int):
        # [cite: 528-531]
        from data import PycFile
        from pyc_object import LoadObject, PycObject
        
        infile = PycFile(filename)
        if not infile.is_open():
            raise IOError(f"Error opening file {filename}")
            
        if not self.is_supported_version(major, minor):
            raise ValueError(f"Unsupported version {major}.{minor}")
            
        self.m_maj = major
        self.m_min = minor
        self.m_unicode = (major >= 3)
        
        obj = LoadObject(infile, self)
        if obj and obj.type == PycObject.TYPE_CODE:
             self.m_code = obj
        else:
             raise ValueError("Failed to load code object from marshalled file")

    def intern(self, s: 'PycString'):
        self.m_interns.append(s)

    def get_intern(self, ref: int) -> 'PycString':
        if ref < 0 or ref >= len(self.m_interns):
            raise IndexError("Intern index out of range")
        return self.m_interns[ref]

    def ref_object(self, obj: 'PycObject'):
        self.m_refs.append(obj)

    def get_ref(self, ref: int) -> 'PycObject':
        if ref < 0 or ref >= len(self.m_refs):
            raise IndexError("Ref index out of range")
        return self.m_refs[ref]