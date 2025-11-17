# ft_otp (HOTP/TOTP)

A clean Python implementation of HOTP (RFC 4226) and TOTP (RFC 6238) with **encrypted key storage**.

## ✨ Features

### Mandatory

- CLI executable name: `ft_otp`
- `-g <hex_key_file>`: Read a master key (>= 64 hex chars), encrypt it, and save to `ft_otp.key`.
- `-k <ft_otp.key>`: Decrypt the key and print a 6‑digit TOTP for the current time.
- Uses standard HMAC and dynamic truncation (RFC 4226) and 30s time step (RFC 6238).

### 🎁 Bonus Features

1. **QR Code Generation** (`ft_otp_qr.py`): Generate QR codes that can be scanned by authenticator apps
2. **Graphical Interface** (`ft_otp_gui.py`): User-friendly GUI with live TOTP updates and countdown timer

## 🚀 Quick Start

```bash
make install    # Install dependencies in venv
make demo       # Run demonstration
make test       # Run comprehensive tests
make gui        # Launch GUI (bonus)
make qr         # Generate QR code (bonus)
```

## Install

```bash
python -m venv .venv
source .venv/bin/activate           # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

### Command Line (Mandatory)

```bash
# Generate encrypted key file
echo -n "NEVER GONNA GIVE YOU UP" | xxd -p -c 256 > key.hex     # demo: convert to hex (not secure!)
python ft_otp.py -g key.hex                                      # will prompt for passphrase
# Key was successfully saved in ft_otp.key.

# Print current TOTP using the encrypted key
python ft_otp.py -k ft_otp.key                                   # will prompt for passphrase
# 123456
```

### QR Code Generation (Bonus)

```bash
# Generate QR code for authenticator apps
python ft_otp_qr.py -k ft_otp.key -i "MyApp" -a "user@example.com"
# Scan the generated ft_otp_qr.png with Google Authenticator, Authy, etc.
```

### Graphical Interface (Bonus)

```bash
# Launch the GUI
python ft_otp_gui.py
# Or use: make gui
```

The GUI features:

- Load encrypted key files with passphrase dialog
- Live TOTP code display with automatic refresh
- Visual countdown timer showing time remaining
- Copy to clipboard functionality
- Clean, modern interface

Non‑interactive (CI) runs can use the environment variable `FT_OTP_PASSPHRASE` to provide the passphrase.

## How it works

- **HOTP/TOTP**: `src.otp` implements HOTP and TOTP directly with `hmac`/`hashlib` and RFC dynamic truncation.
- **Key storage**: `src.crypto_utils` encrypts the raw key using AES‑256‑GCM. The AES key is derived from your
  passphrase via scrypt (`N=2^14, r=8, p=1`). The file `ft_otp.key` is a compact JSON containing:
  - magic/version (`FTOTP1`), scrypt params and salt, AES‑GCM nonce, and ciphertext+tag (base64).
- **Permissions**: on POSIX, the key file is saved with `0600` permissions.

## Validation with oathtool

You can cross‑check TOTP output with `oathtool`:

```bash
oathtool --totp $(cat key.hex)
```

> `key.hex` must contain the master key in lowercase hex without spaces.
> If you used a text string like above, ensure you converted to hex first.

## Edge cases handled

- Key file not found / unreadable
- Wrong passphrase or corrupted key file
- Non‑hex, odd length, or < 64‑char hex keys (explicit messages)
- Time step configurable in code; default 30s
- Cross‑platform (Windows / macOS / Linux)

## Project layout

```
ft_otp/
├─ ft_otp.py                   # CLI (mandatory)
├─ ft_otp_gui.py               # GUI (BONUS)
├─ ft_otp_qr.py                # QR code generator (BONUS)
├─ src/
│  ├─ __init__.py
│  ├─ otp.py                   # HOTP/TOTP (RFC 4226/6238)
│  ├─ crypto_utils.py          # scrypt + AES‑GCM key encryption
│  └─ io_utils.py              # I/O, validation, file perms
├─ requirements.txt
└─ Makefile                    # Build automation
```

## Requirements

- Python 3.9+
- `cryptography` (for AES‑GCM and scrypt)
- `qrcode` + `Pillow` (for QR code generation - bonus)

## Makefile Commands

```bash
make install    # Set up venv and install dependencies
make demo       # Run complete demonstration
make test       # Run comprehensive tests (all pass!)
make gui        # Launch graphical interface (bonus)
make qr         # Generate QR code (bonus)
make bonus      # Demo all bonus features
make clean      # Clean up all generated files
make help       # Show all available commands
```

## Security notes

- The passphrase protects your key with strong primitives (scrypt + AES‑GCM).
- For real deployments, prefer a hardware token or OS keychain/HSM.
- Do not store your passphrase in plain text; the env var is for CI only.

## References

- RFC 4226 — HMAC‑Based One‑Time Password Algorithm
- RFC 6238 — Time‑Based One‑Time Password Algorithm
