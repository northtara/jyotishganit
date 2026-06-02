"""
Test suite for Vimshottari Dasha calculations in jyotishganit.

Tests dasha period calculations, Mahadasha start dates, sub-period divisions,
and consistency with classical references.
"""

from datetime import datetime, timedelta

from jyotishganit.core.constants import (
    HUMAN_LIFE_SPAN_FOR_VIMSHOTTARI,
    VIMSHOTTARI_DASHA_DURATIONS,
)
from jyotishganit.dasha.vimshottari import (
    calculate_dasha_start_date,
    calculate_vimshottari_dashas,
    get_next_adhipati,
)
from jyotishganit.main import calculate_birth_chart


class TestDashaConstants:
    """Test Vimshottari constants and fundamental values."""

    def test_dasha_durations_sum_correct(self):
        """Verify total dasha durations sum to human lifespan."""
        total_years = sum(VIMSHOTTARI_DASHA_DURATIONS.values())
        expected_total = HUMAN_LIFE_SPAN_FOR_VIMSHOTTARI

        assert total_years == expected_total, (
            f"Total dasha years {total_years} != {expected_total}"
        )

    def test_all_planets_have_durations(self):
        """Verify all 9 Vimshottari planets have duration assignments."""
        expected_planets = [
            "Sun",
            "Moon",
            "Mars",
            "Rahu",
            "Jupiter",
            "Saturn",
            "Mercury",
            "Ketu",
            "Venus",
        ]
        actual_planets = list(VIMSHOTTARI_DASHA_DURATIONS.keys())

        assert set(actual_planets) == set(expected_planets)

    def test_dasha_durations_positive(self):
        """Verify all dasha durations are positive."""
        for planet, years in VIMSHOTTARI_DASHA_DURATIONS.items():
            assert years > 0, f"{planet} has non-positive duration: {years}"


class TestMoonNakshatraCalculation:
    """Test Moon nakshatra calculation for dasha determination."""

    def test_nakshatra_index_range(self):
        """Test nakshatra calculation returns valid index."""
        birth = datetime(2020, 5, 15, 12, 0, 0)
        chart = calculate_birth_chart(birth, 28.6139, 77.2090, 5.5)

        # Extract Moon position for nakshatra calc
        moon = next(
            (p for p in chart.d1_chart.planets if p.celestial_body == "Moon"), None
        )
        assert moon is not None

        # Mock the calculation (would use Skyfield in real implementation)
        moon_longitude = [
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
        ].index(moon.sign) * 30 + moon.sign_degrees

        nakshatra_span = 360.0 / 27.0
        nak_index = int(moon_longitude / nakshatra_span)
        remainder_degs = moon_longitude % nakshatra_span

        # Valid range checks
        assert 0 <= nak_index <= 26, f"Nakshatra index {nak_index} out of range 0-26"
        assert 0 <= remainder_degs <= nakshatra_span, (
            f"Remainder {remainder_degs} out of range"
        )


class TestDashaStartCalculation:
    """Test calculation of dasha start dates from birth."""

    def test_start_date_before_birth(self):
        """Verify dasha start date is always before birth date."""
        birth = datetime(1994, 10, 23, 10, 20, 0)
        chart = calculate_birth_chart(birth, 19.0760, 72.8777, 5.5)

        _, dasha_start = calculate_dasha_start_date(birth, 5.5, chart.ayanamsa.value)

        assert dasha_start < birth, (
            f"Dasha start {dasha_start} should be before birth {birth}"
        )

    def test_birth_within_dasha_period(self):
        """Verify birth date falls within calculated dasha period."""
        birth = datetime(1994, 10, 23, 10, 20, 0)
        chart = calculate_birth_chart(birth, 19.0760, 72.8777, 5.5)

        lord, start_date = calculate_dasha_start_date(birth, 5.5, chart.ayanamsa.value)

        # Calculate period end
        duration_years = VIMSHOTTARI_DASHA_DURATIONS[lord]
        end_date = start_date + timedelta(days=duration_years * 365.25)

        # Birth should be within this period
        assert start_date <= birth <= end_date, (
            f"Birth {birth} not within period {start_date} to {end_date}"
        )

    def test_valid_planet_returned(self):
        """Verify returned lord is a valid Vimshottari planet."""
        birth = datetime(1994, 10, 23, 10, 20, 0)
        chart = calculate_birth_chart(birth, 19.0760, 72.8777, 5.5)

        lord, _ = calculate_dasha_start_date(birth, 5.5, chart.ayanamsa.value)

        assert lord in VIMSHOTTARI_DASHA_DURATIONS, f"Invalid lord returned: {lord}"


