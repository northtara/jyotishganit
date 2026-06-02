"""
Panchanga calculations for Vedic astrology.

Provides traditional five-limb (Panchanga) calculations including:
- Tithi (lunar day)
- Nakshatra (constellation)
- Yoga (luni-solar day)
- Karana (half lunar day)
- Vaara (weekday)
"""

import math
from datetime import datetime, timedelta
from functools import cache

from skyfield.api import Star, load
from skyfield.data import hipparcos

# Use global Skyfield objects from core.astronomical
from jyotishganit.core.astronomical import get_ephemeris, get_timescale
from jyotishganit.core.constants import (
    FIXED_KARANAS,
    MOVABLE_KARANAS,
    NAKSHATRA_DEITIES,
    NAKSHATRAS,
    TITHI_NAMES,
    VAARA_NAMES,
    YOGA_NAMES,
)
from jyotishganit.core.models import Panchanga


def _get_sun():
    """Get sun object from ephemeris."""
    return get_ephemeris()["sun"]


@cache
def get_spica_star_object():
    """Loads the Hipparcos star catalog and returns the Skyfield Star object for Spica."""
    with load.open(hipparcos.URL) as f:
        df = hipparcos.load_dataframe(f)
    spica_df = df.loc[65474]
    return Star.from_dataframe(spica_df)


def utc_to_jd(birth_datetime: datetime, timezone_offset: float) -> float:
    """Convert UTC datetime to Julian Day."""
    utc_dt = birth_datetime - timedelta(hours=timezone_offset)
    ts = get_timescale()
    t = ts.utc(
        utc_dt.year, utc_dt.month, utc_dt.day, utc_dt.hour, utc_dt.minute, utc_dt.second
    )
    return t.tdb / 86400.0 + 2451545.0


def solar_longitude(time) -> float:
    eph = get_ephemeris()
    sun = _get_sun()
    pos = eph["earth"].at(time).observe(sun).apparent()
    _, lon, _ = pos.ecliptic_latlon()
    return lon.degrees


def lunar_longitude(time) -> float:
    eph = get_ephemeris()
    pos = eph["earth"].at(time).observe(eph["moon"]).apparent()
    _, lon, _ = pos.ecliptic_latlon()
    return lon.degrees


# Panchanga data is now imported from constants


def calculate_tithi(birth_datetime: datetime, timezone_offset: float) -> str:
    """Calculate Tithi from sun-moon phase."""
    utc_dt = birth_datetime - timedelta(hours=timezone_offset)
    ts = get_timescale()
    t = ts.utc(
        utc_dt.year, utc_dt.month, utc_dt.day, utc_dt.hour, utc_dt.minute, utc_dt.second
    )
    moon_phase = get_lunar_phase(t)
    tithi_num = math.floor(moon_phase / 12) + 1
    if tithi_num > 30:
        tithi_num = 30
    return TITHI_NAMES[tithi_num - 1]


def calculate_nakshatra(
    birth_datetime: datetime, timezone_offset: float, ayanamsa: float
) -> str:
    """Calculate Nakshatra from moon position."""
    utc_dt = birth_datetime - timedelta(hours=timezone_offset)
    ts = get_timescale()
    t = ts.utc(
        utc_dt.year, utc_dt.month, utc_dt.day, utc_dt.hour, utc_dt.minute, utc_dt.second
    )
    moon_lon = (lunar_longitude(t) - ayanamsa) % 360
    nakshatra_index = int(moon_lon / 13.3333) % 27
    return NAKSHATRAS[nakshatra_index]


def calculate_yoga(
    birth_datetime: datetime, timezone_offset: float, ayanamsa: float
) -> str:
    """Calculate Yoga from combined sun-moon longitude."""
    utc_dt = birth_datetime - timedelta(hours=timezone_offset)
    ts = get_timescale()
    t = ts.utc(
        utc_dt.year, utc_dt.month, utc_dt.day, utc_dt.hour, utc_dt.minute, utc_dt.second
    )
    sun_lon = (solar_longitude(t) - ayanamsa) % 360
    moon_lon = (lunar_longitude(t) - ayanamsa) % 360
    yoga_lon = (sun_lon + moon_lon) % 360
    yoga_index = int(yoga_lon / 13.3333) % 27
    return YOGA_NAMES[yoga_index]


