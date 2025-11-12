#!/usr/bin/env python3
"""ft_otp_qr — Generate QR code for TOTP setup (BONUS feature).

Usage:
    ./ft_otp_qr.py -k <encrypted_key_file> [-i <issuer>] [-a <account>] [-o <output.png>]

This generates a QR code that can be scanned by authenticator apps like:
- Google Authenticator
- Microsoft Authenticator  
- Authy
- etc.

The QR code contains an otpauth:// URI with the TOTP parameters.
"""
from __future__ import annotations

import sys
import argparse
import base64
import urllib.parse
from ft_otp_pkg.crypto_utils import prompt_passphrase, decrypt_key
from ft_otp_pkg.io_utils import read_bytes

try:
    import qrcode
except ImportError:
    print("Error: qrcode library not installed. Run: pip install qrcode[pil]", file=sys.stderr)
    sys.exit(1)

def generate_otpauth_uri(
    secret: bytes,
    issuer: str = "ft_otp",
    account: str = "user@example.com",
    algorithm: str = "SHA1",
    digits: int = 6,
    period: int = 30,
) -> str:
    """Generate an otpauth:// URI for TOTP.
    
    Args:
        secret: Raw secret key bytes
        issuer: Service name (e.g., "MyApp")
        account: User account identifier (e.g., "user@example.com")
        algorithm: Hash algorithm (SHA1, SHA256, SHA512)
        digits: Number of OTP digits (default 6)
        period: Time step in seconds (default 30)
    
    Returns:
        otpauth:// URI string
    """
    # Encode secret as base32 (standard for TOTP URIs)
    secret_b32 = base64.b32encode(secret).decode('ascii').rstrip('=')
    
    # Build the label (issuer:account)
    label = f"{issuer}:{account}"
    
    # Build query parameters
    params = {
        'secret': secret_b32,
        'issuer': issuer,
        'algorithm': algorithm.upper(),
        'digits': str(digits),
        'period': str(period),
    }
    
    query_string = urllib.parse.urlencode(params)
    uri = f"otpauth://totp/{urllib.parse.quote(label)}?{query_string}"
    
    return uri

def generate_qr_code(uri: str, output_path: str = "ft_otp_qr.png") -> None:
    """Generate a QR code image from the otpauth URI.
    
    Args:
        uri: otpauth:// URI
        output_path: Path to save the QR code image
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(output_path)
    print(f"QR code saved to: {output_path}")
    print(f"\nScan this QR code with your authenticator app to add the account.")

def main():
    parser = argparse.ArgumentParser(
        description="Generate TOTP QR code for authenticator apps (BONUS feature)"
    )
    parser.add_argument("-k", "--key", required=True, metavar="FILE",
                       help="Encrypted key file (e.g., ft_otp.key)")
    parser.add_argument("-i", "--issuer", default="ft_otp",
                       help="Issuer/service name (default: ft_otp)")
    parser.add_argument("-a", "--account", default="user@example.com",
                       help="Account identifier (default: user@example.com)")
    parser.add_argument("-o", "--output", default="ft_otp_qr.png",
                       help="Output QR code image path (default: ft_otp_qr.png)")
    parser.add_argument("--show-uri", action="store_true",
                       help="Print the otpauth:// URI")
    
    args = parser.parse_args()
    
    # Read and decrypt the key file
    try:
        blob = read_bytes(args.key)
    except Exception as e:
        print(f"Error: cannot read key file: {e}", file=sys.stderr)
        return 2
    
    passphrase = prompt_passphrase(confirm=False)
    try:
        raw_key = decrypt_key(blob, passphrase)
    except Exception as e:
        print(f"Error: wrong passphrase or corrupt key file ({e})", file=sys.stderr)
        return 3
    
    # Generate otpauth URI
    uri = generate_otpauth_uri(
        secret=raw_key,
        issuer=args.issuer,
        account=args.account,
        algorithm="SHA1",
        digits=6,
        period=30,
    )
    
    if args.show_uri:
        print(f"\notpauth URI:\n{uri}\n")
    
    # Generate QR code
    try:
        generate_qr_code(uri, args.output)
    except Exception as e:
        print(f"Error: failed to generate QR code: {e}", file=sys.stderr)
        return 4
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
