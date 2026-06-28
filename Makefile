.PHONY: install lint format format-check test coverage precommit check build clean

install:
	uv sync --extra dev

lint:
	uv run ruff check .

format:
	uv run ruff format .

format-check:
	uv run ruff format --check .

test:
	uv run pytest

coverage:
	uv run pytest --cov=api_client_kit --cov-report=term-missing

precommit:
	uv run pre-commit run --all-files

check:
	uv run ruff check .
	uv run ruff format --check .
	uv run pytest

build:
	uv run python -m build

clean:
	rm -rf build dist htmlcov .coverage .coverage.* coverage.xml
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -prune -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -prune -exec rm -rf {} +
	find . -type d -name "*.egg-info" -prune -exec rm -rf {} +
