# Installation and Configuration

## Preconditions

Python 3.10+, currently up to 3.13 is tested.

## Installation

The package is hosted at the Python Package Index (PyPI) and can be installed using `pip install edutap.wallet_apple`.

We recommend working with `uv`

```bash
uv venv -p 3.13.0
source .venv/bin/activate
uv pip install edutap.wallet_apple
```

## Configuration

Write me

## Development

Run unit tests:

```bash
uvx --with tox-uv tox -e test -- -m "not integration"
```

Run integration tests:

```bash
uvx --with tox-uv tox -e test -- -m "integration"
```

Format code and run checks:

```bash
uvx --with tox-uv tox -e lint
```
