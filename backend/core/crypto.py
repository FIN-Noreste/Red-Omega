# backend/core/crypto.py
from cryptography.hazmat.primitives.asymmetric import ed25519

def verify_ed25519_signature(public_key_hex, signature_hex, message_string):
    try:
        public_key_bytes = bytes.fromhex(public_key_hex)
        signature_bytes = bytes.fromhex(signature_hex)
        public_key = ed25519.Ed25519PublicKey.from_public_bytes(public_key_bytes)
        public_key.verify(signature_bytes, message_string.encode('utf-8'))
        return True
    except Exception:
        return False