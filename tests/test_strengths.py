"""
Pytest test suite for jyotishganit.components.strengths (Vedic Astrology Strength Calculations)
"""

import datetime
import os
import sys
from unittest.mock import Mock, patch

import pytest

# Add parent directory to path for imports if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jyotishganit.components.strengths import (
    angdiff,
    calculate_all_strengths,
    calculate_degrees_in_varga_sign,
    compute_ayanabala,
    compute_bhava_adhipathi_bala,
    compute_bhava_dig_bala,
    compute_bhava_drik_bala,
    compute_chestagbala,
    compute_digbala,
    compute_drekkanabala,
    compute_drikbala,
    compute_ishtakashtabalas,
    compute_kendradhibala,
    compute_naisargikabala,
    compute_nathonnatabala,
    compute_ojhayugmarashiamsabala,
    compute_pakshabala,
    compute_saptavargajabala,
    compute_shadbala,
    compute_sthanabala,
    compute_tribhagabala,
    compute_uchhabala,
    compute_vimshopaka_balas,
    compute_yuddhabala,
    get_angular_distance_between_planets,
    get_planetary_dignity_classification,
    get_sputa_drishti_degree,
    get_varga_sign,
    normalize,
    planet_longitude_from_sign,
)

# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def mock_planet():
    """Create a mock planet object."""
    planet = Mock()
    planet.celestial_body = "Sun"
    planet.sign = "Aries"
    planet.sign_degrees = 15.0
    planet.house = 1
    planet.shadbala = {}
    return planet


@pytest.fixture
def mock_chart():
    """Create a mock chart with planets and houses."""
    chart = Mock()
    chart.planets = []
    chart.houses = []

    # Create mock planets
    sun = Mock(
        celestial_body="Sun", sign="Aries", sign_degrees=10.0, house=1, shadbala={}
    )
    moon = Mock(
        celestial_body="Moon", sign="Taurus", sign_degrees=20.0, house=2, shadbala={}
    )
    mars = Mock(
        celestial_body="Mars", sign="Scorpio", sign_degrees=5.0, house=8, shadbala={}
    )
    mercury = Mock(
        celestial_body="Mercury", sign="Gemini", sign_degrees=15.0, house=3, shadbala={}
    )
    jupiter = Mock(
        celestial_body="Jupiter",
        sign="Sagittarius",
        sign_degrees=12.0,
        house=9,
        shadbala={},
    )
    venus = Mock(
        celestial_body="Venus", sign="Libra", sign_degrees=18.0, house=7, shadbala={}
    )
    saturn = Mock(
        celestial_body="Saturn",
        sign="Capricorn",
        sign_degrees=22.0,
        house=10,
        shadbala={},
    )

    chart.planets = [sun, moon, mars, mercury, jupiter, venus, saturn]

    # Create mock houses
    signs = [
        "Aries",
        "Taurus",
        "Gemini",
        "Cancer",
        "Leo",
        "Virgo",
        "Libra",
        "Scorpio",
        "Sagittarius",
        "Capricorn",
        "Aquarius",
        "Pisces",
    ]
    lords = [
        "Mars",
        "Venus",
        "Mercury",
        "Moon",
        "Sun",
        "Mercury",
        "Venus",
        "Mars",
        "Jupiter",
        "Saturn",
        "Saturn",
        "Jupiter",
    ]

    for i in range(12):
        house = Mock()
        house.sign = signs[i]
        house.sign_degrees = 0.0
        house.lord = lords[i]
        chart.houses.append(house)

    return chart


@pytest.fixture
def mock_person():
    """Create a mock person object."""
    person = Mock()
    person.birth_datetime = datetime.datetime(1990, 1, 1, 12, 0, 0)
    person.timezone_offset = 0
    person.latitude = 28.6139  # Delhi
    person.longitude = 77.2090
    return person


# ============================================================================
# HELPER FUNCTION TESTS
# ============================================================================