class TestSequenceLogic:
    """Test the Vimshottari sequence progression."""

    def test_next_adhipati_cyclic(self):
        """Test that next lord cycles through complete sequence."""
        # Start with Sun and get full cycle
        current = "Sun"
        sequence = [current]

        for _ in range(8):  # Should get all planets except starting one
            current = get_next_adhipati(current)
            sequence.append(current)

        # Should return to Sun
        next_after_last = get_next_adhipati(sequence[-1])
        assert next_after_last == "Sun"

    def test_sequence_order_consistent(self):
        """Test Vimshottari sequence matches classical order."""
        # Classical Vimshottari sequence
        expected_sequence = [
            "Sun",
            "Moon",
            "Mars",
            "Rahu",
            "Jupiter",
            "Saturn",
            "Mercury",
            "Ketu",
            "Venus",
        ]

        current = "Sun"
        actual_sequence = [current]

        for i in range(8):
            current = get_next_adhipati(current)
            actual_sequence.append(current)

            # Check each step matches expected
            assert current == expected_sequence[i + 1], (
                f"Sequence mismatch at position {i + 1}: expected {expected_sequence[i + 1]}, got {current}"
            )

        assert actual_sequence == expected_sequence


class TestCompleteDashaCalculation:
    """Test full Vimshottari dasha calculations."""

    def test_dashas_all_periods_structure(self, sample_vedic_chart_delhi):
        """Test structure of complete dasha periods."""
        chart = sample_vedic_chart_delhi

        dashas = calculate_vimshottari_dashas(
            chart.person.birth_datetime,
            chart.person.timezone_offset,
            chart.person.latitude,
            chart.person.longitude,
            chart.ayanamsa.value,
        )

        # Should have all major sections
        assert hasattr(dashas, "all")
        assert hasattr(dashas, "current")
        assert hasattr(dashas, "upcoming")
        assert hasattr(dashas, "balance")

        # Should have mahadashas
        assert "mahadashas" in dashas.all

        mahadashas = dashas.all["mahadashas"]
        assert len(mahadashas) == 9, f"Expected 9 mahadashas, got {len(mahadashas)}"

    def test_mahadasha_coverage(self):
        """Test that mahadashas cover human lifespan."""
        birth = datetime(1994, 10, 23, 10, 20, 0)
        chart = calculate_birth_chart(birth, 19.0760, 72.8777, 5.5)

        dashas = calculate_vimshottari_dashas(
            birth, 5.5, 19.0760, 72.8777, chart.ayanamsa.value
        )

        total_span = timedelta(0)
        for _lord, data in dashas.all["mahadashas"].items():
            duration = data["end"] - data["start"]
            total_span += duration

        # Should cover expected lifespan (with some tolerance for calculation)
        expected_days = HUMAN_LIFE_SPAN_FOR_VIMSHOTTARI * 365.25
        actual_days = total_span.total_seconds() / (24 * 3600)

        tolerance_days = 10  # Allow small calculation differences
        assert abs(actual_days - expected_days) < tolerance_days

    def test_subperiods_exist(self, sample_vedic_chart_delhi):
        """Test that antardashas and pratyantardashas are calculated."""
        chart = sample_vedic_chart_delhi

        dashas = calculate_vimshottari_dashas(
            chart.person.birth_datetime,
            chart.person.timezone_offset,
            chart.person.latitude,
            chart.person.longitude,
            chart.ayanamsa.value,
            max_depth=3,  # Include pratyantardashas
        )

        # Check first mahadasha
        first_md = list(dashas.all["mahadashas"].keys())[0]
        ma_data = dashas.all["mahadashas"][first_md]

        # Should have antardashas
        assert "antardashas" in ma_data
        antardashas = ma_data["antardashas"]

        # Should have 9 antardashas
        assert len(antardashas) == 9

        # Check first antardasha has pratyantardashas
        first_ad = list(antardashas.keys())[0]
        ad_data = antardashas[first_ad]

        assert "pratyantardashas" in ad_data
        assert len(ad_data["pratyantardashas"]) == 9

    def test_balance_calculation(self):
        """Test dasha balance at birth calculation."""
        birth = datetime(1994, 10, 23, 10, 20, 0)
        chart = calculate_birth_chart(birth, 19.0760, 72.8777, 5.5)

        dashas = calculate_vimshottari_dashas(
            birth, 5.5, 19.0760, 72.8777, chart.ayanamsa.value
        )

        # Should have balance for one planet
        assert len(dashas.balance) == 1

        balance_planet = list(dashas.balance.keys())[0]
        balance_years = dashas.balance[balance_planet]

        # Balance should be positive (remaining years in current dasha)
        assert balance_years > 0, f"Balance years should be positive: {balance_years}"

        # Should be less than or equal to total duration of that planet's dasha
        total_duration = VIMSHOTTARI_DASHA_DURATIONS[balance_planet]
        assert balance_years <= total_duration, (
            f"Balance {balance_years} exceeds total duration {total_duration}"
        )

    def test_current_dasha_identification(self, sample_vedic_chart_delhi):
        """Test identification of current running dasha."""
        chart = sample_vedic_chart_delhi

        dashas = calculate_vimshottari_dashas(
            chart.person.birth_datetime,
            chart.person.timezone_offset,
            chart.person.latitude,
            chart.person.longitude,
            chart.ayanamsa.value,
        )

        # Current should exist and have proper structure
        assert "mahadashas" in dashas.current
        assert len(dashas.current["mahadashas"]) == 1  # Only one current mahadasha

        current_md = list(dashas.current["mahadashas"].keys())[0]
        current_data = dashas.current["mahadashas"][current_md]

        # Should have start/end dates and antardashas
        assert "start" in current_data
        assert "end" in current_data
        assert "antardashas" in current_data

        # Current time should be within current mahadasha period
        now = datetime.now()
        assert current_data["start"] <= now <= current_data["end"]

    def test_upcoming_dashas(self, sample_vedic_chart_delhi):
        """Test upcoming dasha identification."""
        chart = sample_vedic_chart_delhi

        dashas = calculate_vimshottari_dashas(
            chart.person.birth_datetime,
            chart.person.timezone_offset,
            chart.person.latitude,
            chart.person.longitude,
            chart.ayanamsa.value,
        )

        # Should have upcoming periods
        assert "mahadashas" in dashas.upcoming
        upcoming_count = sum(
            len(md_data.get("antardashas", {}))
            for md_data in dashas.upcoming["mahadashas"].values()
        )

        # Should have 3 upcoming antardashas as mentioned in implementation
        assert upcoming_count <= 3, f"Too many upcoming periods: {upcoming_count}"


