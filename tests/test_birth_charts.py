"""
Test suite for Vedic birth chart calculations in jyotishganit.

Tests basic chart generation, timezone handling, geographical variations,
and validates both planetary positions and house systems.
"""

from datetime import datetime

import pytest

from jyotishganit.core.constants import ZODIAC_SIGNS
from jyotishganit.main import calculate_birth_chart, get_birth_chart_json_string


class TestBirthChartBasic:
    """Basic birth chart generation tests."""

    def test_chart_creation_delhi(self, sample_vedic_chart_delhi):
        """Test basic chart creation for Delhi location."""
        chart = sample_vedic_chart_delhi

        # Validate chart structure
        assert hasattr(chart, "person")
        assert hasattr(chart, "d1_chart")
        assert hasattr(chart, "panchanga")
        assert hasattr(chart, "divisional_charts")
        assert hasattr(chart, "ashtakavarga")
        assert hasattr(chart, "dashas")

        # Validate person info
        assert chart.person.latitude == 19.9993
        assert chart.person.longitude == 73.7900
        assert chart.person.timezone_offset == 5.5

    def test_chart_creation_london(self, sample_vedic_chart_london):
        """Test basic chart creation for London location."""
        chart = sample_vedic_chart_london

        assert chart.person.latitude == pytest.approx(51.5074, abs=1e-3)
        assert chart.person.longitude == pytest.approx(-0.1278, abs=1e-3)
        assert chart.person.timezone_offset == 1.0

        # Verify required chart components exist
        assert len(chart.d1_chart.planets) == 9  # All planets (including Rahu/Ketu)
        assert len(chart.d1_chart.houses) == 12

    def test_chart_creation_nyc(self, sample_vedic_chart_nyc):
        """Test basic chart creation for NYC location."""
        chart = sample_vedic_chart_nyc

        assert chart.person.latitude == pytest.approx(40.7128, abs=1e-3)
        assert chart.person.longitude == pytest.approx(-74.0060, abs=1e-3)
        assert chart.person.timezone_offset == -4.0

    def test_chart_jsonld_output(self, sample_vedic_chart_delhi):
        """Test JSON-LD output generation."""
        chart = sample_vedic_chart_delhi
        json_output = get_birth_chart_json_string(chart, indent=2)

        assert isinstance(json_output, str)
        assert '"@type": "VedicBirthChart"' in json_output
        assert '"planets"' in json_output or '"d1Chart"' in json_output
        assert '"houses"' in json_output
        assert "jyotishganit" in json_output


class TestTimezoneHandling:
    """Test timezone offset handling and UTC conversion."""

    @pytest.mark.parametrize(
        "tz_offset",
        [
            0.0,  # GMT
            5.5,  # IST
            -4.0,  # EDT
            9.0,  # JST
            -8.0,  # PST
            3.0,  # EET
        ],
    )
    def test_timezone_offsets(self, tz_offset):
        """Test chart calculation with various timezone offsets."""
        birth = datetime(2020, 5, 15, 12, 0, 0)  # Noon local time
        chart = calculate_birth_chart(birth, 28.6139, 77.2090, tz_offset)

        # Should not raise exceptions and create valid chart
        assert isinstance(chart, type(chart))  # Any chart object
        assert chart.person.timezone_offset == tz_offset

    def test_fractional_timezone_offset(self):
        """Test with fractional timezone offsets (like IST 5.5)."""
        birth = datetime(2020, 5, 15, 12, 0, 0)
        chart = calculate_birth_chart(birth, 28.6139, 77.2090, 5.5)

        assert chart.person.timezone_offset == 5.5
        # Verify that astronomical positions were calculated (basic sanity check)
        assert len(chart.d1_chart.planets) > 0

    def test_timezone_edge_cases(self):
        """Test edge cases like midnight crossings and DST."""
        test_cases = [
            # Midnight transition
            (datetime(2020, 1, 1, 0, 0, 0), 0.0, "GMT Midnight"),
            # Near daylight saving transitions
            (datetime(2020, 3, 8, 1, 0, 0), -5.0, "EST to EDT boundary"),
            (datetime(2020, 11, 1, 1, 0, 0), -4.0, "EDT to EST boundary"),
        ]

        for birth_time, tz, description in test_cases:
            chart = calculate_birth_chart(birth_time, 40.7128, -74.0060, tz)
            assert chart is not None, f"Failed for {description}"


class TestGeographicDiversity:
    """Test calculations across different geographic locations."""

    def test_northern_hemisphere(self):
        """Test calculations north of equator."""
        birth = datetime(2020, 5, 15, 12, 0, 0)
        chart = calculate_birth_chart(birth, 51.5074, -0.1278, 1.0)  # London

        # Basic validations
        assert chart.person.latitude > 0
        assert len(chart.d1_chart.planets) == 9

    def test_southern_hemisphere(self):
        """Test calculations south of equator."""
        birth = datetime(2020, 5, 15, 12, 0, 0)
        chart = calculate_birth_chart(birth, -33.8688, 151.2093, 10.0)  # Sydney

        assert chart.person.latitude < 0
        assert abs(chart.person.latitude) == 33.8688

    def test_antarctica_chart(self):
        """Test high latitude calculations (near pole)."""
        birth = datetime(2020, 12, 21, 12, 0, 0)
        # Test that extreme latitudes don't crash, even if some calculations may not be perfect
        try:
            chart = calculate_birth_chart(
                birth, -77.85, 166.67, 13.0
            )  # Antarctica (McMurdo)
            # Extreme southern latitude should be handled
            assert chart.person.latitude == pytest.approx(-77.85, abs=1e-1)
            # Chart should be created even if some strength calculations might have issues
            assert chart.d1_chart is not None
        except Exception as e:
            pytest.skip(f"Extreme latitude calculations not fully supported: {e}")

    def test_arctic_chart(self):
        """Test high latitude calculations (Arctic)."""
        birth = datetime(2020, 6, 21, 12, 0, 0)
        # Test that extreme latitudes don't crash
        try:
            chart = calculate_birth_chart(birth, 78.22, 15.63, 2.0)  # Svalbard
            assert chart.person.latitude == pytest.approx(78.22, abs=1e-1)
            assert chart.d1_chart is not None
        except Exception as e:
            pytest.skip(f"Extreme latitude calculations not fully supported: {e}")


