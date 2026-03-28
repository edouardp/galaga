.PHONY: test test-galaga test-galaga-marimo build check clean publish-test publish-prod

test: test-galaga test-galaga-marimo

test-galaga:
	uv run pytest packages/galaga/tests/ -v

test-galaga-marimo:
	uv run pytest packages/galaga_marimo/tests/ -v

build:
	cd packages/galaga && uv build
	cd packages/galaga_marimo && uv build

check: build
	uvx twine check dist/galaga-*
	uvx twine check packages/galaga_marimo/dist/galaga_marimo-*

clean:
	rm -rf dist/ packages/galaga_marimo/dist/

publish-test: 
	./scripts/publish-galaga.sh --test
	./scripts/publish-galaga-marimo.sh --test

publish-prod:
	./scripts/publish-galaga.sh
	./scripts/publish-galaga-marimo.sh
