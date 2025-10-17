VENV?=.venv
PY?=$(VENV)/bin/python
PIP?=$(VENV)/bin/pip
UVICORN?=$(VENV)/bin/uvicorn

.PHONY: venv install run dev clean fmt

venv:
	python3 -m venv $(VENV)

install: venv
	$(PIP) install -U pip
	$(PIP) install -r requirements.txt

run:
	$(UVICORN) app.main:app --host 0.0.0.0 --port 8000

dev:
	$(UVICORN) app.main:app --host 0.0.0.0 --port 8000 --reload

clean:
	rm -rf $(VENV) __pycache__ */__pycache__ .pytest_cache .mypy_cache dist build .coverage .ruff_cache
