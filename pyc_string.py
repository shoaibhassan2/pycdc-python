import sys
from typing import Optional, TYPE_CHECKING
from pyc_object import PycObject, PycObjectType

if TYPE_CHECKING:
    from pyc_module import PycModule
    from data import PycData

def check_ascii(data: bytes) -> bool:
    # [cite: 685-686]
    for b in data:
        if b & 0x80:
            return False
    return True

class PycString(PycObject):
    def __init__(self, type_id: int = PycObjectType.TYPE_STRING):
        super().__init__(type_id)
        self.m_value: bytes = b""

    def load(self, stream: 'PycData', mod: 'PycModule'):
        # [cite: 687-694]
        if self.type == PycObjectType.TYPE_STRINGREF:
            # Reference to an already interned string
            ref_idx = stream.get32()
            str_obj = mod.get_intern(ref_idx)
            self.m_type = str_obj.type
            self.m_value = str_obj.value
        else:
            length = 0
            if self.type in (PycObjectType.TYPE_SHORT_ASCII, PycObjectType.TYPE_SHORT_ASCII_INTERNED):
                length = stream.get_byte()
            else:
                length = stream.get32()

            if length < 0:
                raise MemoryError("Negative string length")

            self.m_value = b""
            if length > 0:
                self.m_value = stream.get_buffer(length)
                
                # Validate ASCII types
                if self.type in (PycObjectType.TYPE_ASCII, PycObjectType.TYPE_ASCII_INTERNED,
                                 PycObjectType.TYPE_SHORT_ASCII, PycObjectType.TYPE_SHORT_ASCII_INTERNED):
                    if not check_ascii(self.m_value):
                        raise ValueError("Invalid bytes in ASCII string")

            # Handle Interning
            if self.type in (PycObjectType.TYPE_INTERNED, PycObjectType.TYPE_ASCII_INTERNED,
                             PycObjectType.TYPE_SHORT_ASCII_INTERNED):
                mod.intern(self)

    def is_equal(self, obj: 'PycObject') -> bool:
        # [cite: 695]
        if self.type != obj.type:
            return False
        if not isinstance(obj, PycString):
            return False
        return self.m_value == obj.m_value

    def is_equal_str(self, s: str) -> bool:
        # Helper for comparison with Python strings (decoding assumed utf-8 or latin1 depending on context)
        # The C++ code compares m_value directly.
        return self.m_value == s.encode('utf-8') # Approximation

    @property
    def value(self) -> bytes:
        return self.m_value

    def print(self, stream, mod: 'PycModule', triple: bool = False, parent_f_string_quote: Optional[str] = None):
        # [cite: 696-721]
        prefix = ""
        
        # Determine prefix based on type and version
        if self.type == PycObjectType.TYPE_STRING:
            if mod.str_is_unicode():
                prefix = "b"
        elif self.type == PycObjectType.TYPE_UNICODE:
            if not mod.str_is_unicode():
                prefix = "u"
        elif self.type == PycObjectType.TYPE_INTERNED:
            if mod.intern_is_bytes():
                prefix = "b"
        elif self.type in (PycObjectType.TYPE_ASCII, PycObjectType.TYPE_ASCII_INTERNED,
                           PycObjectType.TYPE_SHORT_ASCII, PycObjectType.TYPE_SHORT_ASCII_INTERNED):
            prefix = ""
        else:
            # Fallback/Error
            pass

        stream.write(prefix)

        if not self.m_value:
            stream.write("''")
            return

        # Determine quote style
        use_quotes = False # Default to single quotes '
        
        # In C++, m_value is std::string (bytes). We iterate over bytes.
        # Check for quotes inside the string to decide outer quotes
        if parent_f_string_quote is None:
            for b in self.m_value:
                ch = chr(b)
                if ch == "'":
                    use_quotes = True # Use double quotes
                elif ch == '"':
                    use_quotes = False # Use single quotes
                    break
        else:
            use_quotes = (parent_f_string_quote[0] == '"')

        # Output start quote
        if parent_f_string_quote is None:
            if triple:
                stream.write('"""' if use_quotes else "'''")
            else:
                stream.write('"' if use_quotes else "'")

        # Output characters with escaping
        for b in self.m_value:
            ch = chr(b)
            # Handle special escapes
            if b < 0x20 or b == 0x7F:
                if ch == '\r':
                    stream.write("\\r")
                elif ch == '\n':
                    if triple:
                        stream.write("\n")
                    else:
                        stream.write("\\n")
                elif ch == '\t':
                    stream.write("\\t")
                else:
                    stream.write(f"\\x{b:02x}")
            elif b >= 0x80:
                if self.type == PycObjectType.TYPE_UNICODE:
                    # Assume UTF-8 if it's a unicode object, otherwise raw bytes
                    # Note: C++ simply prints the char. In Python 3, writing bytes to text stream 
                    # requires decoding or explicit handling. We assume stream accepts str.
                    # If this is actual unicode data stored as utf-8 bytes:
                    try:
                        # Attempt to decode single byte? No, UTF-8 is multi-byte.
                        # The C++ code iterates byte by byte. If it's UTF-8, it just passes through.
                        # We will simulate pass-through (latin1 maps 1-to-1).
                        stream.write(ch) 
                    except:
                        stream.write(f"\\x{b:02x}")
                else:
                    stream.write(f"\\x{b:02x}")
            else:
                # Printable ASCII
                if not use_quotes and ch == "'":
                    stream.write("\\'")
                elif use_quotes and ch == '"':
                    stream.write('\\"')
                elif ch == '\\':
                    stream.write("\\\\")
                elif parent_f_string_quote and ch == '{':
                    stream.write("{{")
                elif parent_f_string_quote and ch == '}':
                    stream.write("}}")
                else:
                    stream.write(ch)

        # Output end quote
        if parent_f_string_quote is None:
            if triple:
                stream.write('"""' if use_quotes else "'''")
            else:
                stream.write('"' if use_quotes else "'")