class TestHelperFunctions:
    """Test basic helper functions."""

    def test_normalize_positive(self):
        """Test normalize with positive angles."""
        assert normalize(370) == 10
        assert normalize(720) == 0
        assert normalize(180) == 180

    def test_normalize_negative(self):
        """Test normalize with negative angles."""
        assert normalize(-10) == 350
        assert normalize(-370) == 350

    def test_normalize_zero(self):
        """Test normalize with zero."""
        assert normalize(0) == 0

    def test_angdiff_basic(self):
        """Test angular difference calculation."""
        assert angdiff(10, 20) == 10
        assert angdiff(350, 10) == 20
        assert angdiff(0, 180) == 180

    def test_angdiff_wraparound(self):
        """Test angular difference with wraparound."""
        assert angdiff(10, 350) == 20
        assert angdiff(350, 10) == 20

    def test_planet_longitude_from_sign(self):
        """Test planet longitude calculation from sign and degrees."""
        assert planet_longitude_from_sign("Aries", 0) == 0
        assert planet_longitude_from_sign("Aries", 15) == 15
        assert planet_longitude_from_sign("Taurus", 0) == 30
        assert planet_longitude_from_sign("Pisces", 29.99) == pytest.approx(359.99)

    def test_calculate_degrees_in_varga_sign(self):
        """Test varga degree calculation."""
        # D9 (Navamsa) calculation
        result = calculate_degrees_in_varga_sign(15.0, 9)
        assert isinstance(result, float)
        assert 0 <= result < 30

    def test_get_varga_sign(self):
        """Test varga sign determination."""
        # D1 (Rasi) should return the same sign
        assert get_varga_sign(15.0, 1) == "Aries"
        assert get_varga_sign(45.0, 1) == "Taurus"

        # D9 (Navamsa)
        result = get_varga_sign(15.0, 9)
        assert result in [
            "Aries",
            "Taurus",
            "Gemini",
            "Cancer",
            "Leo",
            "Virgo",
            "Libra",
            "Scorpio",
            "Sagittarius",
            "Capricorn",
            "Aquarius",
            "Pisces",
        ]


# ============================================================================
# STHANABALA TESTS
# ============================================================================


