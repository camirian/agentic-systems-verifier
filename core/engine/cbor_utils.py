import struct

def encode_uint(val):
    """Encodes an unsigned integer into CBOR format."""
    if val < 24:
        return struct.pack('B', val)
    elif val < 256:
        return struct.pack('BB', 24, val)
    elif val < 65536:
        return struct.pack('>BH', 25, val)
    elif val < 4294967296:
        return struct.pack('>BI', 26, val)
    else:
        return struct.pack('>BQ', 27, val)

def encode_indefinite_array_start():
    """Encodes the start of an indefinite-length array (0x9f)."""
    return b'\x9f'

def encode_break():
    """Encodes the break stop code (0xff)."""
    return b'\xff'

def encode_byte_string(data):
    """Encodes a byte string."""
    length = len(data)
    # Major type 2 is byte string (0x40)
    if length < 24:
        header = 0x40 | length
        return struct.pack('B', header) + data
    elif length < 256:
        return struct.pack('BB', 0x40 | 24, length) + data
    elif length < 65536:
        return struct.pack('>BH', 0x40 | 25, length) + data
    elif length < 4294967296:
        return struct.pack('>BI', 0x40 | 26, length) + data
    else:
        return struct.pack('>BQ', 0x40 | 27, length) + data
