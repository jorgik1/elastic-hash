# Publishing Checklist for Elastic Hash

This checklist will help guide you through the process of publishing your package to PyPI and resolving the issues encountered.

## Package Naming Issue

The name "elastic-hash" was rejected by PyPI as being too similar to an existing package. Try one of these alternatives:

- [ ] optimal-hash
- [ ] ehash-tables
- [ ] farach-hash
- [ ] non-reorder-hash
- [ ] open-elastic-hash
- [ ] funnel-elastic-hash
- [ ] advanced-open-hash
- [ ] yaodisprovehash
- [ ] probe-optimized-hash
- [ ] hashbounds

Once you've chosen a name, update these files:

- [ ] `pyproject.toml`: Change the `name` field
- [ ] `setup.py`: Update the `name` parameter
- [ ] `README.md`: Update references to the package name
- [ ] Any import examples in documentation

## GitHub Actions Issues

Issues with GitHub Actions have been addressed:

- [x] Removed Python 3.7 from test matrix as it's not supported on newer Ubuntu runners
- [x] Updated minimum Python requirement to 3.8 in pyproject.toml

## Linting Issues

To address linting issues:

1. [ ] Run the format-fixing scripts:
   ```bash
   chmod +x scripts/format_code.sh
   ./scripts/format_code.sh
   ```

2. [ ] Address any remaining issues shown by flake8:
   ```bash
   flake8 elastic_hash tests examples
   ```

## Final Publishing Steps

1. [ ] Commit all changes to GitHub:
   ```bash
   git add .
   git commit -m "Fix package name and address linting issues"
   git push
   ```

2. [ ] Build the package:
   ```bash
   python -m build
   ```

3. [ ] Upload to PyPI:
   ```bash
   twine upload dist/*
   ```

4. [ ] Update your GitHub repository's name and URLs to match the new package name

## Optional Next Steps

- [ ] Implement a test in CI for package publication using TestPyPI
- [ ] Add coverage reports to CI
- [ ] Set up automated version bump with git tags
- [ ] Create a project website or more comprehensive documentation