class TestSthanabala:
    """Test Sthanabala (Positional Strength) calculations."""

    def test_compute_uchhabala(self, mock_chart):
        """Test Uchhabala (Exaltation Strength) calculation."""
        compute_uchhabala(mock_chart)

        # Check that Uchhabala was calculated for all planets
        for planet in mock_chart.planets:
            if planet.celestial_body in [
                "Sun",
                "Moon",
                "Mars",
                "Mercury",
                "Jupiter",
                "Venus",
                "Saturn",
            ]:
                assert "Sthanabala" in planet.shadbala
                assert "Uchhabala" in planet.shadbala["Sthanabala"]
                assert isinstance(planet.shadbala["Sthanabala"]["Uchhabala"], float)
                assert 0 <= planet.shadbala["Sthanabala"]["Uchhabala"] <= 60

    def test_get_planetary_dignity_classification(self, mock_chart):
        """Test planetary dignity classification."""
        # Sun in Leo (own sign)
        assert get_planetary_dignity_classification("Sun", "Leo", 15.0) == "own"

        # Moon in Taurus (moolatrikona)
        assert (
            get_planetary_dignity_classification("Moon", "Taurus", 2.0, True) == "mool"
        )

        # Mars in Aries with moolatrikona degrees
        result = get_planetary_dignity_classification("Mars", "Aries", 10.0, True)
        assert result in ["mool", "own"]

    def test_compute_saptavargajabala(self, mock_chart):
        """Test Saptavargaja Bala (Seven Divisional Chart Strength)."""
        compute_saptavargajabala(mock_chart)

        for planet in mock_chart.planets:
            if planet.celestial_body in [
                "Sun",
                "Moon",
                "Mars",
                "Mercury",
                "Jupiter",
                "Venus",
                "Saturn",
            ]:
                assert "Sthanabala" in planet.shadbala
                assert "Saptavargajabala" in planet.shadbala["Sthanabala"]
                # Score should be positive (7 divisions * scores)
                assert planet.shadbala["Sthanabala"]["Saptavargajabala"] > 0

    def test_compute_ojhayugmarashiamsabala(self, mock_chart):
        """Test Ojhayugmarashiamsa Bala (Odd/Even Sign Strength)."""
        compute_ojhayugmarashiamsabala(mock_chart)

        for planet in mock_chart.planets:
            if planet.celestial_body in [
                "Sun",
                "Moon",
                "Mars",
                "Mercury",
                "Jupiter",
                "Venus",
                "Saturn",
            ]:
                assert "Sthanabala" in planet.shadbala
                assert "Ojhayugmarashiamshabala" in planet.shadbala["Sthanabala"]
                bala = planet.shadbala["Sthanabala"]["Ojhayugmarashiamshabala"]
                # Should be 0, 15, or 30
                assert bala in [0.0, 15.0, 30.0]

    def test_compute_kendradhibala(self, mock_chart):
        """Test Kendradi Bala (Angular House Strength)."""
        compute_kendradhibala(mock_chart)

        for planet in mock_chart.planets:
            if planet.celestial_body in [
                "Sun",
                "Moon",
                "Mars",
                "Mercury",
                "Jupiter",
                "Venus",
                "Saturn",
            ]:
                assert "Sthanabala" in planet.shadbala
                assert "Kendradhibala" in planet.shadbala["Sthanabala"]
                bala = planet.shadbala["Sthanabala"]["Kendradhibala"]
                # Should be 60, 30, 15, or 7.5
                assert bala in [60.0, 30.0, 15.0, 7.5]

    def test_compute_drekkanabala(self, mock_chart):
        """Test Drekkana Bala (Decanate Strength)."""
        compute_drekkanabala(mock_chart)

        for planet in mock_chart.planets:
            if planet.celestial_body in [
                "Sun",
                "Moon",
                "Mars",
                "Mercury",
                "Jupiter",
                "Venus",
                "Saturn",
            ]:
                assert "Sthanabala" in planet.shadbala
                assert "Drekshanabala" in planet.shadbala["Sthanabala"]
                bala = planet.shadbala["Sthanabala"]["Drekshanabala"]
                # Should be 0 or 15
                assert bala in [0.0, 15.0]

    def test_compute_sthanabala_total(self, mock_chart):
        """Test total Sthanabala calculation."""
        compute_sthanabala(mock_chart)

        for planet in mock_chart.planets:
            if planet.celestial_body in [
                "Sun",
                "Moon",
                "Mars",
                "Mercury",
                "Jupiter",
                "Venus",
                "Saturn",
            ]:
                assert "Sthanabala" in planet.shadbala
                assert "Total" in planet.shadbala["Sthanabala"]
                assert planet.shadbala["Sthanabala"]["Total"] > 0


# ============================================================================
# DIGBALA TESTS
# ============================================================================


class TestDigbala:
    """Test Digbala (Directional Strength) calculations."""

    def test_compute_digbala(self, mock_chart):
        """Test Digbala calculation."""
        compute_digbala(mock_chart)

        for planet in mock_chart.planets:
            if (
                planet.celestial_body
                in [
                    "Sun",
                    "Moon",
                    "Mars",
                    "Mercury",
                    "Jupiter",
                    "Venus",
                    "Saturn",
                ]
                and "Digbala" in planet.shadbala
            ):
                assert isinstance(planet.shadbala["Digbala"], float)
                assert 0 <= planet.shadbala["Digbala"] <= 60


# ============================================================================
# KAALABALA TESTS
# ============================================================================


