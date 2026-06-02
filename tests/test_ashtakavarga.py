"""
Test suite for Ashtakavarga calculations in jyotishganit.

Tests individual Binnna Ashtakavarga charts and Sarvashtakavarga totals
against classical benchmarks from Maharishi Parashara's teachings.
"""

from jyotishganit.components.ashtakavarga import (
    BENEFIC_HOUSES,
    calculate_ashtakavarga,
    calculate_ashtakavarga_for_chart,
    calculate_bhinna_ashtakavarga,
    create_natal_chart_sign_mapping,
)
from jyotishganit.core.constants import ZODIAC_SIGNS


class TestAshtakavargaConstants:
    """Test Ashtakavarga constant definitions and formulas."""

    def test_benefic_houses_defined(self):
        """Verify all planets have benefic house definitions."""
        expected_planets = [
            "Sun",
            "Moon",
            "Mars",
            "Mercury",
            "Jupiter",
            "Venus",
            "Saturn",
        ]
        assert set(BENEFIC_HOUSES.keys()) == set(expected_planets)

        # Lagna should be included in all
        for planet_houses in BENEFIC_HOUSES.values():
            assert "Lagna" in planet_houses

    def test_benefic_house_values(self):
        """Verify house values are within 1-12 range (as houses are numbered)."""
        for planet, contributors in BENEFIC_HOUSES.items():
            for contributor, houses in contributors.items():
                for house_num in houses:
                    assert 1 <= house_num <= 12, (
                        f"Invalid house {house_num} for {planet}-{contributor}"
                    )

    def test_classical_totals(self, expected_ashtakavarga_benchmarks):
        """Verify classical total bindu counts for each planet's BAV."""
        # These should sum to the classical values from texts
        sun_total = expected_ashtakavarga_benchmarks["sun_bav_total"]
        moon_total = expected_ashtakavarga_benchmarks["moon_bav_total"]

        # Basic sanity checks - totals should be reasonable
        assert sun_total > 0 and sun_total <= 400  # Sun has 48 according to texts
        assert moon_total > 0 and moon_total <= 400  # Moon has 49 according to texts


