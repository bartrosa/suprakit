.DEFAULT_GOAL := help

.PHONY: help install install-lite install-mps install-cuda hooks lock sync test test-all test-cov lint format fmt fmt-check typecheck check ci docs docs-build notebook cli clean clean-venv

help: ## Show this help
	@awk 'BEGIN {FS = ":.*## "}; /^[a-zA-Z0-9_.-]+:.*?## / {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## uv sync: chem + xtb + cpu + dev (tblite wheels on Linux x86_64)
	uv sync --extra dev --extra chem --extra xtb --extra cpu
	uv run pre-commit install

install-lite: ## uv sync without tblite (RDKit/ASE/torch only)
	uv sync --extra dev --extra chem --extra cpu

install-mps: ## uv sync for Apple Silicon
	uv sync --extra dev --extra chem --extra xtb --extra mps

install-cuda: ## uv sync for CUDA (PyTorch CUDA index)
	@echo "Using PyTorch CUDA wheels index: https://download.pytorch.org/whl/cu121"
	uv sync --extra dev --extra chem --extra xtb --extra cuda --index https://download.pytorch.org/whl/cu121

hooks: ## Install pre-commit hooks
	uv run pre-commit install --hook-type pre-commit --hook-type commit-msg

lock: ## uv lock
	uv lock

sync: ## uv sync (respects lockfile)
	uv sync

test: ## uv run pytest (default marker filter)
	uv run pytest -q

test-all: ## uv run pytest without marker filter
	uv run pytest -q -m ""

test-cov: ## pytest with coverage report
	uv run pytest --cov=suprakit --cov-report=term-missing --cov-report=html

lint: ## ruff check
	uv run ruff check .

format: ## ruff format
	uv run ruff format .

fmt: format

fmt-check: ## ruff format --check
	uv run ruff format --check .

typecheck: ## mypy on suprakit package
	uv run mypy

check: ## lint + format check + typecheck + test (CI-style gate)
	uv run ruff check .
	uv run ruff format --check .
	uv run mypy
	uv run pytest -q

ci: check

docs: ## mkdocs serve
	uv run mkdocs serve

docs-build: ## mkdocs build --strict
	uv run mkdocs build --strict

notebook: ## jupyter lab notebooks/
	uv run jupyter lab notebooks/

cli: ## uv run suprakit (pass ARGS=...)
	uv run suprakit $(ARGS)

clean: ## remove caches, build artifacts, coverage
	rm -rf .pytest_cache .ruff_cache .mypy_cache htmlcov site dist build *.egg-info .coverage .coverage.*
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

clean-venv: ## remove .venv
	rm -rf .venv
