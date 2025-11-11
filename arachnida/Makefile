.PHONY: install clean
VENV=.venv
install:
	py -m venv $(VENV)
	pip install -U pip
	pip install -r requirements.txt
clean:
	rm -rf $(VENV) __pycache__ arachnida/__pycache__