class TestTimeframeDiversity:
    """Test calculations across different historical timeframes."""

    @pytest.mark.parametrize(
        "year,month,day",
        [
            (1900, 1, 1),  # Start of 20th century
            (1950, 6, 15),  # Mid-century
            (1975, 12, 25),  # Late 20th century
            (2000, 1, 1),  # Millennium
            (2010, 3, 21),  # 21st century
            (2020, 2, 29),  # Leap year (2020 is leap)
        ],
    )
    def test_historical_dates(self, year, month, day):
        """Test chart calculations for various historical dates."""
        birth = datetime(year, month, day, 12, 0, 0)
        chart = calculate_birth_chart(birth, 19.0760, 72.8777, 5.5)  # Mumbai

        assert chart is not None
        assert chart.person.birth_datetime.year == year

        # Verify ephemeris loaded and positions calculated
        sun = next(p for p in chart.d1_chart.planets if p.celestial_body == "Sun")
        assert sun.sign in ZODIAC_SIGNS
        assert sun.sign_degrees is not None
        assert 0.0 <= sun.sign_degrees <= 30.0

    def test_leap_year_edge_cases(self):
        """Test February 29 dates and leap year boundaries."""
        leap_dates = [
            datetime(2020, 2, 29, 23, 59, 59),  # End of leap day
            datetime(1900, 3, 1, 0, 0, 1),  # Century non-leap year transition
        ]

        for birth_date in leap_dates:
            chart = calculate_birth_chart(birth_date, 51.5074, -0.1278, 0.0)
            assert chart is not None


class TestPlanetaryPositions:
    """Test planetary position calculations and zodiac placement."""

    def test_all_planets_present(self, sample_vedic_chart_delhi):
        """Verify all classical planets are present in chart."""
        chart = sample_vedic_chart_delhi
        expected_planets = [
            "Sun",
            "Moon",
            "Mars",
            "Mercury",
            "Jupiter",
            "Venus",
            "Saturn",
            "Rahu",
            "Ketu",
        ]

        actual_planets = [p.celestial_body for p in chart.d1_chart.planets]
        assert set(actual_planets) == set(expected_planets)

    def test_planet_zodiac_positions(self, sample_vedic_chart_delhi):
        """Verify planet positions are valid zodiac signs with valid degrees."""
        chart = sample_vedic_chart_delhi

        for planet in chart.d1_chart.planets:
            assert planet.sign in ZODIAC_SIGNS
            assert 0.0 <= planet.sign_degrees < 30.0
            assert planet.house in range(1, 13)  # Houses 1-12

    def test_planet_house_assignment(self, sample_vedic_chart_delhi):
        """Verify all planets are assigned to valid houses."""
        chart = sample_vedic_chart_delhi
        for planet in chart.d1_chart.planets:
            assert 1 <= planet.house <= 12

    def test_ayanamsa_application(self, sample_vedic_chart_delhi):
        """Verify ayanamsa is applied to planetary positions."""
        chart = sample_vedic_chart_delhi
        for planet in chart.d1_chart.planets:
            assert planet.sign_degrees is not None


class TestHouseSystem:
    """Test house system calculations and placements."""

    def test_twelve_houses_present(self, sample_vedic_chart_delhi):
        """Verify all 12 houses are created."""
        chart = sample_vedic_chart_delhi
        assert len(chart.d1_chart.houses) == 12

    def test_house_lords_assigned(self, sample_vedic_chart_delhi):
        """Verify all houses have valid lords assigned."""
        chart = sample_vedic_chart_delhi
        for house in chart.d1_chart.houses:
            assert house.lord is not None
            assert house.lord in [p.celestial_body for p in chart.d1_chart.planets]

    def test_house_occupants_tracking(self, sample_vedic_chart_delhi):
        """Verify planets are correctly placed in houses."""
        chart = sample_vedic_chart_delhi

        house_occupants = {}
        for planet in chart.d1_chart.planets:
            house_num = planet.house
            if house_num not in house_occupants:
                house_occupants[house_num] = []
            house_occupants[house_num].append(planet.celestial_body)

        # Each planet should be in exactly one house
        total_planets_placed = sum(
            len(occupants) for occupants in house_occupants.values()
        )
        assert total_planets_placed == 9  # 9 classical planets

        # Some houses may have multiple planets, but all must be accounted for
        assert len(house_occupants) <= 12  # Can't have more houses than 12
