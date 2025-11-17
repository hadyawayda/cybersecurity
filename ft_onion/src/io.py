from __future__ import annotations
import os

def read_bytes(path: str) -> bytes:
    with open(path, 'rb') as f:
        return f.read()

def write_bytes(path: str, data: bytes) -> None:
    tmp = path + '.tmp'
    with open(tmp, 'wb') as f:
        f.write(data)
    os.replace(tmp, path)
