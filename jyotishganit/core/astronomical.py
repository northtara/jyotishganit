"""
Astronomical calculations for jyotishganit.

Provides high-precision planetary positions using Skyfield with JPL ephemeris.
Implements True Chitra Paksha Ayanamsa for Vedic charts.
"""

import os
from datetime import datetime, timedelta
import math
from typing import Dict, List, Tuple
from functools import lru_cache
import platform

from skyfield.api import load, Loader, wgs84, Star
from skyfield.data import hipparcos
from skyfield.framelib import ecliptic_frame
from skyfield import almanac

from jyotishganit.core.models import Person, Ayanamsa as AyanamsaModel, PlanetPosition, PlanetDignities
from jyotishganit.core.constants import (
    PLANETARY_DIGNITIES, PLANETARY_TATTVA, SIGN_TATTVA, TATTVA_RELATIONS
)


def _get_data_directory():
    """
    Get platform-appropriate data directory for astronomical files.
    
    Returns:
        str: Path to the data directory following platform conventions
    """
    system = platform.system()
    
    if system == "Windows":
        # Use LOCALAPPDATA on Windows (e.g., C:\Users\username\AppData\Local)
        base_dir = os.environ.get('LOCALAPPDATA', os.path.expanduser('~'))
        data_dir = os.path.join(base_dir, 'jyotishganit')
    elif system == "Darwin":  # macOS
        # Use Application Support on macOS
        data_dir = os.path.expanduser('~/Library/Application Support/jyotishganit')
    else:  # Linux and other Unix-like systems
        # Use XDG Base Directory specification
        xdg_data = os.environ.get('XDG_DATA_HOME', os.path.expanduser('~/.local/share'))
        data_dir = os.path.join(xdg_data, 'jyotishganit')
    
    return data_dir


# Data directory for downloaded files
DATA_DIR = _get_data_directory()
os.makedirs(DATA_DIR, exist_ok=True)

# Custom loader for data(directory)
loader = Loader(DATA_DIR, verbose=True)  # Verbose=True to see progress bars during downloads

# Initialize astronomical objects with error handling
_ts = None
_eph = None

def _initialize_astronomical_data():
    """Initialize astronomical data with proper error handling."""
    global _ts, _eph
    
    if _ts is None or _eph is None:
        try:
            _ts = loader.timescale()
            _eph = loader('de421.bsp')
        except Exception as e:
            raise RuntimeError(
                f"Failed to initialize astronomical data. This usually happens on first run "
                f"when downloading ephemeris files. Please ensure you have an internet "
                f"connection and sufficient disk space (~10MB). Error: {e}"
            ) from e

def get_timescale():
    """Get initialized timescale object."""
    _initialize_astronomical_data()
    return _ts

def get_ephemeris():
    """Get initialized ephemeris object.""" 
    _initialize_astronomical_data()
    return _eph

@lru_cache(maxsize=None)
def _get_spica() -> Star:
    """Get cached Spica star object - matches original implementation."""
    with load.open(hipparcos.URL) as f:
        df = hipparcos.load_dataframe(f)
    # HIP 65474 is the Hipparcos catalog number for Spica (Alpha Virginis)
    spica_df = df.loc[65474]
    return Star.from_dataframe(spica_df)


def skyfield_time_from_datetime(birth_date: datetime, timezone_offset: float) -> object:
    """Create timezone-aware Skyfield time."""
    utc_datetime = birth_date - timedelta(hours=timezone_offset)
    ts = get_timescale()
    t = ts.utc(
        utc_datetime.year, utc_datetime.month, utc_datetime.day,
        utc_datetime.hour, utc_datetime.minute, utc_datetime.second
    )
    return t


def calculate_ayanamsa(t) -> float:
    """Calculate True Chitra Paksha Ayanamsa at time t."""
    spica = _get_spica()
    eph = get_ephemeris()
    pos = eph['earth'].at(t).observe(spica).apparent()
    _, lon, _ = pos.ecliptic_latlon()
    ayanamsa = lon.degrees - 180.0
    return ayanamsa if ayanamsa >= 0 else ayanamsa + 360


