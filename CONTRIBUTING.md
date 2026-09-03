# Contributing to FL26 Live Transfer Updater

Thank you for considering contributing to FL26 Live Transfer Updater! This document provides guidelines and instructions for contributing.

## Code of Conduct

Be respectful, inclusive, and constructive in all interactions.

## Getting Started

1. **Fork** the repository
2. **Clone** your fork locally
3. **Create a branch** for your changes (`git checkout -b feature/my-feature`)
4. **Install dev dependencies**: `pip install -r requirements-dev.txt`
5. **Make changes** and write tests
6. **Run tests**: `pytest tests/ -v`
7. **Commit** with clear messages
8. **Push** to your fork
9. **Create a Pull Request** with description

## Development Guidelines

### Code Style

- Follow PEP 8
- Use type hints
- Run `black` for formatting
- Use `ruff` for linting

```bash
black fl26_updater tests
ruff check fl26_updater tests
mypy fl26_updater
```

### Testing

- Write tests for new functionality
- Maintain >80% code coverage
- Use pytest fixtures for setup/teardown

```bash
pytest tests/ -v --cov=fl26_updater
```

### Commit Messages

Use clear, descriptive commit messages:

```
Add player matching engine

- Implements fuzzy name matching
- Adds confidence scoring
- Includes comprehensive tests
```

## Areas for Contribution

### High Priority

- [ ] FotMob API integration
- [ ] EDIT binary format parser
- [ ] Data validation and error handling

### Medium Priority

- [ ] Transfermarkt data source
- [ ] Web UI for transfer review
- [ ] Enhanced logging and debugging

### Nice to Have

- [ ] Discord/Slack notifications
- [ ] Player alias database
- [ ] Historical analytics dashboard
- [ ] Docker support

## Reporting Issues

When reporting bugs, please include:

1. **Description**: Clear explanation of the issue
2. **Steps to Reproduce**: How to trigger the bug
3. **Expected Behavior**: What should happen
4. **Actual Behavior**: What actually happened
5. **Environment**: Python version, OS, etc.
6. **Logs**: Relevant error messages or logs

## Questions?

Feel free to open a GitHub Discussion or Issue for questions.
