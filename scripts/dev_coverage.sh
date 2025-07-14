#!/bin/bash
# Install dev dependencies with: uv pip install --group dev
pytest --cov=intent_kit --cov-report=term-missing --cov-report=html "$@"
echo "Open htmlcov/index.html for a detailed report."