def tropical_to_sidereal(tropical_lon: float, ayanamsa: float) -> float:
    """Convert tropical to sidereal longitude."""
    sidereal = tropical_lon - ayanamsa
    return sidereal if sidereal >= 0 else sidereal + 360


def calculate_ascendant(t, latitude: float, longitude: float, ayanamsa: float) -> float:
    """Calculate sidereal ascendant using correct formula."""
    location = wgs84.latlon(latitude_degrees=latitude, longitude_degrees=longitude)

    # Calculate Local Sidereal Time
    # GMST = Greenwich Mean Sidereal Time in hours
    gmst = t.gmst
    lst_hours = gmst + location.longitude.hours

    # Convert LST to radians
    lst_rad = math.radians(lst_hours * 15)  # 15 degrees per hour

    # Get obliquity of the ecliptic
    obliquity = calculate_obliquity(t)
    obl_rad = math.radians(obliquity)

    # Get latitude in radians
    lat_rad = location.latitude.radians

    # Use the CORRECT formula from the reference
    y = -math.cos(lst_rad)  # Note: NEGATIVE cosine
    x = math.sin(lst_rad) * math.cos(obl_rad) + math.tan(lat_rad) * math.sin(obl_rad)

    # Calculate ascendant angle
    asc_rad = math.atan2(y, x)

    # Convert to tropical longitude (0-360)
    asc_tropical = (math.degrees(asc_rad) + 180) % 360

    # Convert to sidereal
    return tropical_to_sidereal(asc_tropical, ayanamsa)


def calculate_obliquity(t):
    """Calculates the obliquity of the ecliptic using the IAU 1980 formula."""
    T = t.tdb / 36525.0
    eps_arcsec = 84381.448 - 46.8150 * T - 0.00059 * T**2 + 0.001813 * T**3
    return eps_arcsec / 3600.0


def get_ecliptic_longitude(position) -> float:
    """Extract ecliptic longitude from Skyfield position."""
    _, lon, _ = position.ecliptic_latlon()
    return lon.degrees


def get_motion_type(planet_name: str, t) -> str:
    """Get motion type (direct, retrograde, stationary) as string for a planet."""
    # Sun, Moon, Rahu, Ketu don't retrograde
    if planet_name in ["Sun", "Moon"]:
        return "direct"
    if planet_name in ["Rahu", "Ketu"]:
        return "retrograde"

    # Map planet names to Skyfield body names
    body_mapping = {
        "Mars": "mars",
        "Mercury": "mercury",
        "Jupiter": "jupiter barycenter",
        "Venus": "venus",
        "Saturn": "saturn barycenter"
    }

    if planet_name not in body_mapping:
        return "direct"

    try:
        eph = get_ephemeris()
        body_name = body_mapping[planet_name]
        body = eph[body_name]
        # Use apparent position for better accuracy
        pos = eph['earth'].at(t).observe(body).apparent()

        # Get ecliptic coordinates and rates using ecliptic frame
        lat, lon, dist, lat_rate, lon_rate, range_rate = pos.frame_latlon_and_rates(ecliptic_frame)

        # Convert lon_rate to degrees per day
        try:
            lon_rate_deg_per_day = lon_rate.degrees.per_day
        except AttributeError:
            # Handle different Skyfield versions
            lon_rate_deg_per_day = (lon_rate.radians * (180.0 / math.pi)).per_day

        # Stricter threshold for stationary (same as user's function)
        stationary_threshold = 1e-3  # degrees per day (~3.6 arcseconds/day)

        if abs(lon_rate_deg_per_day) <= stationary_threshold:
            motion_type = "stationary"
        elif lon_rate_deg_per_day < 0:
            motion_type = "retrograde"
        else:
            motion_type = "direct"

        return motion_type

    except Exception as e:
        print(f"Error calculating motion for {planet_name}: {e}")
        return "direct"