class TestKaalabala:
    """Test Kaalabala (Temporal Strength) calculations."""

    @patch("jyotishganit.core.astronomical.get_sunrise_sunset")
    def test_compute_nathonnatabala(self, mock_sunrise_sunset, mock_chart, mock_person):
        """Test Natonnata Bala (Day/Night Strength)."""
        mock_sunrise_sunset.return_value = (6.0, 18.0)

        compute_nathonnatabala(mock_chart, mock_person)

        for planet in mock_chart.planets:
            if planet.celestial_body in [
                "Sun",
                "Moon",
                "Mars",
                "Mercury",
                "Jupiter",
                "Venus",
                "Saturn",
            ]:
                assert "Kaalabala" in planet.shadbala
                assert "Natonnatabala" in planet.shadbala["Kaalabala"]
                bala = planet.shadbala["Kaalabala"]["Natonnatabala"]
                assert 0 <= bala <= 60

    def test_compute_pakshabala(self, mock_chart):
        """Test Paksha Bala (Lunar Phase Strength)."""
        compute_pakshabala(mock_chart)

        for planet in mock_chart.planets:
            if planet.celestial_body in [
                "Sun",
                "Moon",
                "Mars",
                "Mercury",
                "Jupiter",
                "Venus",
                "Saturn",
            ]:
                assert "Kaalabala" in planet.shadbala
                assert "Pakshabala" in planet.shadbala["Kaalabala"]
                bala = planet.shadbala["Kaalabala"]["Pakshabala"]
                assert 0 <= bala <= 60

    @patch("jyotishganit.core.astronomical.get_sunrise_sunset")
    def test_compute_tribhagabala(self, mock_sunrise_sunset, mock_chart, mock_person):
        """Test Tribhaga Bala (Day/Night Third Division Strength)."""
        mock_sunrise_sunset.return_value = (6.0, 18.0)

        compute_tribhagabala(mock_chart, mock_person)

        for planet in mock_chart.planets:
            if planet.celestial_body in [
                "Sun",
                "Moon",
                "Mars",
                "Mercury",
                "Jupiter",
                "Venus",
                "Saturn",
            ]:
                assert "Kaalabala" in planet.shadbala
                assert "Tribhagabala" in planet.shadbala["Kaalabala"]
                bala = planet.shadbala["Kaalabala"]["Tribhagabala"]
                assert bala in [0.0, 60.0]

    @patch("jyotishganit.components.strengths.get_planet_declination")
    @patch("jyotishganit.components.strengths.skyfield_time_from_datetime")
    def test_compute_ayanabala(
        self, mock_skyfield, mock_declination, mock_chart, mock_person
    ):
        """Test Ayana Bala (Declination Strength)."""
        mock_skyfield.return_value = Mock()
        mock_declination.return_value = 10.0  # Sample declination

        compute_ayanabala(mock_chart, mock_person)

        for planet in mock_chart.planets:
            if planet.celestial_body in [
                "Sun",
                "Moon",
                "Mars",
                "Mercury",
                "Jupiter",
                "Venus",
                "Saturn",
            ]:
                assert "Kaalabala" in planet.shadbala
                assert "Ayanabala" in planet.shadbala["Kaalabala"]
                bala = planet.shadbala["Kaalabala"]["Ayanabala"]
                # Sun's Ayana Bala can be up to 120
                max_bala = 120 if planet.celestial_body == "Sun" else 60
                assert 0 <= bala <= max_bala


# ============================================================================
# CHESHTABALA TESTS
# ============================================================================


class TestCheshtabala:
    """Test Cheshtabala (Motional Strength) calculations."""

    @patch("jyotishganit.components.strengths._get_mean_longitude_from_skyfield")
    @patch("jyotishganit.components.strengths.skyfield_time_from_datetime")
    def test_compute_chestagbala(
        self, mock_skyfield, mock_mean_long, mock_chart, mock_person
    ):
        """Test Cheshta Bala calculation."""
        mock_skyfield.return_value = Mock()
        mock_mean_long.return_value = 100.0

        compute_chestagbala(mock_chart, mock_person)

        for planet in mock_chart.planets:
            if planet.celestial_body in [
                "Mars",
                "Mercury",
                "Jupiter",
                "Venus",
                "Saturn",
            ]:
                assert "Cheshtabala" in planet.shadbala
                assert isinstance(planet.shadbala["Cheshtabala"], float)
                assert 0 <= planet.shadbala["Cheshtabala"] <= 60


