.DEFAULT_GOAL := help

.PHONY: help install install-lite install-mps install-cuda hooks lock sync test test-cov lint fmt fmt-check typecheck check docs docs-build notebook cli clean clean-venv native-build

help: ## Show this help
	@awk 'BEGIN {FS = ":.*## "}; /^[a-zA-Z0-9_.-]+:.*?## / {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## uv sync for CPU (chem + xtb + dev; tblite wheels on Linux x86_64)
	uv sync --extra chem --extra xtb --extra cpu --group dev

install-lite: ## uv sync without tblite (RDKit/ASE/torch only; useful if xtb fails to build)
	uv sync --extra chem --extra cpu --group dev

install-mps: ## uv sync for Apple Silicon
	uv sync --extra chem --extra xtb --extra mps --group dev

install-cuda: ## uv sync for CUDA (prints note about --index flag)
	@echo "Using PyTorch CUDA wheels index: https://download.pytorch.org/whl/cu121"
	uv sync --extra chem --extra xtb --extra cuda --group dev --index https://download.pytorch.org/whl/cu121

hooks: ## Install pre-commit hooks with commit-msg type
	uv run pre-commit install --hook-type pre-commit --hook-type commit-msg

lock: ## uv lock
	uv lock

sync: ## uv sync (respects lockfile)
	uv sync

test: ## uv run pytest
	uv run pytest

test-cov: ## uv run pytest with coverage report
	uv run pytest --cov=suprakit --cov-report=term-missing --cov-report=html

lint: ## uv run ruff check
	uv run ruff check .

fmt: ## uv run ruff format
	uv run ruff format .

fmt-check: ## uv run ruff format --check
	uv run ruff format --check .

typecheck: ## uv run mypy src/suprakit/core
	uv run mypy src/suprakit/core

check: ## lint + fmt-check + typecheck + test (CI equivalent)
	uv run ruff check .
	uv run ruff format --check .
	uv run mypy src/suprakit/core
	uv run pytest

docs: ## uv run mkdocs serve
	uv run mkdocs serve

docs-build: ## uv run mkdocs build
	uv run mkdocs build --strict

notebook: ## uv run jupyter lab notebooks/
	uv run jupyter lab notebooks/

cli: ## uv run suprakit (pass ARGS=...)
	uv run suprakit $(ARGS)

clean: ## remove caches, build artifacts, coverage
	rm -rf .pytest_cache .ruff_cache .mypy_cache htmlcov site .coverage .coverage.*
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

clean-venv: ## remove .venv entirely
	rm -rf .venv

native-build: ## build all native submodules (currently no-op with friendly message)
	@echo "No native submodules are registered yet. See native/README.md for policy."