def calculate_planet_positions(t, ayanamsa: float, ascendant: float) -> List[PlanetPosition]:
    """Calculate sidereal positions for all planets."""
    eph = get_ephemeris()
    planets = [
        ("Sun", eph['sun']),
        ("Moon", eph['moon']),
        ("Mars", eph['mars']),
        ("Mercury", eph['mercury']),
        ("Jupiter", eph['jupiter barycenter']),
        ("Venus", eph['venus']),
        ("Saturn", eph['saturn barycenter']),
    ]

    positions = []
    for name, body in planets:
        pos = eph['earth'].at(t).observe(body).apparent()
        tropical_lon = get_ecliptic_longitude(pos)
        sidereal_lon = tropical_to_sidereal(tropical_lon, ayanamsa)
        house = get_house_position(sidereal_lon, ascendant)

        sign, sign_degrees = lon_to_sign_degrees(sidereal_lon)
        nakshatra, pada, deity = lon_to_nakshatra(sidereal_lon)

        # Calculate dignities based on position
        dignities = calculate_dignities(name, sign, sign_degrees)

        # Calculate motion type
        motion_info = get_motion_type(name, t)

        planet_pos = PlanetPosition(
            celestial_body=name,
            sign=sign,
            sign_degrees=sign_degrees,
            nakshatra=nakshatra,
            pada=pada,
            nakshatra_deity=deity,
            house=house,
            motion_type=motion_info,  # "direct", "retrograde", or "stationary"
            shadbala={},  # Placeholder
            dignities=dignities,
            conjuncts=[],  # Placeholder
            aspects={"gives": [], "receives": []}  # No motion here
        )
        positions.append(planet_pos)

    # 4. Calculate Rahu and Ketu (Mean Lunar Nodes)
    T = (t.tt - 2451545.0) / 36525.0
    rahu_tropical = (125.04452 - 1934.136261 * T) % 360
    rahu_sidereal = tropical_to_sidereal(rahu_tropical, ayanamsa)
    ketu_sidereal = (rahu_sidereal + 180) % 360

    for name, sidereal_lon in [("Rahu", rahu_sidereal), ("Ketu", ketu_sidereal)]:
        house = get_house_position(sidereal_lon, ascendant)
        sign, sign_degrees = lon_to_sign_degrees(sidereal_lon)
        nakshatra, pada, deity = lon_to_nakshatra(sidereal_lon)
        dignities = calculate_dignities(name.split()[0], sign, sign_degrees)  # Use 'Rahu' or 'Ketu'
        motion_type = get_motion_type(name, t)
        planet_pos = PlanetPosition(
            celestial_body=name,
            sign=sign,
            sign_degrees=sign_degrees,
            nakshatra=nakshatra,
            pada=pada,
            nakshatra_deity=deity,
            house=house,
            motion_type=motion_type,
            shadbala={},
            dignities=dignities,
            conjuncts=[],
            aspects={"gives": [], "receives": []}
        )
        positions.append(planet_pos)

    return positions


# Dignities calculations use imported constants

def get_planet_tattva(planet: str) -> str:
    return PLANETARY_TATTVA.get(planet, "Water")

def get_sign_tattva(sign: str) -> str:
    return SIGN_TATTVA.get(sign, "Water")

def get_friendly_tattvas(tattva: str) -> List[str]:
    return TATTVA_RELATIONS.get(tattva, [])