# ============================================================================
# YUDDHABALA TESTS
# ============================================================================


class TestYuddhabala:
    """Test Yuddhabala (Planetary War Strength) calculations."""

    def test_compute_yuddhabala_no_war(self, mock_chart):
        """Test Yuddha Bala when planets are not in war."""
        # Ensure planets are far apart - update their positions
        for i, planet in enumerate(mock_chart.planets):
            planet.sign_degrees = (i * 20.0) % 30  # Spread them out
            planet.shadbala = {"Shadbala": {"Total": 100.0}, "Kaalabala": {}}

        compute_yuddhabala(mock_chart)

        # All Yuddhabala should be 0
        for planet in mock_chart.planets:
            if planet.celestial_body in [
                "Mars",
                "Mercury",
                "Jupiter",
                "Venus",
                "Saturn",
            ]:
                assert planet.shadbala["Kaalabala"]["Yuddhabala"] == 0.0

    def test_compute_yuddhabala_with_war(self, mock_chart):
        """Test Yuddha Bala when planets are in war (within 1 degree)."""
        # Put Mars and Jupiter very close
        mars = next(p for p in mock_chart.planets if p.celestial_body == "Mars")
        jupiter = next(p for p in mock_chart.planets if p.celestial_body == "Jupiter")

        mars.sign = "Aries"
        mars.sign_degrees = 10.0
        jupiter.sign = "Aries"
        jupiter.sign_degrees = 10.5  # Within 1 degree

        mars.shadbala = {"Shadbala": {"Total": 150.0}, "Kaalabala": {}}
        jupiter.shadbala = {"Shadbala": {"Total": 100.0}, "Kaalabala": {}}

        compute_yuddhabala(mock_chart)

        # Mars should win, Jupiter should lose
        assert mars.shadbala["Kaalabala"]["Yuddhabala"] > 0
        assert jupiter.shadbala["Kaalabala"]["Yuddhabala"] < 0


# ============================================================================
# NAISARGIKABALA TESTS
# ============================================================================


class TestNaisargikabala:
    """Test Naisargika Bala (Natural Strength) calculations."""

    def test_compute_naisargikabala(self, mock_chart):
        """Test Naisargika Bala calculation."""
        compute_naisargikabala(mock_chart)

        for planet in mock_chart.planets:
            if planet.celestial_body in [
                "Sun",
                "Moon",
                "Mars",
                "Mercury",
                "Jupiter",
                "Venus",
                "Saturn",
            ]:
                assert "Naisargikabala" in planet.shadbala
                assert isinstance(planet.shadbala["Naisargikabala"], (int, float))
                assert planet.shadbala["Naisargikabala"] > 0


# ============================================================================
# DRIKBALA TESTS
# ============================================================================


class TestDrikbala:
    """Test Drikbala (Aspectual Strength) calculations."""

    def test_get_angular_distance_between_planets(self, mock_chart):
        """Test angular distance calculation between planets."""
        dist = get_angular_distance_between_planets(mock_chart, "Sun", "Moon")
        assert isinstance(dist, float)
        assert -180 <= dist <= 180

    def test_get_sputa_drishti_degree(self):
        """Test Sputa Drishti calculation."""
        # 7th aspect (180°) should be strongest (60)
        assert get_sputa_drishti_degree(180, "Sun") == pytest.approx(60, abs=1)

        # No aspect at 0° or 360°
        assert get_sputa_drishti_degree(0, "Sun") == pytest.approx(0, abs=1)

        # Mars special aspects at 90° and 150°
        mars_90 = get_sputa_drishti_degree(90, "Mars")
        assert mars_90 >= 45  # Should be strong

    def test_compute_drikbala(self, mock_chart):
        """Test Drik Bala calculation."""
        compute_drikbala(mock_chart)

        for planet in mock_chart.planets:
            if planet.celestial_body in [
                "Sun",
                "Moon",
                "Mars",
                "Mercury",
                "Jupiter",
                "Venus",
                "Saturn",
            ]:
                assert "Drikbala" in planet.shadbala
                assert isinstance(planet.shadbala["Drikbala"], float)


