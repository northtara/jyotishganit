# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.5] - 2026-10-01

### Fixed
- Resolved the coordinate-frame mismatch reported in issue #12 by using the true ecliptic and equinox of date consistently for Spica, planetary longitudes, the ascendant, and mean lunar nodes.
- Aligned ascendant sidereal time and obliquity with that frame, and corrected solar-ingress and planetary-declination calculations to use coordinates of date.
- Normalized sidereal longitudes to the range [0, 360).

### Added
- Added 242 coordinate-frame regression cases, including independent reference snapshots and eastern-horizon geometry checks across 1900–2050.

### Notes
- True Chitra Paksha remains the ayanamsa, and Rahu/Ketu still use the existing approximate mean-node model. Chart results affected by the frame mismatch may change after upgrading.

## [0.1.4] - 2026-10-01

### Fixed
- Corrected unequal D30 intervals and sign mappings for even natal signs, preserving upper-inclusive internal boundaries.
- Fixed day/night calculations for polar latitudes, solar events spanning UTC midnight, and Natonnata Bala scaling and continuity.

### Changed
- Updated packaging and development tooling, with Python 3.10 through 3.13 validation and a typed package marker.

## [0.1.3] - 2026-05-30

### Fixed
- Corrected mean obliquity calculation to measure TT Julian centuries from J2000

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
