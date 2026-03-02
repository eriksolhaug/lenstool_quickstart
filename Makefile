# Makefile for common development tasks

.PHONY: help clean install test lint format docs

help:
	@echo "Available commands:"
	@echo "  make install      - Install the package in development mode"
	@echo "  make test         - Run tests with pytest"
	@echo "  make lint         - Run linting checks"
	@echo "  make format       - Format code with black and isort"
	@echo "  make clean        - Remove build artifacts"
	@echo "  make examples     - Run example scripts"

install:
	pip install -e ".[dev]"

test:
	pytest tests/ -v --cov=lenstool_quickstart --cov-report=html

lint:
	flake8 lenstool_quickstart tests examples
	black --check lenstool_quickstart tests examples

format:
	black lenstool_quickstart tests examples
	isort lenstool_quickstart tests examples

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build dist .eggs .pytest_cache .coverage htmlcov

examples:
	python examples/basic_example.py
	python examples/multiband_example.py
