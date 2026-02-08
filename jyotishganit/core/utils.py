"""
Utility functions for jyotishganit library.

Provides common calculations and conversions used across modules.
"""

from jyotishganit.core.constants import NAKSHATRA_DEITIES, NAKSHATRAS, ZODIAC_SIGNS


def longitude_to_zodiac(longitude: float) -> tuple[str, float]:
    """Convert ecliptic longitude to Zodiac Sign and degrees within sign."""
    sign_index = int(longitude // 30)
    degrees = longitude % 30
    return ZODIAC_SIGNS[sign_index], degrees


def longitude_to_nakshatra(longitude: float) -> tuple[str, int, str]:
    """Convert ecliptic longitude to Nakshatra, Pada, and Deity."""
    span = 360 / 27  # Degrees per nakshatra
    pada_span = span / 4  # Degrees per pada
    index = int(longitude / span)
    remainder = longitude % span
    pada = int(remainder / pada_span) + 1
    return NAKSHATRAS[index], pada, NAKSHATRA_DEITIES[index]


def normalize_angle(angle: float) -> float:
    """Normalize angle to 0-360 degrees."""
    return angle % 360


def get_house_position(planet_lon: float, asc_lon: float) -> int:
    """Calculate house position using equal house system (equal 30° per house)."""
    diff = (planet_lon - asc_lon) % 360
    return int(diff / 30) + 1