# ============================================================================
# SHADBALA TESTS
# ============================================================================


class TestShadbala:
    """Test complete Shadbala calculations."""

    @patch("jyotishganit.components.strengths.skyfield_time_from_datetime")
    @patch("jyotishganit.components.strengths.get_planet_declination")
    @patch("jyotishganit.core.astronomical.get_sunrise_sunset")
    def test_compute_shadbala(
        self, mock_sunrise, mock_decl, mock_skyfield, mock_chart, mock_person
    ):
        """Test complete Shadbala calculation."""
        mock_sunrise.return_value = (6.0, 18.0)
        mock_decl.return_value = 10.0

        # Mock time object with tt attribute (Julian date)
        mock_time = Mock()
        mock_time.tt = 2451545.0  # J2000.0 epoch
        mock_skyfield.return_value = mock_time

        compute_shadbala(mock_chart, mock_person)

        for planet in mock_chart.planets:
            if planet.celestial_body in [
                "Sun",
                "Moon",
                "Mars",
                "Mercury",
                "Jupiter",
                "Venus",
                "Saturn",
            ]:
                assert "Shadbala" in planet.shadbala
                assert "Total" in planet.shadbala["Shadbala"]
                assert "Rupas" in planet.shadbala["Shadbala"]
                assert planet.shadbala["Shadbala"]["Total"] > 0
                assert planet.shadbala["Shadbala"]["Rupas"] > 0


# ============================================================================
# VIMSHOPAKA BALA TESTS
# ============================================================================


class TestVimshopakaБала:
    """Test Vimshopaka Bala calculations."""

    def test_compute_vimshopaka_balas(self, mock_chart):
        """Test Vimshopaka Bala calculation."""
        compute_vimshopaka_balas(mock_chart)

        for planet in mock_chart.planets:
            if planet.celestial_body in [
                "Sun",
                "Moon",
                "Mars",
                "Mercury",
                "Jupiter",
                "Venus",
                "Saturn",
            ]:
                assert "Vimshopaka" in planet.shadbala
                assert isinstance(planet.shadbala["Vimshopaka"], dict)
                assert len(planet.shadbala["Vimshopaka"]) > 0


# ============================================================================
# ISHTA/KASHTA BALA TESTS
# ============================================================================


class TestIshtaKashtaBala:
    """Test Ishta and Kashta Bala calculations."""

    def test_compute_ishtakashtabalas(self, mock_chart):
        """Test Ishta and Kashta Bala calculation."""
        # Setup required prerequisites
        for planet in mock_chart.planets:
            planet.shadbala = {"Sthanabala": {"Uchhabala": 30.0}, "Cheshtabala": 40.0}

        compute_ishtakashtabalas(mock_chart)

        for planet in mock_chart.planets:
            if planet.celestial_body in [
                "Sun",
                "Moon",
                "Mars",
                "Mercury",
                "Jupiter",
                "Venus",
                "Saturn",
            ]:
                assert "Ishtabala" in planet.shadbala
                assert "Kashtabala" in planet.shadbala
                assert planet.shadbala["Ishtabala"] + planet.shadbala[
                    "Kashtabala"
                ] == pytest.approx(60, abs=0.1)


# ============================================================================
# BHAVA BALA TESTS
# ============================================================================


