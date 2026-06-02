"""
Pytest fixtures for jyotishganit testing.

Provides diverse birth data fixtures covering:
- Different timezone offsets and locations
- Various time periods (1900s, 2000s, present)
- Geographic diversity (hemispheres, latitudes)
- Edge cases for astrological calculations
"""

from datetime import datetime

import pytest

from jyotishganit.core.models import Person
from jyotishganit.main import calculate_birth_chart

# =============================================================================
# GEOGRAPHIC AND TIMEZONE FIXTURES
# =============================================================================


@pytest.fixture
def test_locations():
    """Dictionary of diverse test locations with coordinates and timezones."""
    return {
        "mumbai": {"lat": 19.0760, "lon": 72.8777, "tz": 5.5},  # IST
        "delhi": {"lat": 28.6139, "lon": 77.2090, "tz": 5.5},  # IST
        "london": {"lat": 51.5074, "lon": -0.1278, "tz": 0.0},  # GMT/BST
        "nyc": {"lat": 40.7128, "lon": -74.0060, "tz": -4.0},  # EDT (simplified)
        "tokyo": {"lat": 35.6762, "lon": 139.6503, "tz": 9.0},  # JST
        "sydney": {"lat": -33.8688, "lon": 151.2093, "tz": 11.0},  # AEDT
        "capetown": {"lat": -33.9249, "lon": 18.4241, "tz": 2.0},  # SAST
        "anchorage": {"lat": 61.2181, "lon": -149.9003, "tz": -9.0},  # AKDT
    }


# =============================================================================
# BIRTH DATA FIXTURES - DIVERSE TIMEFRAMES
# =============================================================================


@pytest.fixture
def birth_1900s():
    """Early 20th century birth data."""
    return [
        # 1900: Start of 20th century
        Person(datetime(1900, 1, 1, 12, 0, 0), 19.0760, 72.8777, 5.5, "Mumbai1900"),
        # 1950s: Mid-century
        Person(datetime(1955, 6, 15, 6, 30, 0), 28.6139, 77.2090, 5.5, "Delhi1955"),
        # 1990s: Late century before millennium
        Person(datetime(1995, 12, 31, 23, 59, 0), 51.5074, -0.1278, 0.0, "London1995"),
    ]


@pytest.fixture
def birth_2000s():
    """21st century birth data."""
    return [
        # Y2K and early 2000s
        Person(datetime(2000, 1, 1, 0, 0, 1), 35.6762, 139.6503, 9.0, "Tokyo2000"),
        Person(datetime(2005, 7, 4, 13, 45, 0), 40.7128, -74.0060, -4.0, "NYC2005"),
        # Late 2000s to present
        Person(datetime(2010, 3, 21, 9, 15, 0), -33.8688, 151.2093, 10.0, "Sydney2010"),
        Person(
            datetime(2020, 5, 10, 16, 20, 0), -33.9249, 18.4241, 2.0, "CapeTown2020"
        ),
    ]


@pytest.fixture
def birth_edge_cases():
    """Edge cases for astronomical calculations."""
    return [
        # High latitude (near poles)
        Person(
            datetime(2015, 12, 21, 12, 0, 0), -77.85, 166.67, 12.0, "Antarctica"
        ),  # McMurdo
        Person(
            datetime(2015, 6, 21, 12, 0, 0), 78.22, 15.63, 2.0, "Svalbard"
        ),  # Longyearbyen
        # Equinox/Solstice births
        Person(
            datetime(2021, 3, 20, 21, 37, 0), 40.7128, -74.0060, -4.0, "Equinox"
        ),  # Vernal
        Person(
            datetime(2021, 12, 21, 5, 59, 0), 40.7128, -74.0060, -5.0, "Solstice"
        ),  # Winter
        # Leap year edges
        Person(datetime(2020, 2, 29, 23, 59, 0), 51.5074, -0.1278, 0.0, "LeapYear"),
        Person(datetime(1900, 3, 1, 0, 0, 1), 51.5074, -0.1278, 0.0, "NonLeapCentury"),
    ]


@pytest.fixture
def birth_timezone_variety():
    """Birth data with fractional timezone offsets."""
    return [
        Person(
            datetime(2015, 8, 15, 10, 30, 0), 40.7128, -74.0060, -4.5, "ET_Minus45"
        ),  # EST with DST
        Person(
            datetime(2015, 8, 15, 15, 45, 0), 51.5074, -0.1278, 1.0, "LondonBST"
        ),  # BST
        Person(
            datetime(2015, 8, 15, 22, 15, 0), 19.0760, 72.8777, 5.5, "MumbaiIST"
        ),  # IST
        Person(
            datetime(2015, 8, 15, 8, 45, 0), 35.6762, 139.6503, 9.0, "TokyoJST"
        ),  # JST
    ]


# =============================================================================
# PRE-COMPUTED CHART FIXTURES
# =============================================================================


@pytest.fixture
def sample_vedic_chart_delhi():
    """Pre-computed chart for Delhi, 1994 - useful for manual verification."""
    birth = datetime(1994, 10, 23, 10, 20, 0)  # Nashik coordinates from test_ganita.py
    return calculate_birth_chart(birth, 19.9993, 73.7900, 5.5)


