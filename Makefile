# Makefile for galaga
#
# Usage:
#   make              Show all available targets
#   make <target>     Run a specific target

EXCLUDE_NEWER := $(shell date -u -v-7d +%Y-%m-%dT00:00:00Z 2>/dev/null || date -u -d '7 days ago' +%Y-%m-%dT00:00:00Z 2>/dev/null)

.PHONY: help
help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-24s\033[0m %s\n", $$1, $$2}'

# ============================================================================
# Setup and Installation
# ============================================================================

.PHONY: install
install: ## Install dependencies with uv
	uv sync

.PHONY: install-hooks
install-hooks: ## Install pre-commit git hooks
	uv run pre-commit install

# ============================================================================
# Code Quality
# ============================================================================

.PHONY: lint
lint: ## Run linting checks
	./scripts/lint.sh

.PHONY: format
format: ## Auto-fix formatting and linting issues
	./scripts/lint.sh --fix

.PHONY: lint-fix
lint-fix: format ## Alias for format

.PHONY: pre-commit
pre-commit: ## Run all pre-commit hooks manually
	uv run pre-commit run --all-files

.PHONY: security
security: ## Run security scans (bandit + pip-audit)
	uv run bandit -r -c .bandit packages/
	uv run pip-audit

# ============================================================================
# Testing
# ============================================================================

.PHONY: test
test: test-galaga test-galaga-marimo test-galaga-matrix test-galaga-mermaid ## Run all tests

.PHONY: test-all
test-all: test ## Alias for test

.PHONY: test-galaga
test-galaga: ## Run galaga tests
	uv run pytest packages/galaga/tests/ -v

.PHONY: test-galaga-marimo
test-galaga-marimo: ## Run galaga-marimo tests with Python 3.14
	@TMPVENV=$$(mktemp -d)/gamo-test && \
	uv venv "$$TMPVENV" --python 3.14 && \
	uv pip install --python "$$TMPVENV/bin/python" -e packages/galaga -e packages/galaga_marimo pytest && \
	"$$TMPVENV/bin/pytest" packages/galaga_marimo/tests/ -v && \
	rm -rf "$$TMPVENV"

.PHONY: test-galaga-matrix
test-galaga-matrix: ## Run galaga-matrix tests
	PYTHONPATH=.:packages/galaga_matrix uv run --python 3.14 pytest packages/galaga_matrix/tests/ -q

.PHONY: test-galaga-mermaid
test-galaga-mermaid: ## Run galaga-mermaid tests
	PYTHONPATH=.:packages/galaga_mermaid uv run pytest packages/galaga_mermaid/tests/ -q

.PHONY: test-quick
test-quick: ## Run core galaga tests stopping on first failure
	uv run pytest packages/galaga/tests/ -x -q

# ============================================================================
# Dependencies
# ============================================================================

.PHONY: update-deps
update-deps: ## Update dependencies (7-day lag for supply chain protection)
	@test -n "$(EXCLUDE_NEWER)" || { echo "Set EXCLUDE_NEWER manually"; exit 1; }
	@echo "Excluding packages uploaded after $(EXCLUDE_NEWER)"
	uv lock --upgrade --exclude-newer "$(EXCLUDE_NEWER)"
	uv sync
	uv run pip-audit

# ============================================================================
# Build
# ============================================================================

.PHONY: build
build: ## Build package distributions
	cd packages/galaga && uv build
	cd packages/galaga_marimo && uv build
	cd packages/galaga_matrix && uv build
	cd packages/galaga_mermaid && uv build

.PHONY: check
check: build ## Build and run twine checks
	uvx twine check dist/galaga-*
	uvx twine check packages/galaga_marimo/dist/galaga_marimo-*
	uvx twine check packages/galaga_matrix/dist/galaga_matrix-*
	uvx twine check packages/galaga_mermaid/dist/galaga_mermaid-*

# ============================================================================
# Release
# ============================================================================

.PHONY: release
release: ## Release interactively (asks for patch, minor, or major)
	@CHOICE=$$(uv run scripts/chooser.py --title "Release type?" patch minor major 3>&1 1>&2) || exit 1; \
	./scripts/release.sh $$CHOICE

.PHONY: release-patch
release-patch: ## Release a patch version
	./scripts/release.sh patch

.PHONY: release-minor
release-minor: ## Release a minor version
	./scripts/release.sh minor

.PHONY: release-major
release-major: ## Release a major version
	./scripts/release.sh major

# ============================================================================
# Cleanup
# ============================================================================

.PHONY: clean
clean: ## Remove build artifacts and caches
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache .ruff_cache .coverage htmlcov dist/ packages/*/dist/ packages/*/.pytest_cache

.PHONY: clean-all
clean-all: clean ## Remove all local environment and tool caches
	rm -rf .venv
	uv run pre-commit clean

# ============================================================================
# Validation
# ============================================================================

.PHONY: all
all: validate ## Run full validation

.PHONY: validate
validate: lint security test ## Run lint, security, and tests
	@echo ""
	@echo "Validation complete."

# ============================================================================
# Default Target
# ============================================================================

.DEFAULT_GOAL := help
