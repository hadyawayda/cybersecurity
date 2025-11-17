from __future__ import annotations
from typing import List
import os, json, base64
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

MAGIC = b"ONI1"

def _derive(passphrase: str, salt: bytes, n: int=2**14, r: int=8, p: int=1) -> bytes:
    if not isinstance(passphrase, str): raise TypeError("passphrase must be str")
    kdf = Scrypt(salt=salt, length=32, n=n, r=r, p=p)
    return kdf.derive(passphrase.encode('utf-8'))

def seal(plaintext: bytes, passphrases: List[str]) -> bytes:
    """Encrypt plaintext with N onion layers (outermost = last passphrase)."""
    if not isinstance(plaintext, (bytes, bytearray)):
        raise TypeError("plaintext must be bytes-like")
    meta = {"layers": []}
    blob = bytes(plaintext)
    for pw in passphrases:
        salt = os.urandom(16)
        nonce = os.urandom(12)
        key = _derive(pw, salt)
        blob = AESGCM(key).encrypt(nonce, blob, MAGIC)
        meta["layers"].append({"salt": base64.b64encode(salt).decode(), "nonce": base64.b64encode(nonce).decode()})
    meta_b = json.dumps(meta, separators=(',',':')).encode()
    return MAGIC + len(meta_b).to_bytes(4,'big') + meta_b + blob

def peel(blob: bytes, passphrases: List[str]) -> bytes:
    if not (isinstance(blob, (bytes, bytearray)) and len(blob) >= 8):
        raise ValueError("blob too short or wrong type")
    if blob[:4] != MAGIC: raise ValueError("bad magic or unsupported version")
    mlen = int.from_bytes(blob[4:8],'big')
    meta = json.loads(blob[8:8+mlen].decode())
    ct = blob[8+mlen:]
    layers = meta.get("layers", [])
    if len(layers) != len(passphrases):
        raise ValueError("passphrase count mismatch")
    for i in range(len(passphrases)-1, -1, -1):
        salt = base64.b64decode(layers[i]["salt"])
        nonce = base64.b64decode(layers[i]["nonce"])
        key = _derive(passphrases[i], salt)
        ct = AESGCM(key).decrypt(nonce, ct, MAGIC)
    return ct
