.PHONY: install clean all

# Virtual environment directory
VENV = .venv

# Python executable in venv (Windows)
PYTHON = $(VENV)/Scripts/python

# Pip executable in venv (Windows)
PIP = $(VENV)/Scripts/pip

$(VENV):
	@echo "Creating virtual environment..."
	python -m venv $(VENV)

all: install

install: $(VENV)
	@echo "Installing dependencies from requirements.txt..."
	$(PYTHON) -m pip install -U pip
	$(PYTHON) -m pip install -r requirements.txt
	@echo "Installation complete!"

clean:
	@echo "Cleaning up..."
	rm -rf $(VENV)
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	@echo "Clean complete!"