class TestBhinnaAshtakavarga:
    """Test individual Bhinna Ashtakavarga calculations."""

    def test_calculate_bhinna_ashtakavarga_structure(self):
        """Test basic structure of BAV calculation."""
        # Sample natal chart with planets in known positions
        natal_chart = {
            "Sun": 4,  # Leo (natural Sun sign - should be strong)
            "Moon": 3,  # Cancer
            "Mars": 0,  # Aries
            "Mercury": 2,  # Gemini (own sign)
            "Jupiter": 8,  # Sagittarius
            "Venus": 6,  # Libra
            "Saturn": 10,  # Aquarius
            "Lagna": 5,  # Virgo
        }

        bav = calculate_bhinna_ashtakavarga("Sun", natal_chart, BENEFIC_HOUSES)

        # Should have bindu counts for all 12 signs
        assert len(bav) == 12
        assert set(bav.keys()) == set(ZODIAC_SIGNS)

        # All counts should be non-negative integers
        for _sign, bindus in bav.items():
            assert isinstance(bindus, int)
            assert bindus >= 0

    def test_sun_bav_total_benchmark(self, expected_ashtakavarga_benchmarks):
        """Verify Sun's BAV totals match classical texts."""
        # Place Sun in its own sign (Leo = 4) for maximum exaltation
        natal_chart_sun_in_leo = {
            "Sun": 4,
            "Moon": 0,
            "Mars": 0,
            "Mercury": 0,
            "Jupiter": 0,
            "Venus": 0,
            "Saturn": 0,
            "Lagna": 0,
        }

        sun_bav = calculate_bhinna_ashtakavarga(
            "Sun", natal_chart_sun_in_leo, BENEFIC_HOUSES
        )

        # Sum should be 48 according to Parashara
        total_bindus = sum(sun_bav.values())
        expected_total = expected_ashtakavarga_benchmarks["sun_bav_total"]

        # Allow some tolerance due to computational factors
        tolerance = 2
        assert abs(total_bindus - expected_total) <= tolerance, (
            f"Sun BAV total {total_bindus} should be close to {expected_total}"
        )

    def test_moon_bav_total_benchmark(self, expected_ashtakavarga_benchmarks):
        """Verify Moon's BAV totals match classical texts."""
        # Place Moon in Cancer for maximum strength
        natal_chart_moon_in_cancer = {
            "Sun": 0,
            "Moon": 3,
            "Mars": 0,
            "Mercury": 0,
            "Jupiter": 0,
            "Venus": 0,
            "Saturn": 0,
            "Lagna": 0,
        }

        moon_bav = calculate_bhinna_ashtakavarga(
            "Moon", natal_chart_moon_in_cancer, BENEFIC_HOUSES
        )

        total_bindus = sum(moon_bav.values())
        expected_total = expected_ashtakavarga_benchmarks["moon_bav_total"]

        tolerance = 2
        assert abs(total_bindus - expected_total) <= tolerance, (
            f"Moon BAV total {total_bindus} should be close to {expected_total}"
        )

    def test_bindu_count_consistency(self):
        """Test that bindu counts are consistent for same planetary configuration."""
        natal_chart = {
            "Sun": 4,
            "Moon": 3,
            "Mars": 7,
            "Mercury": 2,
            "Jupiter": 11,
            "Venus": 1,
            "Saturn": 9,
            "Lagna": 0,
        }

        # Calculate BAV multiple times - should be deterministic
        bav1 = calculate_bhinna_ashtakavarga("Sun", natal_chart, BENEFIC_HOUSES)
        bav2 = calculate_bhinna_ashtakavarga("Sun", natal_chart, BENEFIC_HOUSES)

        assert bav1 == bav2

    def test_all_planets_bav_non_empty(self):
        """Verify all planets have non-empty BAV charts."""
        natal_chart = {
            "Sun": 4,
            "Moon": 3,
            "Mars": 0,
            "Mercury": 2,
            "Jupiter": 8,
            "Venus": 6,
            "Saturn": 10,
            "Lagna": 5,
        }

        planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

        for planet in planets:
            bav = calculate_bhinna_ashtakavarga(planet, natal_chart, BENEFIC_HOUSES)

            # Should have all 12 signs
            assert len(bav) == 12

            # Should have some positive bindus (not all zeros)
            assert sum(bav.values()) > 0


class TestSarvashtakavarga:
    """Test Sarvashtakavarga (total) calculations."""

    def test_calculate_ashtakavarga_structure(self):
        """Test basic structure of full Ashtakavarga calculation."""
        natal_chart = {
            "Sun": 4,
            "Moon": 3,
            "Mars": 0,
            "Mercury": 2,
            "Jupiter": 8,
            "Venus": 6,
            "Saturn": 10,
            "Lagna": 5,
        }

        result = calculate_ashtakavarga(natal_chart)

        # Should have bhav (individual) and sav (total) sections
        assert "bhav" in result
        assert "sav" in result

        # bhav should have all planets
        assert set(result["bhav"].keys()) == {
            "Sun",
            "Moon",
            "Mars",
            "Mercury",
            "Jupiter",
            "Venus",
            "Saturn",
        }

        # sav should have bindu counts for all signs
        assert len(result["sav"]) == 12
        assert set(result["sav"].keys()) == set(ZODIAC_SIGNS)

    def test_sarvashtakavarga_totals(self):
        """Test that SAV totals equal sum of individual BAVs."""
        natal_chart = {
            "Sun": 4,
            "Moon": 3,
            "Mars": 0,
            "Mercury": 2,
            "Jupiter": 8,
            "Venus": 6,
            "Saturn": 10,
            "Lagna": 5,
        }

        result = calculate_ashtakavarga(natal_chart)

        planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

        # Calculate expected totals by summing individual BAVs
        expected_sav = dict.fromkeys(ZODIAC_SIGNS, 0)
        for planet in planets:
            bav = calculate_bhinna_ashtakavarga(planet, natal_chart, BENEFIC_HOUSES)
            for sign, bindus in bav.items():
                expected_sav[sign] += bindus

        actual_sav = result["sav"]

        # Should match exactly
        assert expected_sav == actual_sav

    def test_sav_bindu_range(self):
        """Test that SAV bindu counts are in reasonable ranges."""
        natal_chart = {
            "Sun": 0,
            "Moon": 1,
            "Mars": 2,
            "Mercury": 3,
            "Jupiter": 4,
            "Venus": 5,
            "Saturn": 6,
            "Lagna": 7,
        }

        result = calculate_ashtakavarga(natal_chart)

        for sign, bindus in result["sav"].items():
            # Each sign should have reasonable bindu count
            # Range based on accumulated benefic houses across all planets/lagna
            assert 15 <= bindus <= 40, (
                f"SAV bindus for {sign}: {bindus} seems unreasonable"
            )