@pytest.fixture
def sample_vedic_chart_london():
    """Pre-computed chart for London."""
    birth = datetime(1985, 5, 15, 14, 30, 0)
    return calculate_birth_chart(birth, 51.5074, -0.1278, 1.0)  # BST equivalent


@pytest.fixture
def sample_vedic_chart_nyc():
    """Pre-computed chart for NYC."""
    birth = datetime(2007, 9, 11, 8, 46, 0)  # 9/11
    return calculate_birth_chart(birth, 40.7128, -74.0060, -4.0)  # EDT


# =============================================================================
# EXPECTED VALUES FOR MANUAL VERIFICATION
# =============================================================================


@pytest.fixture
def expected_ashtakavarga_benchmarks():
    """Expected Ashtakavarga bindu values for validation against classical texts."""
    return {
        "sun_bav_total": 48,  # Sun should sum to 48 bindus across retrograde path
        "moon_bav_total": 49,  # Moon should sum to 49 bindus
        "mars_bav_total": 39,  # Mars should sum to 39 bindus
        "mercury_bav_total": 54,  # Mercury should sum to 54 bindus
        "jupiter_bav_total": 56,  # Jupiter should sum to 56 bindus
        "venus_bav_total": 52,  # Venus should sum to 52 bindus
        "saturn_bav_total": 39,  # Saturn should sum to 39 bindus
    }


@pytest.fixture
def expected_shadbala_ranges():
    """Expected ranges for planetary strength validations."""
    return {
        "minimum_shadbala": 200.0,  # Theoretical minimum shadbala
        "maximum_shadbala": 600.0,  # Theoretical maximum shadbala
        "exalted_sun_range": (450.0, 500.0),  # Sun in Leo
        "exalted_moon_range": (450.0, 500.0),  # Moon in Taurus
        "debilitated_sun_range": (180.0, 220.0),  # Sun in Aquarius
        "debilitated_moon_range": (200.0, 250.0),  # Moon in Scorpio
    }


@pytest.fixture
def expected_dasha_start_ages():
    """Expected Vimshottari dasha start ages for common charts."""
    return {
        "sun_dasha_start_age": (0, 6),
        "moon_dasha_start_age": (0, 10),
        "mars_dasha_start_age": (28, 38),
        "mercury_dasha_start_age": (0, 17),
        "jupiter_dasha_start_age": (16, 26),
        "venus_dasha_start_age": (0, 20),
        "saturn_dasha_start_age": (43, 49),
    }


# =============================================================================
# PARAMETRIC FIXTURES
# =============================================================================


@pytest.fixture(
    params=[
        # Indian locations (IST +5.5)
        ("Mumbai", 19.0760, 72.8777, 5.5),
        ("Delhi", 28.6139, 77.2090, 5.5),
        ("Chennai", 13.0827, 80.2707, 5.5),
        ("Kolkata", 22.5726, 88.3639, 5.5),
        ("Bangalore", 12.9716, 77.5946, 5.5),
    ]
)
def indian_location(request):
    """Parametric fixture for Indian cities."""
    name, lat, lon, tz = request.param
    return {"name": name, "lat": lat, "lon": lon, "tz": tz}


@pytest.fixture(
    params=[
        # Western locations
        ("London", 51.5074, -0.1278, 0.0),
        ("New York", 40.7128, -74.0060, -5.0),
        ("Los Angeles", 34.0522, -118.2437, -8.0),
        ("Berlin", 52.5200, 13.4050, 1.0),
        ("Paris", 48.8566, 2.3522, 1.0),
        ("Rome", 41.9028, 12.4964, 1.0),
        ("Moscow", 55.7558, 37.6173, 3.0),
    ]
)
def western_location(request):
    """Parametric fixture for Western cities."""
    name, lat, lon, tz = request.param
    return {"name": name, "lat": lat, "lon": lon, "tz": tz}


@pytest.fixture(
    params=[
        # Eastern/Pacific locations
        ("Tokyo", 35.6762, 139.6503, 9.0),
        ("Sydney", -33.8688, 151.2093, 11.0),
        ("Shanghai", 31.2304, 121.4737, 8.0),
        ("Seoul", 37.5665, 126.9780, 9.0),
        ("Bangkok", 13.7563, 100.5018, 7.0),
    ]
)
def asian_pacific_location(request):
    """Parametric fixture for Asian/Pacific cities."""
    name, lat, lon, tz = request.param
    return {"name": name, "lat": lat, "lon": lon, "tz": tz}


@pytest.fixture(
    params=[
        datetime(1900, 1, 1),
        datetime(1950, 6, 15),
        datetime(1975, 12, 25),
        datetime(2000, 1, 1),
        datetime(2005, 7, 4),
        datetime(2010, 3, 21),
        datetime(2015, 8, 15),
        datetime(2020, 5, 10),
        datetime(2023, 12, 31),
    ]
)
def historical_birth_year(request):
    """Parametric fixture for various birth years."""
    birth_date = request.param
    return birth_date.replace(hour=12, minute=0, second=0)  # Standardize time
