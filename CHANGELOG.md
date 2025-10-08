# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.2] - 2025-10-08

### Fixed
- Fixed divisional chart ascendant d1HousePlacement calculation (was always showing 1, now correctly calculated)
- Fixed type hints: Added Optional import for proper type annotations
- Relaxed mypy configuration for better compatibility

### Added
- Professional badges to README (PyPI version, Python version, License, Downloads, GitHub stars)

### Removed
- Unnecessary cross-platform tests (reduced from 112 to 109 tests, maintained 89% coverage)

## [0.1.1] - 2025-10-05

### Changed
- Updated PyPI metadata with correct GitHub repository links
- Minor metadata improvements

## [0.1.0] - 2025-10-05

### Added
- Initial release of jyotishganit
- Complete Vedic birth chart calculations
- Planetary positions with True Chitra Paksha Ayanamsa
- Panchanga calculations (Tithi, Nakshatra, Yoga, Karana, Vaara)
- Divisional charts (D1-D60)
- Ashtakavarga system
- Shadbala (6-fold planetary strength) calculations
- Vimshottari Dasha system
- JSON-LD structured output
- High-precision astronomical calculations using Skyfield/JPL ephemeris

### Dependencies
- skyfield: Astronomical calculations
- pandas: Data processing
- numpy: Numerical computations