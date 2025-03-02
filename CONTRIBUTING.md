# Contributing to Elastic Hash

Thank you for considering contributing to Elastic Hash! This document outlines how to contribute to the project.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/elastic-hash.git`
3. Install the package in development mode: `pip install -e ".[dev]"`
4. Create a branch for your changes: `git checkout -b feature/my-feature`

## Development

### Code Style

We follow the [PEP 8](https://pep8.org/) style guide for Python. Please ensure your code follows these guidelines.

### Testing

Before submitting a pull request, please ensure that all tests pass:

```bash
python run_all_tests.py
```

If you add new functionality, please also add appropriate tests.

### Documentation

If you add new features, please update the documentation accordingly. This includes:

- Docstrings for new functions, classes, and methods
- Updates to the README.md if necessary
- Example usage in examples directory if appropriate

## Submitting Changes

1. Push your changes to your fork
2. Submit a pull request
3. In your pull request, please describe:
   - What changes you made
   - Why you made those changes
   - Any potential issues or limitations

## Benchmark Results

If your changes impact performance, please include benchmark results:

```bash
python examples/benchmark.py
```

## Code of Conduct

Please be respectful and constructive in your communications. We aim to create a welcoming and inclusive community.

## License

By contributing to this project, you agree that your contributions will be licensed under the project's MIT license.
