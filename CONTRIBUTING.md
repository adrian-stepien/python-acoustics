# Contributing

Thank you for helping maintain `python-acoustics`.

This fork uses `master` as the main branch and short-lived feature branches for changes.

## Development setup

Install `uv`, then run:

```bash
uv sync --all-groups
```

Useful commands:

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run sphinx-build -b html docs docs/_build/html
uv build
```

The Makefile provides the same workflow as convenience targets:

```bash
make sync
make test
make lint
make format-check
make docs
make build
```

## Nix

Nix is optional. Use it if you want a pinned Linux development shell or package check:

```bash
nix develop
nix flake check
```

GitHub Actions is the primary CI system. Nix runs in a separate optional workflow.

## Releases

Releases are GitHub-only for now. To publish a release:

```bash
git tag v0.3.0
git push origin v0.3.0
```

The release workflow builds the source distribution and wheel, then attaches both
artifacts to the GitHub Release. It does not publish to PyPI.

## Commit messages

Use short imperative commit messages, for example:

```text
Fix octave band filtering for NumPy 2.4
```

Do not add co-author trailers unless a human collaborator explicitly requests one.
