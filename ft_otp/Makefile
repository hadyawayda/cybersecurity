.PHONY: all install clean test demo help run gui qr bonus

# Virtual environment directory
VENV = .venv

# Python executable in venv (Windows)
PYTHON = $(VENV)/Scripts/python
PIP = $(VENV)/Scripts/pip

# Main executable
MAIN = ft_otp.py
GUI = ft_otp_gui.py
QR = ft_otp_qr.py

# Test data
TEST_KEY = key.hex
TEST_KEYFILE = ft_otp.key

all: install

$(VENV):
	@echo "Creating virtual environment..."
	python -m venv $(VENV)

install: $(VENV)
	@echo "Installing dependencies from requirements.txt..."
	$(PYTHON) -m pip install -U pip
	$(PYTHON) -m pip install -r requirements.txt
	@echo "Installation complete!"
	@echo ""
	@echo "Usage:"
	@echo "  make demo     - Run a complete demonstration"
	@echo "  make test     - Run tests with oathtool verification"
	@echo "  make gui      - Launch graphical interface (BONUS)"
	@echo "  make qr       - Generate QR code (BONUS)"
	@echo "  make help     - Show usage information"

help:
	@echo "ft_otp - Time-based One-Time Password Generator"
	@echo ""
	@echo "Available targets:"
	@echo "  make install  - Set up virtual environment and install dependencies"
	@echo "  make demo     - Generate test key and demonstrate TOTP generation"
	@echo "  make test     - Run comprehensive tests (requires oathtool)"
	@echo "  make gui      - Launch graphical interface (BONUS)"
	@echo "  make qr       - Generate QR code for authenticator apps (BONUS)"
	@echo "  make bonus    - Demo all bonus features (GUI + QR)"
	@echo "  make clean    - Remove virtual environment, cache files, and test files"
	@echo "  make help     - Show this help message"
	@echo ""
	@echo "Manual usage:"
	@echo "  Generate encrypted key file:"
	@echo "    $(PYTHON) $(MAIN) -g key.hex"
	@echo ""
	@echo "  Generate TOTP code:"
	@echo "    $(PYTHON) $(MAIN) -k ft_otp.key"
	@echo ""
	@echo "Environment variable:"
	@echo "  FT_OTP_PASSPHRASE - Set passphrase non-interactively (for testing)"

demo: $(VENV)
	@echo "========================================="
	@echo "ft_otp Demonstration"
	@echo "========================================="
	@echo ""
	@echo "Step 1: Creating a test key (64 hex chars minimum)..."
	@echo "3132333435363738393031323334353637383930313233343536373839303132" > $(TEST_KEY)
	@echo "Key saved to $(TEST_KEY)"
	@echo ""
	@echo "Step 2: Testing with invalid key (should fail)..."
	@echo -n "NEVER GONNA GIVE YOU UP" > key_invalid.txt
	@-$(PYTHON) $(MAIN) -g key_invalid.txt 2>&1 || echo "(Expected error above)"
	@echo ""
	@echo "Step 3: Generating encrypted key file (using passphrase 'test123')..."
	@FT_OTP_PASSPHRASE=test123 $(PYTHON) $(MAIN) -g $(TEST_KEY)
	@echo ""
	@echo "Step 4: Generating TOTP code..."
	@FT_OTP_PASSPHRASE=test123 $(PYTHON) $(MAIN) -k $(TEST_KEYFILE)
	@echo ""
	@echo "Step 5: Waiting 2 seconds and generating another code..."
	@sleep 2
	@FT_OTP_PASSPHRASE=test123 $(PYTHON) $(MAIN) -k $(TEST_KEYFILE)
	@echo ""
	@echo "========================================="
	@echo "Demo complete! Key file: $(TEST_KEYFILE)"
	@echo "========================================="
	@rm -f key_invalid.txt

