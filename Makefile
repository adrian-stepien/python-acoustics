DOCS = docs

.PHONY: sync test tests coverage lint lint-fix format format-check typecheck docs build sdist clean release

sync:
	uv sync --all-groups

test:
	uv run pytest

tests: test

coverage:
	uv run pytest --cov-report=html

lint:
	uv run ruff check .

lint-fix:
	uv run ruff check --fix .

format:
	uv run ruff format .

format-check:
	uv run ruff format --check .

typecheck:
	uv run basedpyright

docs:
	uv run sphinx-build -W --keep-going -b html $(DOCS) $(DOCS)/_build/html

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
