import time
import struct
from . import cbor_utils

class BaseBundle:
    def __init__(self, config, data):
        """
        Initialize a generic bundle.
        :param config: Dictionary containing protocol configuration (from config.json).
        :param data: Dictionary containing bundle data (fields matching config).
        """
        self.config = config
        self.data = data
        
        # Set common attributes
        self.version = config.get('version')
        self.payload = data.get('payload', b"")
        
        # Handle timestamp if not provided
        if 'creation_timestamp' not in data:
            time_offset = config.get('time_offset', 0)
            self.data['creation_timestamp'] = int(time.time() - time_offset)
            self.data['sequence_number'] = 0
        
        # Set default lifetime if not provided
        if 'lifetime' not in data:
            self.data['lifetime'] = config.get('default_lifetime', 3600)

    def serialize(self):
        encoding = self.config.get('encoding')
        if encoding == 'sdnv_cbhe':
            return self._serialize_sdnv_cbhe()
        elif encoding == 'cbor':
            return self._serialize_cbor()
        else:
            raise ValueError(f"Unknown encoding: {encoding}")

    def _encode_sdnv(self, val):
        """Encodes a value as an SDNV (Self-Delimiting Numeric Value)."""
        if val == 0:
            return b'\x00'
        
        output = []
        while val > 0:
            byte = val & 0x7F
            val >>= 7
            if output:
                byte |= 0x80
            output.append(byte)
        return bytes(reversed(output))

    def _serialize_sdnv_cbhe(self):
        """Serializes using SDNVs and Compressed Bundle Header Encoding (BPv6 style)."""
        # Primary Block
        data = b'\x06' # Version 6 fixed for now, or use self.version encoded? 
        # BPv6 spec says version is 1 byte.
        
        # Serialize fields defined in config
        header_content = b""
        fields = self.config.get('primary_block', {}).get('fields', [])
        
        # Special handling for proc_flags if not in data (default 0)
        if 'proc_flags' not in self.data:
            header_content += self._encode_sdnv(0)
        else:
            header_content += self._encode_sdnv(self.data['proc_flags'])

        # Iterate over configured fields (skipping proc_flags as we just did it? 
        # config.json for bpv6 didn't have proc_flags in the list, let's check.
        # It started with dest_node. 
        # BPv6 structure: Version, Proc Flags, Block Length, [Fields...]
        # My config.json "fields" list started with dest_node.
        # So I need to handle Proc Flags and Block Length manually or add them to config.
        # For this prototype, I'll handle the structure wrapper here and fields inside.
        
        # Block Length is calculated later.
        
        for field in fields:
            val = self.data.get(field, 0)
            header_content += self._encode_sdnv(val)
            
        # Block Length (length of header_content)
        data += self._encode_sdnv(len(header_content))
        data += header_content
        
        # Payload Block
        payload_block = b'\x01' # Type
        payload_block += self._encode_sdnv(0x02) # Flags (Last block)
        payload_block += self._encode_sdnv(len(self.payload))
        payload_block += self.payload
        
        return data + payload_block

    def _serialize_cbor(self):
        """Serializes using CBOR (BPv7 style)."""
        data = cbor_utils.encode_indefinite_array_start()
        
        # Primary Block
        pb_fields = []
        
        # Fields from config
        fields = self.config.get('primary_block', {}).get('fields', [])
        
        for field in fields:
            val = self.data.get(field)
            
            if field == 'version':
                pb_fields.append(cbor_utils.encode_uint(self.version))
            elif field == 'proc_flags':
                pb_fields.append(cbor_utils.encode_uint(val if val is not None else 0))
            elif field == 'crc_type':
                pb_fields.append(cbor_utils.encode_uint(val if val is not None else 0))
            elif 'eid' in field:
                # Expecting val to be pre-encoded bytes for EID, or a tuple?
                # If buffer_manager prepares it as bytes, we just append.
                # If it's a tuple/list, we need to encode it.
                # Let's assume buffer_manager passes pre-encoded bytes for complex types for now,
                # or we handle it here.
                if isinstance(val, bytes):
                    pb_fields.append(val)
                else:
                    # Fallback or error
                    pb_fields.append(cbor_utils.encode_uint(0)) 
            elif field == 'creation_timestamp_array':
                # Expecting [time, seq]
                ts = self.data.get('creation_timestamp')
                seq = self.data.get('sequence_number')
                encoded_ts = b'\x82' + cbor_utils.encode_uint(ts) + cbor_utils.encode_uint(seq)
                pb_fields.append(encoded_ts)
            elif field == 'lifetime':
                pb_fields.append(cbor_utils.encode_uint(val))
            else:
                # Default uint encoding
                pb_fields.append(cbor_utils.encode_uint(val if val is not None else 0))

        # Primary Block Array Header
        pb_header = struct.pack('B', 0x80 + len(pb_fields)) # Simple array header for short arrays
        pb_data = pb_header + b"".join(pb_fields)
        data += pb_data
        
        # Payload Block (Simplified for prototype)
        pay_fields = []
        pay_fields.append(cbor_utils.encode_uint(1)) # Type
        pay_fields.append(cbor_utils.encode_uint(1)) # Block Number
        pay_fields.append(cbor_utils.encode_uint(0)) # Flags
        pay_fields.append(cbor_utils.encode_uint(0)) # CRC Type
        pay_fields.append(cbor_utils.encode_byte_string(self.payload))
        
        pay_header = b'\x85'
        pay_data = pay_header + b"".join(pay_fields)
        data += pay_data
        
        data += cbor_utils.encode_break()
        return data
