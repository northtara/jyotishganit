"""D30 interval and chart-assembly regressions; no ephemeris required."""

from math import nextafter
from types import SimpleNamespace

import pytest

from jyotishganit.components.divisional_charts import (
    compute_divisional_chart,
    compute_divisional_position_for_type,
    trimsamsa_from_long,
)
from jyotishganit.core.constants import ZODIAC_SIGNS

# PVR, Vedic Astrology: An Integrated Approach, section 6.2.17, pp. 58-59.
ODD = [
    (5, "Aries"),
    (10, "Aquarius"),
    (18, "Sagittarius"),
    (25, "Gemini"),
    (30, "Libra"),
]
EVEN = [
    (5, "Taurus"),
    (12, "Virgo"),
    (20, "Pisces"),
    (25, "Capricorn"),
    (30, "Scorpio"),
]


@pytest.mark.parametrize("sign_index", range(12))
def test_d30_interval_interiors(sign_index):
    sign = ZODIAC_SIGNS[sign_index]
    intervals = ODD if sign_index % 2 == 0 else EVEN
    start = 0
    for end, expected in intervals:
        for fraction in (0.25, 0.5, 0.75):
            degree = start + (end - start) * fraction
            assert trimsamsa_from_long(sign, degree)[1] == expected
            assert compute_divisional_position_for_type(sign, degree, "D30") == expected
        start = end


@pytest.mark.parametrize("sign_index", range(12))
def test_d30_boundaries(sign_index):
    sign = ZODIAC_SIGNS[sign_index]
    intervals = ODD if sign_index % 2 == 0 else EVEN
    assert trimsamsa_from_long(sign, 0)[1] == intervals[0][1]
    assert trimsamsa_from_long(sign, nextafter(30.0, 0.0))[1] == intervals[-1][1]
    for index, (boundary, expected) in enumerate(intervals[:-1]):
        # Preserve upper-inclusive endpoints; adjacent floats stay on their side.
        assert trimsamsa_from_long(sign, nextafter(boundary, 0.0))[1] == expected
        assert trimsamsa_from_long(sign, boundary)[1] == expected
        assert (
            trimsamsa_from_long(sign, nextafter(boundary, 30.0))[1]
            == intervals[index + 1][1]
        )


@pytest.mark.parametrize(
    "degree,expected", [(15, "Pisces"), (22, "Capricorn"), (24.5, "Capricorn")]
)
def test_d30_even_sign_regressions(degree, expected):
    d1 = SimpleNamespace(
        houses=[SimpleNamespace(sign="Taurus", sign_degrees=degree)],
        planets=[
            SimpleNamespace(
                celestial_body="Sun", sign="Taurus", sign_degrees=degree, house=1
            )
        ],
    )
    chart = compute_divisional_chart(d1, "D30")
    assert chart.ascendant.sign == expected
    assert len(chart.houses) == 12
    assert chart.houses[0].sign == expected
    assert chart.houses[0].occupants[0].sign == expected
