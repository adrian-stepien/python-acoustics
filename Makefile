DOCS = docs

.PHONY: sync test tests lint format format-check docs build sdist clean release

sync:
	uv sync --all-groups

test:
	uv run pytest

tests: test

lint:
	uv run ruff check .

format:
	uv run ruff format .

format-check:
	uv run ruff format --check .

docs:
	uv run sphinx-build -b html $(DOCS) $(DOCS)/_build/html

build:
	uv build

sdist: build

clean:
	rm -rf dist
	find . -name __pycache__ | xargs rm -rf {}
	find . -name "*.pyc" | xargs rm -rf {}
	rm -rf acoustics.egg-info
	rm -rf build
	rm -rf .pytest_cache
	rm -rf $(DOCS)/_build

release:
	@echo "Releases are created by pushing a version tag, for example: git tag v0.3.0 && git push origin v0.3.0"
