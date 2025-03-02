# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2025-03-02

### Changed
- Fixed linting issues throughout the codebase
- Updated GitHub Actions workflow to support Python 3.8 and later
- Renamed package to "open-elastic-hash" due to PyPI naming conflict
- Improved code formatting and organization
- Made matplotlib an optional dependency

### Fixed
- Fixed f-string issues in benchmark code
- Resolved compatibility issues with newer Python versions
- Fixed various small bugs in implementation

## [0.1.0] - 2025-03-02

### Added
- Initial release of the elastic-hash library
- ElasticHashTable implementation with O(1) amortized expected probe complexity
- FunnelHashTable implementation with O(log² 1/δ) worst-case expected probe complexity
- Comprehensive test suite
- Benchmarking tools
- Example usage scripts
