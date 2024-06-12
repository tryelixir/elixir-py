# Elixir

Python SDK for the Elixir API

## Installation

1. Clone the repository:

```bash
git clone https://github.com/acalabs-xyz/elixir-py
```

2. Navigate to the project directory:

```bash
cd elixir-py
```

3. Install the dependencies:

```bash
poetry install
```

## Setup

If using VSCode, install the `Flake8` and `Black Formatter` extensions.

## Tests

```bash
poetry run pytest tests
```

## Lint

```bash
poetry run flake8 .
```

## Formatting

```bash
poetry run black .
```

## Publishing

### Test

```bash
# One-time config
poetry config repositories.testpypi https://test.pypi.org/legacy/
poetry config pypi-token.testpypi your-api-token

poetry build
poetry publish -r testpypi
```

### Production

```bash
# One-time config
poetry config pypi-token.pypi your-api-token

poetry build
poetry publish
```

## License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).
