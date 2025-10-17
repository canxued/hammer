VENV?=.venv
PY?=$(VENV)/bin/python
PIP?=$(VENV)/bin/pip
UVICORN?=$(VENV)/bin/uvicorn

.PHONY: venv install run dev clean fmt

venv:
	python3 -m venv $(VENV)

install: ## install dependencies (user space if venv not available)
	@python3 -m venv $(VENV) 2>/dev/null || true
	@if [ -x "$(PIP)" ]; then \
		$(PIP) install -U pip; \
		$(PIP) install -r requirements.txt; \
	else \
		python3 -m pip install --user -r requirements.txt; \
	fi

run: ## run server
	@if [ -x "$(UVICORN)" ]; then \
		$(UVICORN) app.main:app --host 0.0.0.0 --port 8000; \
	else \
		~/.local/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000; \
	fi

dev: ## run server with reload
	@if [ -x "$(UVICORN)" ]; then \
		$(UVICORN) app.main:app --host 0.0.0.0 --port 8000 --reload; \
	else \
		~/.local/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload; \
	fi

clean:
	rm -rf $(VENV) __pycache__ */__pycache__ .pytest_cache .mypy_cache dist build .coverage .ruff_cache
