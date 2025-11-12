from __future__ import annotations

import hmac
import time
import struct
import hashlib
from typing import Optional

# RFCs:
# - HOTP: RFC 4226 (HMAC-Based One-Time Password Algorithm)
# - TOTP: RFC 6238 (Time-Based One-Time Password Algorithm, built on HOTP)

def _int_to_bytes(counter: int) -> bytes:
    """Convert an integer *counter* to an 8-byte big-endian buffer (RFC 4226 §5.3)."""
    return struct.pack(">Q", counter)

def hotp(key: bytes, counter: int, digits: int = 6, algo: str = "sha1") -> str:
    """Compute HOTP value per RFC 4226 using dynamic truncation.

    Args:
        key: Secret key as raw bytes.
        counter: Moving factor (integer).
        digits: Number of output digits (usually 6 or 8).
        algo: Hash algorithm ("sha1", "sha256", or "sha512").

    Returns:
        Zero-padded numeric code as a string of length *digits*.

    Implementation details:
        - HS = HMAC-ALGO(key, counter_as_8byte_big_endian)
        - Truncate dynamically to 31-bit code per RFC 4226 §5.3.
        - Return code mod 10^digits, zero-padded.
    """
    if digits <= 0:
        raise ValueError("digits must be positive")
    algo = algo.lower()
    if algo not in ("sha1", "sha256", "sha512"):  # RFC 6238 allows these
        raise ValueError("algo must be one of: sha1, sha256, sha512")
    counter_bytes = _int_to_bytes(counter)
    hm = hmac.new(key, counter_bytes, getattr(hashlib, algo)).digest()
    offset = hm[-1] & 0x0F
    # 31-bit dynamic truncation
    code = ((hm[offset] & 0x7f) << 24) | (hm[offset + 1] << 16) | (hm[offset + 2] << 8) | (hm[offset + 3])
    otp_int = code % (10 ** digits)
    return f"{otp_int:0{digits}d}"

def totp(
    key: bytes,
    digits: int = 6,
    period: int = 30,
    t0: int = 0,
    for_time: Optional[int] = None,
    algo: str = "sha1",
) -> str:
    """Compute TOTP per RFC 6238 using HOTP(key, counter) with time-based counter.

    Args:
        key: Secret key in raw bytes.
        digits: Code length (default 6).
        period: Time step X in seconds (default 30s per RFC 6238).
        t0: Unix time to start counting from (default 0).
        for_time: If provided, generate TOTP for this Unix timestamp; else use time.time().
        algo: Hash algorithm ("sha1" default per RFC, "sha256"/"sha512" also supported).

    Returns:
        Zero-padded numeric TOTP string of length *digits*.

    Raises:
        ValueError for invalid parameters.

    Note:
        The moving factor is C = floor((T - T0) / X), RFC 6238 §4.
    """
    if period <= 0:
        raise ValueError("period must be positive seconds")
    if for_time is None:
        T = int(time.time())
    else:
        if for_time < 0:
            raise ValueError("for_time must be a non-negative Unix timestamp")
        T = int(for_time)
    counter = (T - t0) // period
    return hotp(key, counter, digits=digits, algo=algo)
