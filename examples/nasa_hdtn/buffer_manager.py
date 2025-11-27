import json
import os
import sys

# Add core to path for imports if running from example dir
current_dir = os.path.dirname(os.path.abspath(__file__))
core_path = os.path.join(current_dir, '../../')
if core_path not in sys.path:
    sys.path.append(core_path)

from core.engine.base_bundle import BaseBundle
from core.engine import cbor_utils

class BufferManager:
    def __init__(self):
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        self.bundles = []

    def create_bundle_v6(self, source, dest, payload):
        """Creates and stores a BPv6 bundle using generic engine."""
        # Prepare data dictionary matching config fields
        data = {
            "source_node": source[0],
            "source_service": source[1],
            "dest_node": dest[0],
            "dest_service": dest[1],
            "report_to_node": 0,
            "report_to_service": 0,
            "custodian_node": 0,
            "custodian_service": 0,
            "payload": payload
        }
        
        bundle = BaseBundle(self.config['bpv6'], data)
        self.bundles.append(bundle)
        return bundle

    def create_bundle_v7(self, source, dest, payload):
        """Creates and stores a BPv7 bundle using generic engine."""
        # Helper to encode EID for BPv7 (as BaseBundle expects pre-encoded bytes for complex types in this prototype)
        def encode_eid(node, service):
            # ipn scheme = 2
            inner = b'\x82' + cbor_utils.encode_uint(node) + cbor_utils.encode_uint(service)
            return b'\x82' + cbor_utils.encode_uint(2) + inner

        data = {
            "dest_eid": encode_eid(dest[0], dest[1]),
            "source_eid": encode_eid(source[0], source[1]),
            "report_to_eid": encode_eid(0, 0),
            "payload": payload
        }
        
        bundle = BaseBundle(self.config['bpv7'], data)
        self.bundles.append(bundle)
        return bundle

