.PHONY: test run open clean install venv progress-range

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

progress-range:
	mkdir -p assets/progress-range
	for pct in $$(seq 0 100); do \
		.venv/bin/python -m atfield.cli $$pct -o assets/progress-range/progress$$pct.svg; \
	done

clean:
	rm -rf .venv __pycache__ .pytest_cache *.egg-info
	find . -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true
