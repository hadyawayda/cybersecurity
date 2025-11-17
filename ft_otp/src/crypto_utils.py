from __future__ import annotations

import os
import json
import base64
import getpass
from dataclasses import dataclass
from typing import Dict, Any

from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

MAGIC = "FTOTP1"  # file format magic/version

@dataclass
class EncParams:
    """Encryption parameters stored alongside the ciphertext."""
    salt: bytes
    nonce: bytes
    n: int = 2**14
    r: int = 8
    p: int = 1
    def to_json(self) -> Dict[str, Any]:
        return {
            "magic": MAGIC,
            "salt": base64.b64encode(self.salt).decode("ascii"),
            "nonce": base64.b64encode(self.nonce).decode("ascii"),
            "n": self.n, "r": self.r, "p": self.p,
        }
    @staticmethod
    def from_json(obj: Dict[str, Any]) -> "EncParams":
        if obj.get("magic") != MAGIC:
            raise ValueError("Invalid key file format (bad magic)")
        return EncParams(
            salt=base64.b64decode(obj["salt"]), 
            nonce=base64.b64decode(obj["nonce"]),
            n=int(obj.get("n", 2**14)),
            r=int(obj.get("r", 8)),
            p=int(obj.get("p", 1)),
        )

def _derive_key(passphrase: str, salt: bytes, n: int, r: int, p: int) -> bytes:
    """Derive a 256-bit key from a passphrase using scrypt."""
    kdf = Scrypt(salt=salt, length=32, n=n, r=r, p=p)
    return kdf.derive(passphrase.encode("utf-8"))

def prompt_passphrase(confirm: bool = False, env_var: str = "FT_OTP_PASSPHRASE") -> str:
    """Obtain a passphrase from env or interactive prompt.

    Args:
        confirm: If True, ask to confirm by typing twice (for -g).
        env_var: Environment variable to check first.

    Returns:
        The passphrase string (may be empty, but discouraged).
    """
    import os
    if env_var in os.environ:
        return os.environ[env_var]
    while True:
        pw = getpass.getpass("Enter passphrase: ")
        if not confirm:
            return pw
        pw2 = getpass.getpass("Confirm passphrase: ")
        if pw == pw2:
            return pw
        print("Passphrases do not match. Try again.")

def encrypt_key(hex_key: str, passphrase: str) -> bytes:
    """Encrypt a hex-encoded key with a passphrase using AES-GCM + scrypt.

    Returns:
        The serialized JSON (UTF-8) of { params..., "ciphertext": base64 }.
    """
    if len(hex_key) % 2 != 0:
        raise ValueError("hex key length must be even")
    raw_key = bytes.fromhex(hex_key)
    salt = os.urandom(16)
    nonce = os.urandom(12)  # AES-GCM 96-bit nonce
    params = EncParams(salt=salt, nonce=nonce)
    aesgcm = AESGCM(_derive_key(passphrase, salt, params.n, params.r, params.p))
    ct = aesgcm.encrypt(nonce, raw_key, associated_data=b"ft_otp key")  # includes tag
    payload = params.to_json()
    payload["ciphertext"] = base64.b64encode(ct).decode("ascii")
    return json.dumps(payload, separators=(",", ":")).encode("utf-8")

def decrypt_key(blob: bytes, passphrase: str) -> bytes:
    """Decrypt and return the raw key bytes from a serialized JSON *blob*."""
    obj = json.loads(blob.decode("utf-8"))
    params = EncParams.from_json(obj)
    ct = base64.b64decode(obj["ciphertext"])
    aesgcm = AESGCM(_derive_key(passphrase, params.salt, params.n, params.r, params.p))
    return aesgcm.decrypt(params.nonce, ct, associated_data=b"ft_otp key")