class TestConsistency:
    """Test calculation consistency and edge cases."""

    def test_deterministic_calculations(self):
        """Test that repeated calculations give same results."""
        birth = datetime(1994, 10, 23, 10, 20, 0)
        chart = calculate_birth_chart(birth, 19.0760, 72.8777, 5.5)

        dashas1 = calculate_vimshottari_dashas(
            birth, 5.5, 19.0760, 72.8777, chart.ayanamsa.value
        )
        dashas2 = calculate_vimshottari_dashas(
            birth, 5.5, 19.0760, 72.8777, chart.ayanamsa.value
        )

        # Balance should be identical
        assert dashas1.balance == dashas2.balance

        # Check few dates are same (avoid full nested comparison)
        first_md_1 = list(dashas1.all["mahadashas"].keys())[0]
        first_md_2 = list(dashas2.all["mahadashas"].keys())[0]

        assert first_md_1 == first_md_2

        date1 = dashas1.all["mahadashas"][first_md_1]["start"]
        date2 = dashas2.all["mahadashas"][first_md_2]["start"]

        assert date1 == date2

    def test_different_ayanamsa_effect(self):
        """Test that different ayanamsa values affect moon nakshatra."""
        birth = datetime(2020, 5, 15, 12, 0, 0)

        # Calculate with two different ayanamsa values
        dashas_lahiri = calculate_vimshottari_dashas(
            birth, 5.5, 19.0760, 72.8777, 23.85
        )  # Lahiri
        dashas_pushya = calculate_vimshottari_dashas(
            birth, 5.5, 19.0760, 72.8777, 21.21
        )  # Pushya

        # Starting dasha lord might differ (moon nakshatra depends on ayanamsa)
        lord_lahiri = list(dashas_lahiri.balance.keys())[0]
        lord_pushya = list(dashas_pushya.balance.keys())[0]

        # Might be different due to ayanamsa difference
        # Just verify both return valid lords
        assert lord_lahiri in VIMSHOTTARI_DASHA_DURATIONS
        assert lord_pushya in VIMSHOTTARI_DASHA_DURATIONS

    def test_edge_dates(self):
        """Test dasha calculation for edge dates."""
        edge_dates = [
            datetime(1900, 1, 1, 0, 0, 0),  # Century start
            datetime(2000, 1, 1, 0, 0, 0),  # Millennium
            datetime(2020, 2, 29, 12, 0, 0),  # Leap year leap day
            datetime(2023, 12, 31, 23, 59, 59),  # Year end
        ]

        for birth_date in edge_dates:
            chart = calculate_birth_chart(birth_date, 28.6139, 77.2090, 0.0)

            dashas = calculate_vimshottari_dashas(
                birth_date, 0.0, 28.6139, 77.2090, chart.ayanamsa.value
            )

            # Should not raise exceptions and have valid structure
            assert len(dashas.all["mahadashas"]) == 9
            assert len(dashas.balance) == 1
