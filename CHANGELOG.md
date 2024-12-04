# Changelog

All notable changes to the CalWORKs Analysis project will be documented in this file.

## [1.1.1] - 12/4/2024

### Fixed
- Handle invalid household sizes (NP <= 0) in preprocessing
- Update PUMA configuration structure reference
- Improve data validation logging

## [1.1.0] - 12/4/2024

### Added
- PUMA region names and detailed configuration in `config.yaml`
- Proper MBSAC threshold calculation with support for households > 10 persons
- Comprehensive income calculation rules including earned income disregard
- Categorical eligibility handling for Food Stamps and Public Assistance
- Documentation links to official CalWORKs rules

### Changed
- **Major Refactor**: Income calculation logic
  - Separated earned vs unearned income processing
  - Added $450 earned income disregard per working family member
  - Improved handling of excluded income types
  - Better documentation of income source types

- **Code Efficiency**:
  - Reduced code duplication in income calculations (~40% reduction)
  - Vectorized operations for faster processing
  - Improved memory usage by reducing intermediate dataframes

- **Configuration Management**:
  - Moved all thresholds and rules to `config.yaml`
  - Added detailed comments and documentation
  - Structured configuration for better maintainability

- **Improved Error Handling**:
  - Added proper error messages for income calculation failures
  - Better logging of processing steps
  - Validation of input data types

### Technical Improvements
- **Performance**:
  - Vectorized MBSAC threshold calculations
  - Optimized pandas operations for income aggregation
  - Reduced memory footprint in person data processing

- **Code Quality**:
  - Reduced function complexity in preprocessing.py
  - Added type hints for better code maintainability
  - Improved function documentation
  - Better separation of concerns between modules

- **Maintainability**:
  - Centralized configuration in YAML
  - Added comments for future implementation of excluded income types
  - Better organization of PUMA region metadata

### Fixed
- Incorrect handling of households with more than 10 persons
- Missing income disregard calculations
- Improper aggregation of household income sources

## [1.0.0] - Initial Release

- Basic CalWORKs eligibility determination
- Simple income calculations
- Regional analysis capabilities 