def calculate_dignities(planet: str, sign: str, degrees: float) -> PlanetDignities:
    """Calculate dignities for a planet in given sign at given degrees using priorities."""
    planet_data = PLANETARY_DIGNITIES.get(planet, {})
    planet_tattva = planet_data.get("element", "Water")
    rashi_tattva = SIGN_TATTVA.get(sign, "Water")
    friendly_tattvas = TATTVA_RELATIONS.get(planet_tattva, [])

    dignity = "none"

    # Priority hierarchy for dignities

    # 1. Deep Exaltation - exact exalted degree within 0.05 degrees (5' orb)
    if (planet_data.get("exaltation") and
        sign == planet_data["exaltation"]["sign"] and
        planet_data["exaltation"]["degrees"] is not None and
        abs(degrees - planet_data["exaltation"]["degrees"]) < 0.05):
            dignity = "deep_exaltation"

    # 2. Deep Debilitation - exact debilitated degree within 0.05 degrees (5' orb)
    elif (planet_data.get("debilitation") and
          sign == planet_data["debilitation"]["sign"] and
          planet_data["debilitation"]["degrees"] is not None and
          abs(degrees - planet_data["debilitation"]["degrees"]) < 0.05):
            dignity = "deep_debilitation"

    # 3. Exalted - in exaltation sign (sign-wide for traditional planets like Moon)
    elif planet_data.get("exaltation") and sign == planet_data["exaltation"]["sign"]:
        dignity = "exalted"

    # 4. Debilitated - in debilitation sign (sign-wide)
    elif planet_data.get("debilitation") and sign == planet_data["debilitation"]["sign"]:
        dignity = "debilitated"

    # 5. Moolatrikona - in moolatrikona sign and degrees range
    elif (planet_data.get("moolatrikona") and
          sign == planet_data["moolatrikona"]["sign"] and
          planet_data["moolatrikona"]["min_degrees"] <= degrees <= planet_data["moolatrikona"]["max_degrees"]):
        dignity = "moolatrikona"

    # 6. Own sign - in any own sign
    elif sign in planet_data.get("own_signs", []):
        dignity = "own_sign"

    # 7. Neutral (default)
    else:
        dignity = "neutral"

    return PlanetDignities(
        dignity=dignity,
        planet_tattva=planet_tattva,
        rashi_tattva=rashi_tattva,
        friendly_tattvas=friendly_tattvas
    )