class TestBhavaBala:
    """Test Bhava Bala (House Strength) calculations."""

    def test_compute_bhava_adhipathi_bala(self, mock_chart):
        """Test Bhava Adhipathi Bala (House Lord Strength)."""
        # Setup Shadbala for lords
        for planet in mock_chart.planets:
            planet.shadbala = {"Shadbala": {"Total": 100.0}}

        compute_bhava_adhipathi_bala(mock_chart)

        for house in mock_chart.houses:
            assert hasattr(house, "bhava_bala_adhipathi")
            assert house.bhava_bala_adhipathi >= 0

    def test_compute_bhava_dig_bala(self, mock_chart):
        """Test Bhava Dig Bala (House Directional Strength)."""
        compute_bhava_dig_bala(mock_chart)

        for house in mock_chart.houses:
            assert hasattr(house, "bhava_dig_bala")
            assert isinstance(house.bhava_dig_bala, float)
            assert house.bhava_dig_bala >= 0

    @patch("jyotishganit.components.strengths.planet_longitude_from_sign")
    def test_compute_bhava_drik_bala(self, mock_long, mock_chart):
        """Test Bhava Drik Bala (House Aspectual Strength)."""
        mock_long.return_value = 15.0

        # Setup houses with sign_degrees
        for house in mock_chart.houses:
            house.sign_degrees = 0.0

        compute_bhava_drik_bala(mock_chart)

        for house in mock_chart.houses:
            assert hasattr(house, "bhava_drik_bala")
            assert isinstance(house.bhava_drik_bala, float)


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


class TestIntegration:
    """Integration tests for complete calculations."""

    @patch("jyotishganit.components.strengths.skyfield_time_from_datetime")
    @patch("jyotishganit.components.strengths.get_planet_declination")
    @patch("jyotishganit.core.astronomical.get_sunrise_sunset")
    def test_calculate_all_strengths(
        self, mock_sunrise, mock_decl, mock_skyfield, mock_chart, mock_person
    ):
        """Test complete strength calculation pipeline."""
        mock_sunrise.return_value = (6.0, 18.0)
        mock_decl.return_value = 10.0

        # Mock time object with tt attribute (Julian date)
        mock_time = Mock()
        mock_time.tt = 2451545.0  # J2000.0 epoch
        mock_skyfield.return_value = mock_time

        result = calculate_all_strengths(mock_chart, mock_person)

        assert result == mock_chart

        # Verify all planets have shadbala calculated
        for planet in mock_chart.planets:
            if planet.celestial_body in [
                "Sun",
                "Moon",
                "Mars",
                "Mercury",
                "Jupiter",
                "Venus",
                "Saturn",
            ]:
                assert "Shadbala" in planet.shadbala
                assert "Vimshopaka" in planet.shadbala
                assert "Ishtabala" in planet.shadbala
                assert "Kashtabala" in planet.shadbala

        # Verify houses have bhava bala calculated
        for house in mock_chart.houses:
            assert hasattr(house, "bhava_bala")


# ============================================================================
# EDGE CASE TESTS
# ============================================================================


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_normalize_large_angles(self):
        """Test normalize with very large angles."""
        assert normalize(1000) == normalize(1000 % 360)
        assert normalize(-1000) == normalize(-1000 % 360)

    def test_angdiff_exact_opposition(self):
        """Test angular difference at exact opposition."""
        assert angdiff(0, 180) == 180
        assert angdiff(180, 0) == 180

    def test_planet_at_sign_boundary(self):
        """Test calculations when planet is at sign boundary."""
        long = planet_longitude_from_sign("Aries", 29.99)
        assert 29.99 <= long < 30

    def test_varga_sign_at_boundaries(self):
        """Test varga sign calculation at boundaries."""
        # Test at 0 degrees
        assert get_varga_sign(0.0, 1) == "Aries"
        # Test at 359.99 degrees
        assert get_varga_sign(359.99, 1) == "Pisces"

    def test_empty_chart(self):
        """Test handling of chart with no planets."""
        empty_chart = Mock()
        empty_chart.planets = []
        empty_chart.houses = []

        # Should not raise errors
        compute_naisargikabala(empty_chart)
        compute_vimshopaka_balas(empty_chart)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
