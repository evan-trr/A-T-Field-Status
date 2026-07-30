.PHONY: test run open clean install venv

venv:
	python3 -m venv .venv
	.venv/bin/pip install -e .
	.venv/bin/pip install pytest

install: venv

test:
	.venv/bin/python -m pytest tests/ -v

run:
	.venv/bin/atfield $(ARGS)

open:
	.venv/bin/atfield $(ARGS) > /tmp/atfield.svg && open /tmp/atfield.svg

clean:
	rm -rf .venv __pycache__ .pytest_cache *.egg-info
	find . -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true
