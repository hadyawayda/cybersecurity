#!/usr/bin/env python3
"""ft_otp — Time-based One-Time Password generator (RFC 6238 built on HOTP RFC 4226).

Usage:
    ./ft_otp -g <hex_key_file>
        Read a hex master key (>= 64 hex chars) from file, encrypt it with a passphrase,
        and store it in ./ft_otp.key

    ./ft_otp -k <encrypted_key_file>
        Decrypt the stored key (passphrase required) and print a 6-digit TOTP for now.

Environment:
    FT_OTP_PASSPHRASE  If set, used as passphrase for -g and -k (non-interactive).

Notes:
    - Uses TOTP with 30s time step and 6 digits (default RFC parameters).
    - Key file is AES-256-GCM encrypted using a key derived by scrypt (N=2^14, r=8, p=1).
"""
from __future__ import annotations

import sys
import argparse
from ft_otp_pkg.io_utils import read_hex_key_file, validate_hex_key, secure_write, read_bytes
from ft_otp_pkg.crypto_utils import prompt_passphrase, encrypt_key, decrypt_key
from ft_otp_pkg.otp import totp

DEFAULT_KEY_PATH = "ft_otp.key"

def cmd_generate(hex_path: str, out_path: str = DEFAULT_KEY_PATH) -> int:
    """Handle -g: read hex key, validate, encrypt, save to ft_otp.key.

    Returns:
        Exit status code (0 ok, non-zero error).
    """
    try:
        hex_key = read_hex_key_file(hex_path)
        validate_hex_key(hex_key, min_len=64)
    except Exception as e:
        print(f"./ft_otp: error: {e}")
        return 2

    pw = prompt_passphrase(confirm=True)
    try:
        blob = encrypt_key(hex_key, pw)
        secure_write(out_path, blob)
    except Exception as e:
        print(f"./ft_otp: error: failed to encrypt/save key: {e}")
        return 3

    print("Key was successfully saved in ft_otp.key.")
    return 0

def cmd_code(enc_path: str) -> int:
    """Handle -k: decrypt key file and print 6-digit TOTP for current time."""
    try:
        blob = read_bytes(enc_path)
    except Exception as e:
        print(f"./ft_otp: error: cannot read key file: {e}")
        return 2

    pw = prompt_passphrase(confirm=False)
    try:
        raw_key = decrypt_key(blob, pw)
    except Exception as e:
        print(f"./ft_otp: error: wrong passphrase or corrupt key file ({e})")
        return 3

    code = totp(raw_key, digits=6, period=30, algo="sha1")
    print(code)
    return 0

def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(add_help=False)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-g", dest="gen_path", metavar="FILE", help="read hex key from FILE and save encrypted ft_otp.key")
    group.add_argument("-k", dest="key_path", metavar="FILE", help="read encrypted key from FILE and print current TOTP")
    parser.add_argument("-o", dest="out_path", default=DEFAULT_KEY_PATH, help="output path for -g (default: ft_otp.key)")
    parser.add_argument("-h", "--help", action="help", help="show this help message and exit")
    return parser.parse_args(argv)

def main(argv: list[str] | None = None) -> int:
    ns = parse_args(sys.argv[1:] if argv is None else argv)
    if ns.gen_path:
        return cmd_generate(ns.gen_path, ns.out_path)
    else:
        return cmd_code(ns.key_path)

if __name__ == "__main__":
    raise SystemExit(main())
