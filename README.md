# python-acoustics

[![Tests](https://github.com/adrian-stepien/python-acoustics/actions/workflows/test.yml/badge.svg)](https://github.com/adrian-stepien/python-acoustics/actions/workflows/test.yml)

The `python-acoustics` module is a Python module with useful tools for acousticians.

This repository is the maintained fork of the original `python-acoustics` project.
Releases for this fork are published as GitHub Releases with source distribution
and wheel artifacts.

## Installation

Install a release wheel from the GitHub Releases page, or install directly from a tag:

```bash
python -m pip install "acoustics @ git+https://github.com/adrian-stepien/python-acoustics.git@v0.3.0"
```

For local development, use `uv`:

```bash
uv sync --all-groups
uv run pytest
```

## Examples

Several examples can be found in the `examples` folder.

## Tests

The main checks are:

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest
```

## Documentation

Documentation sources live in the `docs` folder. Build them locally with:

```bash
uv run sphinx-build -b html docs docs/_build/html
```

## Nix

Nix support is optional. If you use Nix, `nix develop` provides a reproducible
development shell and `nix flake check` validates the package. The primary
development and CI workflow is still `uv` plus GitHub Actions.

## License

`python-acoustics` is distributed under the BSD 3-clause license. See `LICENSE` for more information.

## Contributing

Contributors are welcome. See `CONTRIBUTING.md` for the current development workflow.