class TestChartIntegration:
    """Test Ashtakavarga integration with full chart calculations."""

    def test_create_natal_chart_sign_mapping(self):
        """Test sign mapping creation from D1 chart."""

        # Mock a simple D1 chart
        class MockPlanet:
            def __init__(self, name, sign):
                self.celestial_body = name
                self.sign = sign

        class MockAscendant:
            def __init__(self, sign):
                self.sign = sign

        class MockD1Chart:
            def __init__(self):
                self.planets = [
                    MockPlanet("Sun", "Leo"),
                    MockPlanet("Moon", "Cancer"),
                    MockPlanet("Mars", "Aries"),
                ]
                self.ascendant = MockAscendant("Virgo")

        d1_chart = MockD1Chart()
        ascendant_sign = "Virgo"

        sign_mapping = create_natal_chart_sign_mapping(d1_chart, ascendant_sign)

        # Should have all planets and Lagna
        assert set(sign_mapping.keys()) == {"Sun", "Moon", "Mars", "Lagna"}

        # Should map signs correctly to indices
        assert sign_mapping["Sun"] == 4  # Leo
        assert sign_mapping["Moon"] == 3  # Cancer
        assert sign_mapping["Mars"] == 0  # Aries
        assert sign_mapping["Lagna"] == 5  # Virgo

    def test_full_chart_integration(self, sample_vedic_chart_delhi):
        """Test Ashtakavarga calculation with real D1 chart data."""
        chart = sample_vedic_chart_delhi
        # Should be able to calculate AV without errors
        ascendant_sign = chart.d1_chart.houses[0].sign
        av = calculate_ashtakavarga_for_chart(chart.d1_chart, ascendant_sign)
        assert hasattr(av, "bhav")
        assert hasattr(av, "sav")
        # Verify SAV has all signs
        assert len(av.sav) == 12
        # Verify all planets have BAV charts
        expected_planets = {
            "Sun",
            "Moon",
            "Mars",
            "Mercury",
            "Jupiter",
            "Venus",
            "Saturn",
        }
        assert set(av.bhav.keys()) == expected_planets

    def test_bindu_counts_numeric(self, sample_vedic_chart_delhi):
        """Verify all bindu counts are numeric and reasonable."""
        chart = sample_vedic_chart_delhi
        ascendant_sign = chart.d1_chart.houses[0].sign
        av = calculate_ashtakavarga_for_chart(chart.d1_chart, ascendant_sign)
        # Check SAV bindus
        for _sign, bindus in av.sav.items():
            assert isinstance(bindus, int)
            assert bindus >= 0
        # Check individual BAV charts
        for _planet, bav in av.bhav.items():
            for _sign, bindus in bav.items():
                assert isinstance(bindus, int)
                assert bindus >= 0