def lon_to_sign_degrees(longitude: float) -> Tuple[str, float]:
    """Convert ecliptic lon to sign and degrees within sign."""
    signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
             'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
    sign_index = int(longitude // 30)
    degrees = longitude % 30
    return signs[sign_index], degrees


def lon_to_nakshatra(longitude: float) -> Tuple[str, int, str]:
    """Convert lon to nakshatra, pada, deity."""
    nakshatras = [
        'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra',
        'Punarvasu', 'Pushya', 'Ashlesha', 'Magha', 'Purva Phalguni',
        'Uttara Phalguni', 'Hasta', 'Chitra', 'Swati', 'Vishakha', 'Anuradha',
        'Jyeshtha', 'Mula', 'Purva Ashadha', 'Uttara Ashadha', 'Shravana',
        'Dhanishta', 'Shatabhisha', 'Purva Bhadrapada', 'Uttara Bhadrapada', 'Revati'
    ]
    deities = [
        'Ashwini Kumaras', 'Yama', 'Agni', 'Brahma', 'Soma', 'Rudra',
        'Aditi', 'Brihaspati', 'Nagas', 'Pitris', 'Aryaman', 'Bhaga',
        'Surya', 'Vishwakarma', 'Vayu', 'Indra-Agni', 'Mitra', 'Indra',
        'Nirriti', 'Apah', 'Vishvedevatas', 'Vishnu', 'Vasus', 'Varuna',
        'Ajikapada', 'Ahirbudhnya', 'Pushan'
    ]
    span = 360 / 27
    pada_span = span / 4
    index = int(longitude / span)
    remainder = longitude % span
    pada = int(remainder / pada_span) + 1
    return nakshatras[index], pada, deities[index]


def get_planet_velocity(planet_name: str, t) -> float:
    """Get apparent geocentric velocity in degrees per day."""
    if planet_name in ["Sun", "Moon", "Rahu", "Ketu"]:
        if planet_name == "Sun":
            return 1.0  # Approx
        elif planet_name == "Moon":
            return 13.0  # Approx
        else:
            return 0.0  # Nodes don't move much

    body_mapping = {
        "Mars": "mars",
        "Mercury": "mercury",
        "Jupiter": "jupiter barycenter",
        "Venus": "venus",
        "Saturn": "saturn barycenter"
    }

    if planet_name not in body_mapping:
        return 0.0

    try:
        eph = get_ephemeris()
        body = eph[body_mapping[planet_name]]
        pos = eph['earth'].at(t).observe(body).apparent()
        _, lon, dist, _, lon_rate, _ = pos.frame_latlon_and_rates(ecliptic_frame)

        # Get longitude rate in degrees per day
        try:
            velocity = lon_rate.degrees.per_day
        except AttributeError:
            velocity = (lon_rate.radians * (180.0 / math.pi)).per_day

        return velocity

    except Exception as e:
        print(f"Error calculating velocity for {planet_name}: {e}")
        return 0.0


def get_planet_declination(planet_name: str, t) -> float:
    """Get declination of planet at time t."""
    if planet_name in ["Rahu", "Ketu"]:
        # Lunar nodes are equatorial
        return 0.0

    body_mapping = {
        "Sun": 'sun',
        "Moon": 'moon',
        "Mars": "mars",
        "Mercury": "mercury",
        "Jupiter": "jupiter barycenter",
        "Venus": "venus",
        "Saturn": "saturn barycenter"
    }

    if planet_name not in body_mapping:
        return 0.0

    try:
        eph = get_ephemeris()
        body = eph[body_mapping[planet_name]]
        pos = eph['earth'].at(t).observe(body).apparent()
        _, dec, _ = pos.radec()
        return dec.degrees
    except Exception as e:
        print(f"Error calculating declination for {planet_name}: {e}")
        return 0.0


def get_sunrise_sunset(person: Person) -> Tuple[float, float]:
    """Get sunrise and sunset times from midnight in hours."""
    try:
        location = wgs84.latlon(person.latitude, person.longitude)
        t = skyfield_time_from_datetime(person.birth_datetime, person.timezone_offset or 0)

        # Get sunrise/sunset around birth date
        ts = get_timescale()
        eph = get_ephemeris()
        t0 = ts.utc(person.birth_datetime.year, person.birth_datetime.month, person.birth_datetime.day, 0)
        t1 = ts.utc(person.birth_datetime.year, person.birth_datetime.month, person.birth_datetime.day+1, 0)

        f = almanac.sunrise_sunset(eph, location)
        times, events = almanac.find_discrete(t0, t1, f)

        sunrise = None
        sunset = None
        # Calculate reference point: local midnight converted to UTC
        local_midnight = person.birth_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
        midnight_utc = local_midnight - timedelta(hours=person.timezone_offset or 0)

        for i, event in enumerate(events):
            event_utc = times[i].utc_datetime()
            local_hour = event_utc.hour + event_utc.minute / 60.0 + event_utc.second / 3600.0 + (person.timezone_offset or 0)

            # Handle day rollover - if local hour >= 24, subtract 24
            if local_hour >= 24:
                local_hour -= 24

            if event == 1:  # sunrise
                sunrise = local_hour
            elif event == 0:  # sunset
                sunset = local_hour

        return sunrise, sunset

    except Exception as e:
        print(f"Error calculating sunrise/sunset: {e}")
        # Approximate: sunrise 6am, sunset 6pm
        return 6.0, 18.0


def is_birth_daytime(person: Person) -> bool:
    """Check if birth is during day."""
    sunrise, sunset = get_sunrise_sunset(person)
    birth_hour = person.birth_datetime.hour + person.birth_datetime.minute / 60.0
    return sunrise < birth_hour < sunset


def get_house_position(planet_lon: float, asc_lon: float) -> int:
    """Whole sign house system (sign-based houses)."""
    # Get ascendant sign index (1-12)
    signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
             'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
    asc_sign, _ = lon_to_sign_degrees(asc_lon)
    asc_sign_index = signs.index(asc_sign) + 1

    # Get planet sign index
    planet_sign, _ = lon_to_sign_degrees(planet_lon)
    planet_sign_index = signs.index(planet_sign) + 1

    # Calculate house using sign-based system
    house = ((planet_sign_index - asc_sign_index) % 12) + 1
    return house


def calculate_solar_ingress(solar_longitude: float, year: int) -> datetime:
    """
    Calculate the exact datetime when the Sun enters a specific ecliptic longitude.

    Uses binary search with minute-level precision to find the crossing point.
    Handles wraparound at 0°/360° boundary correctly.

    Args:
        solar_longitude: Target ecliptic longitude in degrees (0-360)
        year: Year to search within

    Returns:
        datetime object (UTC) of the solar ingress
    """
    try:
        # Define search range
        ts = get_timescale()
        eph = get_ephemeris()
        t_start = ts.utc(year, 1, 1)
        t_end = ts.utc(year, 12, 31)

        def sun_longitude_diff(t):
            """Calculate signed difference from target longitude."""
            pos = eph['earth'].at(t).observe(eph['sun']).apparent()
            _, lon, _ = pos.ecliptic_latlon()

            # Handle wraparound at 0/360
            diff = lon.degrees - solar_longitude
            if diff > 180:
                diff -= 360
            elif diff < -180:
                diff += 360
            return diff

        # Step through days to find sign change
        days = []
        current_t = t_start
        while current_t.tt < t_end.tt:
            days.append(current_t)
            current_t = _ts.tt_jd(current_t.tt + 1)  # Add 1 day

        # Find where we cross the target longitude
        prev_val = sun_longitude_diff(days[0])
        for i in range(1, len(days)):
            curr_val = sun_longitude_diff(days[i])

            # Check if we crossed the target (sign change in difference)
            if (prev_val < 0 and curr_val >= 0) or (prev_val > 0 and curr_val <= 0):
                # Refine with binary search between days[i-1] and days[i]
                t_low = days[i-1]
                t_high = days[i]

                # Binary search to minute-level precision
                for _ in range(20):  # ~1 minute precision after 20 iterations
                    t_mid = _ts.tt_jd((t_low.tt + t_high.tt) / 2)
                    mid_val = sun_longitude_diff(t_mid)

                    if abs(mid_val) < 0.001:  # Close enough (~3.6 arcseconds)
                        return t_mid.utc_datetime()

                    # Update search bounds
                    if (mid_val < 0 and prev_val < 0) or (mid_val > 0 and prev_val > 0):
                        t_low = t_mid
                    else:
                        t_high = t_mid

                return t_high.utc_datetime()

            prev_val = curr_val

        # Fallback: approximate spring equinox
        print(f"Warning: Solar ingress not found for {solar_longitude}° in {year}")
        return datetime(year, 3, 21)

    except Exception as e:
        print(f"Error calculating solar ingress: {e}")
        return datetime(year, 3, 21)


def get_solar_ingress_weekday(solar_longitude: float, year: int) -> int:
    """
    Get the weekday when the Sun enters a specified ecliptic longitude.

    Used for determining Varsha and Maasa lords in strength calculations.

    Args:
        solar_longitude: Target ecliptic longitude (0° = Aries start)
        year: Year to search

    Returns:
        Vedic weekday index: 0=Sunday, 1=Monday, 2=Tuesday, 3=Wednesday,
                            4=Thursday, 5=Friday, 6=Saturday
    """
    ingress_dt = calculate_solar_ingress(solar_longitude, year)

    # Python's weekday(): 0=Monday, 1=Tuesday, ..., 6=Sunday
    # Convert to Vedic: 0=Sunday, 1=Monday, ..., 6=Saturday
    python_weekday = ingress_dt.weekday()
    vedic_weekday = (python_weekday + 1) % 7

    return vedic_weekday


def calculate_all_positions(person: Person) -> Tuple[AyanamsaModel, float, List[PlanetPosition]]:
    """Compute ayanamsa, ascendant, and planet positions."""
    t = skyfield_time_from_datetime(person.birth_datetime, person.timezone_offset or 0)
    ayanamsa_value = calculate_ayanamsa(t)
    ayanamsa = AyanamsaModel(name="True Chitra Paksha", value=ayanamsa_value)
    asc_lon = calculate_ascendant(t, person.latitude, person.longitude, ayanamsa_value)
    planets = calculate_planet_positions(t, ayanamsa_value, asc_lon)
    return ayanamsa, asc_lon, planets


# Export main functions
__all__ = ['skyfield_time_from_datetime', 'calculate_ayanamsa', 'calculate_all_positions', 'get_solar_ingress_weekday']
