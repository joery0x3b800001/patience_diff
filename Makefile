.PHONY: test install clean help

help:
	@echo "Patience Diff Python"
	@echo "  make test       - Run tests"
	@echo "  make install    - Install in dev mode"
	@echo "  make clean      - Clean artifacts"

test:
	python3 -m pytest test/ -v

install:
	pip install -e .

clean:
	rm -rf build dist *.egg-info __pycache__ .pytest_cache
