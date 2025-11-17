from __future__ import annotations

import os

def read_hex_key_file(path: str) -> str:
    """Read a file that contains a hex string (may include whitespace/newlines)."""
    with open(path, "r", encoding="utf-8") as f:
        data = f.read().strip()
    # Allow whitespace by filtering only hex chars
    filtered = ''.join(ch for ch in data if ch in '0123456789abcdefABCDEF')
    return filtered

def validate_hex_key(hex_key: str, min_len: int = 64) -> None:
    """Validate that *hex_key* has only hex chars, even length, and length >= min_len."""
    if any(ch not in '0123456789abcdefABCDEF' for ch in hex_key):
        raise ValueError("key must be hexadecimal characters only")
    if len(hex_key) % 2 != 0:
        raise ValueError("key length must be even number of chars (pairs of hex)")
    if len(hex_key) < min_len:
        raise ValueError(f"key must be at least {min_len} hexadecimal characters") 

def secure_write(path: str, data: bytes) -> None:
    """Write *data* to *path*, restricting permissions on POSIX to 0600."""
    with open(path, "wb") as f:
        f.write(data)
    if os.name == "posix":
        os.chmod(path, 0o600)

def read_bytes(path: str) -> bytes:
    with open(path, "rb") as f:
        return f.read()
