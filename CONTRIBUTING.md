# Contributing to CalWORKs Analysis

## Getting Started

1. Fork the repository
2. Create a feature branch
3. Set up development environment
4. Make your changes
5. Run tests
6. Submit a pull request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/calworks-analysis.git
cd calworks-analysis

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dev dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## Code Style

- Follow PEP 8
- Use type hints
- Write docstrings (Google style)
- Maximum line length: 88 characters
- Use Black for formatting

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=Script_python

# Run specific test
pytest tests/unit/test_data_ops.py
```

## Pull Request Process

1. Update documentation
2. Add tests for new features
3. Update CHANGELOG.md
4. Ensure CI passes
5. Get review from maintainers

## Code Review Checklist

- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Code follows style guide
- [ ] All tests passing
- [ ] No new warnings 