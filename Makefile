.PHONY: help install install-dev test lint format type-check clean run

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

install:  ## Install the package
	pip install -e .

install-dev:  ## Install development dependencies
	pip install -r requirements-dev.txt

test:  ## Run tests
	python -m pytest tests/ -v

test-coverage:  ## Run tests with coverage
	python -m pytest tests/ --cov=library_management_system --cov-report=html --cov-report=term

lint:  ## Run linting
	flake8 library_management_system/ tests/
	pylint library_management_system/

format:  ## Format code with black
	black library_management_system/ tests/ library_management.py

format-check:  ## Check if code is formatted
	black --check library_management_system/ tests/ library_management.py

type-check:  ## Run type checking
	mypy library_management_system/

quality:  ## Run all quality checks
	$(MAKE) format-check
	$(MAKE) lint
	$(MAKE) type-check
	$(MAKE) test

clean:  ## Clean up build artifacts
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

run:  ## Run the application
	python library_management.py