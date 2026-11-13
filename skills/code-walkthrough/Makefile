# The same checks CI runs (.github/workflows/code-walkthrough.yml).
PY ?= python3

.PHONY: check lint test examples
check: lint test

lint:
	$(PY) -m ruff check .
	$(PY) -m ruff format --check .

test:
	$(PY) -m pytest -q

# Render the bundled examples into /tmp, in both layouts.
examples:
	for f in examples/*.json; do \
	  for l in pages rail; do \
	    $(PY) scripts/walkthrough.py $$f --layout $$l -o /tmp/$$(basename $$f .json)-$$l.html; \
	  done; \
	done
