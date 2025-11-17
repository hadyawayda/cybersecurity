.PHONY: install test clean
VENV?=.venv
PY=$(VENV)/bin/python
PIP=$(VENV)/bin/pip
install:
	python3 -m venv $(VENV)
	$(PIP) install -U pip
	$(PIP) install -r requirements.txt
test:
	$(PY) -m pip install pytest
	$(PY) -m pytest -q
clean:
	rm -rf $(VENV) __pycache__ src/**/__pycache__ .pytest_cache