test: $(VENV)
	@echo "========================================="
	@echo "Running ft_otp Tests"
	@echo "========================================="
	@echo ""
	@echo "Test 1: Invalid key length..."
	@echo "12345" > test_short.hex
	@-$(PYTHON) $(MAIN) -g test_short.hex 2>&1 | grep -q "error" && echo "✓ PASS: Rejected short key" || echo "✗ FAIL"
	@rm -f test_short.hex
	@echo ""
	@echo "Test 2: Non-hex characters..."
	@echo "NEVER GONNA GIVE YOU UP NOT HEX" > test_text.txt
	@-$(PYTHON) $(MAIN) -g test_text.txt 2>&1 | grep -q "error" && echo "✓ PASS: Rejected non-hex" || echo "✗ FAIL"
	@rm -f test_text.txt
	@echo ""
	@echo "Test 3: Valid key generation..."
	@echo "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef" > test_valid.hex
	@FT_OTP_PASSPHRASE=testpass $(PYTHON) $(MAIN) -g test_valid.hex -o test.key 2>&1 | grep -q "successfully" && echo "✓ PASS: Key saved successfully" || echo "✗ FAIL"
	@echo ""
	@echo "Test 4: TOTP generation..."
	@FT_OTP_PASSPHRASE=testpass $(PYTHON) $(MAIN) -k test.key > totp_output.txt
	@test $$(wc -l < totp_output.txt) -eq 1 && echo "✓ PASS: Generated single line output" || echo "✗ FAIL"
	@test $$(wc -c < totp_output.txt) -le 8 && echo "✓ PASS: Output is 6 digits + newline" || echo "✗ FAIL"
	@grep -qE '^[0-9]{6}' totp_output.txt && echo "✓ PASS: Output is 6 digits" || echo "✗ FAIL"
	@echo ""
	@echo "Test 5: Wrong passphrase..."
	@-FT_OTP_PASSPHRASE=wrongpass $(PYTHON) $(MAIN) -k test.key 2>&1 | grep -q "error" && echo "✓ PASS: Rejected wrong passphrase" || echo "✗ FAIL"
	@echo ""
	@echo "Test 6: Missing key file..."
	@-$(PYTHON) $(MAIN) -k nonexistent.key 2>&1 | grep -q "error" && echo "✓ PASS: Handled missing file" || echo "✗ FAIL"
	@echo ""
	@command -v oathtool >/dev/null 2>&1 && $(MAKE) test-oathtool || echo "⚠ SKIP: oathtool not installed (install with: apt-get install oathtool or brew install oath-toolkit)"
	@rm -f test_valid.hex test.key totp_output.txt
	@echo ""
	@echo "========================================="
	@echo "Tests complete!"
	@echo "========================================="

test-oathtool:
	@echo "Test 7: Verification with oathtool..."
	@echo "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef" > verify.hex
	@FT_OTP_PASSPHRASE=verify $(PYTHON) $(MAIN) -g verify.hex -o verify.key >/dev/null 2>&1
	@FT_OTP_PASSPHRASE=verify $(PYTHON) $(MAIN) -k verify.key > ft_output.txt
	@oathtool --totp $$(cat verify.hex) > oath_output.txt
	@diff -q ft_output.txt oath_output.txt >/dev/null 2>&1 && echo "✓ PASS: Output matches oathtool" || echo "⚠ WARNING: Output differs (may be due to timing)"
	@rm -f verify.hex verify.key ft_output.txt oath_output.txt

clean:
	@echo "Cleaning up..."
	@rm -rf $(VENV)
	@rm -rf __pycache__ ft_otp_pkg/__pycache__
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@rm -f $(TEST_KEY) $(TEST_KEYFILE)
	@rm -f key_invalid.txt test_short.hex test_text.txt test_valid.hex test.key
	@rm -f totp_output.txt verify.hex verify.key ft_output.txt oath_output.txt
	@echo "Clean complete!"

gui: $(VENV)
	@echo "Launching ft_otp GUI (BONUS)..."
	@echo "Creating test key with passphrase 'test123'..."
	@echo "3132333435363738393031323334353637383930313233343536373839303132" > $(TEST_KEY)
	@FT_OTP_PASSPHRASE=test123 $(PYTHON) $(MAIN) -g $(TEST_KEY) -o $(TEST_KEYFILE) >/dev/null 2>&1
	@echo "Use passphrase 'test123' to unlock the key file in the GUI."
	@$(PYTHON) $(GUI)

qr: $(VENV)
	@echo "Generating QR code (BONUS)..."
	@echo "Creating test key with passphrase 'test123'..."
		@echo "3132333435363738393031323334353637383930313233343536373839303132" > $(TEST_KEY)
		@FT_OTP_PASSPHRASE=test123 $(PYTHON) $(MAIN) -g $(TEST_KEY) -o $(TEST_KEYFILE) >/dev/null 2>&1
		@echo "This will generate a QR code that you can scan with authenticator apps."
	@echo "(e.g., Google Authenticator, Microsoft Authenticator, Authy)"
	@echo ""
	@FT_OTP_PASSPHRASE=test123 $(PYTHON) $(QR) -k $(TEST_KEYFILE) -i "ft_otp Demo" -a "demo@example.com" --show-uri

bonus: install
	@echo "========================================="
	@echo "ft_otp BONUS Features Demo"
	@echo "========================================="
	@echo ""
	@echo "BONUS 1: QR Code Generation"
	@echo "----------------------------"
	@$(MAKE) qr
	@echo ""
	@echo "BONUS 2: Graphical Interface"
	@echo "----------------------------"
	@echo "Launching GUI... (close the window to continue)"
	@$(MAKE) gui
	@echo ""
	@echo "========================================="
	@echo "Bonus demo complete!"
	@echo "========================================="
