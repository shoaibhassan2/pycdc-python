import struct
import sys
from typing import IO, Optional, Union

class PycData:
    """Abstract base class for reading Python bytecode data."""
    
    def is_open(self) -> bool:
        raise NotImplementedError

    def at_eof(self) -> bool:
        raise NotImplementedError

    def get_byte(self) -> int:
        raise NotImplementedError

    def get_buffer(self, bytes_count: int) -> bytes:
        raise NotImplementedError

    def get16(self) -> int:
        """Reads a 16-bit little-endian unsigned integer."""
        b1 = self.get_byte()
        b2 = self.get_byte()
        if b1 == -1 or b2 == -1:
             # Handle EOF or error appropriately, C++ implementation often assumes valid input or returns partial
             # In C++: result |= (getByte() & 0xFF) << 8; [cite: 374]
             pass 
        return (b1 & 0xFF) | ((b2 & 0xFF) << 8)

    def get32(self) -> int:
        """Reads a 32-bit little-endian unsigned integer."""
        # [cite: 375-376]
        b1 = self.get_byte()
        b2 = self.get_byte()
        b3 = self.get_byte()
        b4 = self.get_byte()
        return (b1 & 0xFF) | ((b2 & 0xFF) << 8) | ((b3 & 0xFF) << 16) | ((b4 & 0xFF) << 24)

    def get64(self) -> int:
        """Reads a 64-bit little-endian unsigned integer."""
        # [cite: 377-380]
        lo = self.get32()
        hi = self.get32()
        return (lo & 0xFFFFFFFF) | ((hi & 0xFFFFFFFF) << 32)


class PycFile(PycData):
    """Implementation of PycData for reading from a file."""
    
    def __init__(self, filename: str):
        try:
            self.m_stream: Optional[IO[bytes]] = open(filename, "rb")
        except OSError:
            self.m_stream = None

    def __del__(self):
        if self.m_stream:
            self.m_stream.close()

    def is_open(self) -> bool:
        return self.m_stream is not None

    def at_eof(self) -> bool:
        if not self.m_stream:
            return True
        # Check for EOF by peeking
        current_pos = self.m_stream.tell()
        b = self.m_stream.read(1)
        if not b:
            return True
        self.m_stream.seek(current_pos)
        return False

    def get_byte(self) -> int:
        if not self.m_stream:
            return -1
        b = self.m_stream.read(1)
        if not b:
            return -1 # EOF
        return b[0]

    def get_buffer(self, bytes_count: int) -> bytes:
        if not self.m_stream:
            return b""
        return self.m_stream.read(bytes_count)


class PycBuffer(PycData):
    """Implementation of PycData for reading from a memory buffer."""

    def __init__(self, buffer: bytes):
        self.m_buffer = buffer
        self.m_size = len(buffer)
        self.m_pos = 0

    def is_open(self) -> bool:
        return self.m_buffer is not None

    def at_eof(self) -> bool:
        return self.m_pos >= self.m_size

    def get_byte(self) -> int:
        if self.at_eof():
            return -1
        ch = self.m_buffer[self.m_pos]
        self.m_pos += 1
        return ch

    def get_buffer(self, bytes_count: int) -> bytes:
        if self.m_pos + bytes_count > self.m_size:
            bytes_count = self.m_size - self.m_pos
        
        if bytes_count <= 0:
            return b""
            
        result = self.m_buffer[self.m_pos : self.m_pos + bytes_count]
        self.m_pos += bytes_count
        return result

# Formatted print helper functions usually map to print() or file.write() in Python
def formatted_print(stream: IO[str], format_str: str, *args):
    # [cite: 388-392]
    # Python's string formatting is powerful enough to handle most C-style formats
    # usually via % operator or f-strings.
    # Note: C++ uses vsnprintf style formatting.
    try:
        stream.write(format_str % args)
    except TypeError:
        # Fallback if format string doesn't match args directly
        stream.write(format_str + " " + str(args))