# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.7] - 2026-10-09

### Fixed
- All equal-division charts (D2–D60) now select the subdivision and its natal-degree remainder together using exact division of the supplied numeric value (issue #20). Values within a float step of D9/D27/D45 boundaries now resolve on their exact side: `70/3` evaluates just below 23⅓°, so Aries maps to Libra in D9. Remainders retain fractional arcseconds; integer total-seconds metadata and D30's unequal, upper-inclusive boundaries are unchanged.

### Changed
- D2 now returns twelve houses ordered from its ascendant, like other divisional charts (issue #18). Previously it returned only Cancer and Leo in that order. Planetary signs, lords and D1 placement metadata are unchanged; the other ten houses are empty. Consumers relying on the two-entry list must accommodate the complete house list.

## [0.1.6] - 2026-10-06

### Fixed
- Fixed Cheshta Bala for Mars, Mercury, Jupiter, Venus and Saturn changing every minute (issue #16). Mean longitudes came from Skyfield osculating elements of the Earth-to-planet vector, which are not mean longitudes. They now come from Meeus' heliocentric mean elements (Table 31.a), converted to the chart's sidereal frame.
- Averaged mean and true longitude along the shorter arc, so planets either side of 0° Aries no longer get a kendra off by up to 180°.
- D2 house numbers are now counted from the D2 ascendant (issue #14). Charts with a Cancer D2 ascendant now number Cancer 1 and Leo 2 instead of 12 and 1.

### Added
- Added Cheshta Bala regressions: stability over minutes, the 0° Aries average, and B.V. Raman's and V.P. Jain's published examples.

### Notes
- Cheshta Bala values for these planets will change after upgrading. Results are within about 1.5 virupas of the published examples. Mercury is within about 4.5, because the books use older 1900-epoch constants for its Seeghrochcha.
- Removed the unused `MEAN_VELOCITIES` and `PLANET_MEAN_MOTION` constants in favour of `MEAN_LONGITUDE_TERMS`.

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
