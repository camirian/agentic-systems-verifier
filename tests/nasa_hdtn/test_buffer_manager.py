import unittest
import sys
import os

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, '../')
sys.path.append(project_root)

from examples.nasa_hdtn.buffer_manager import BufferManager
from core.engine import cbor_utils

class TestBufferManager(unittest.TestCase):
    def setUp(self):
        self.manager = BufferManager()

    def test_bpv6_creation_and_serialization(self):
        """Verify BPv6 Bundle creation and serialization."""
        source = (1, 1)
        dest = (2, 2)
        payload = b"Hello BPv6"
        bundle = self.manager.create_bundle_v6(source, dest, payload)
        
        serialized = bundle.serialize()
        
        # Verify Primary Block Version (0x06)
        self.assertEqual(serialized[0], 0x06)
        
        # Verify payload is at the end
        self.assertTrue(serialized.endswith(payload))

    def test_bpv7_creation_and_serialization(self):
        """Verify BPv7 Bundle creation and serialization."""
        source = (10, 1)
        dest = (20, 2)
        payload = b"Hello BPv7"
        bundle = self.manager.create_bundle_v7(source, dest, payload)
        
        serialized = bundle.serialize()
        
        # Verify Indefinite Array Start (0x9f)
        self.assertEqual(serialized[0], 0x9f)
        
        # Verify Break Stop Code (0xff) at end
        self.assertEqual(serialized[-1], 0xff)
        
        # Verify Primary Block is first (0x88 for array of 8)
        self.assertEqual(serialized[1], 0x88)

    def test_cbor_utils(self):
        """Verify CBOR encoding utilities."""
        self.assertEqual(cbor_utils.encode_uint(5), b'\x05')
        self.assertEqual(cbor_utils.encode_break(), b'\xff')

if __name__ == '__main__':
    unittest.main()