def calculate_karana(birth_datetime: datetime, timezone_offset: float) -> str:
    """Calculate Karana from Moon–Sun longitude difference (in degrees)."""
    # convert to UTC
    utc_dt = birth_datetime - timedelta(hours=timezone_offset)

    # compute lunar elongation using your time scale
    ts = get_timescale()
    t = ts.utc(
        utc_dt.year, utc_dt.month, utc_dt.day, utc_dt.hour, utc_dt.minute, utc_dt.second
    )

    # Get sun and moon longitudes
    sun_lon = solar_longitude(t)
    moon_lon = lunar_longitude(t)

    # Calculate difference: if Moon < Sun, add 360° to Moon longitude
    if moon_lon < sun_lon:
        longitude_diff = (moon_lon + 360.0) - sun_lon
    else:
        longitude_diff = moon_lon - sun_lon

    # Each Karana = 6 degrees, calculate K value as per authoritative formula
    K = int(longitude_diff / 6.0)

    # Apply the authoritative formula:
    # If K is 57, 58, 59, or 0 (which corresponds to 60) → Fixed Karanas
    if K % 60 in [57, 58, 59, 0]:
        # Map to fixed karanas: 57→Shakuni, 58→Chatushpada, 59→Naga, 0→Kimstughna
        fixed_index = K % 60
        if fixed_index == 0:  # K=60 corresponds to Kimstughna
            fixed_index = 60
        return FIXED_KARANAS[fixed_index - 57]
    else:
        # For other K values: divide by 7 and find remainder
        # Remainder 1→Bava, 2→Balava, etc. (1-based indexing in formula)
        remainder = K % 7
        if remainder == 0:  # When K is multiple of 7, remainder should be 7 (Vishti)
            remainder = 7
        return MOVABLE_KARANAS[remainder - 1]  # Convert to 0-based indexing


def calculate_vaara(birth_datetime: datetime) -> str:
    """Calculate Vaara (weekday) from date."""
    # Python weekday(): Monday=0, Sunday=6
    # Vedic weekday: Sunday=0, Monday=1, etc.
    weekday_index = birth_datetime.weekday()  # Monday=0, Sunday=6
    # Convert Python weekday to Vedic: Sunday becomes 0
    vedic_index = (weekday_index + 1) % 7
    return VAARA_NAMES[vedic_index]


def get_lunar_phase(time):
    """Get lunar phase in degrees (0-360)."""
    sun_lon = solar_longitude(time)
    moon_lon = lunar_longitude(time)
    phase = (moon_lon - sun_lon) % 360
    return phase


def get_body_separation(time, body1, body2):
    """Get separation between two celestial bodies."""
    eph = get_ephemeris()
    pos1 = eph["earth"].at(time).observe(body1).apparent()
    pos2 = eph["earth"].at(time).observe(body2).apparent()
    _, lon1, _ = pos1.ecliptic_latlon()
    _, lon2, _ = pos2.ecliptic_latlon()
    separation = abs(lon1.degrees - lon2.degrees)
    return min(separation, 360 - separation)


def lon_to_nakshatra_full(longitude: float) -> tuple[str, int, str]:
    """
    Convert longitude to nakshatra with pada and deity.

    Args:
        longitude: Sidereal longitude in degrees

    Returns:
        Tuple of (nakshatra_name, pada, deity_name)
    """
    # Each nakshatra is 13.333... degrees (360/27)
    nakshatra_size = 360.0 / 27.0
    nakshatra_index = int(longitude / nakshatra_size) % 27

    # Calculate pada (1-4 within each nakshatra)
    position_in_nakshatra = longitude % nakshatra_size
    pada = int(position_in_nakshatra / (nakshatra_size / 4)) + 1

    nakshatra_name = NAKSHATRAS[nakshatra_index]
    deity_name = NAKSHATRA_DEITIES[nakshatra_index]

    return nakshatra_name, pada, deity_name


def create_panchanga(
    birth_datetime: datetime, timezone_offset: float, ayanamsa: float
) -> Panchanga:
    """Create Panchanga object with all five limbs calculated for birth time."""
    return Panchanga(
        tithi=calculate_tithi(birth_datetime, timezone_offset),
        nakshatra=calculate_nakshatra(birth_datetime, timezone_offset, ayanamsa),
        yoga=calculate_yoga(birth_datetime, timezone_offset, ayanamsa),
        karana=calculate_karana(birth_datetime, timezone_offset),
        vaara=calculate_vaara(birth_datetime),
    )


def calculate_panchanga_at_birth(
    birth_datetime: datetime, timezone_offset: float, ayanamsa: float
):
    """Calculate all panchanga elements at birth time."""
    utc_dt = birth_datetime - timedelta(hours=timezone_offset)
    ts = get_timescale()
    ts.utc(
        utc_dt.year, utc_dt.month, utc_dt.day, utc_dt.hour, utc_dt.minute, utc_dt.second
    )

    return {
        "tithi": calculate_tithi(birth_datetime, timezone_offset),
        "nakshatra": calculate_nakshatra(birth_datetime, timezone_offset, ayanamsa),
        "yoga": calculate_yoga(birth_datetime, timezone_offset, ayanamsa),
        "karana": calculate_karana(birth_datetime, timezone_offset),
        "vaara": calculate_vaara(birth_datetime),
    }
