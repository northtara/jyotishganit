"""Divisional mapping and chart-assembly regressions; no ephemeris required."""

from fractions import Fraction
from math import nextafter
from types import SimpleNamespace

import pytest

from jyotishganit.components.divisional_charts import (
    compute_divisional_chart,
    compute_divisional_position_for_type,
    navamsa_from_long,
    trimsamsa_from_long,
)
from jyotishganit.core.constants import DIVISIONAL_CHARTS, SIGN_LORDS, ZODIAC_SIGNS

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
def test_d9_exact_input_boundaries(sign_index):
    # Movable/fixed/dual starts, expressed by the independent element sequence.
    start = (0, 9, 6, 3)[sign_index % 4]
    boundaries = [Fraction(10 * index, 3) for index in range(1, 9)]
    degrees = [0.0, nextafter(0.0, 30.0), nextafter(30.0, 0.0)]
    degrees += [float(Fraction(10 * index + 5, 3)) for index in range(9)]
    for boundary in boundaries:
        edge = float(boundary)
        degrees.extend((nextafter(edge, 0.0), edge, nextafter(edge, 30.0)))
    for degree in degrees:
        exact = Fraction(degree)
        part = sum(exact >= boundary for boundary in boundaries)
        expected_sign = ZODIAC_SIGNS[(start + part) % 12]
        expected_remainder = float(exact - Fraction(10 * part, 3))
        _, actual_sign, remainder = navamsa_from_long(ZODIAC_SIGNS[sign_index], degree)
        assert actual_sign == expected_sign
        assert remainder == expected_remainder
        assert (
            compute_divisional_position_for_type(ZODIAC_SIGNS[sign_index], degree, "D9")
            == expected_sign
        )


@pytest.mark.parametrize(
    "degree,expected",
    [
        (23.333333333333332, "Libra"),
        (nextafter(23.333333333333332, 30.0), "Scorpio"),
        (10, "Cancer"),
        (20, "Libra"),
    ],
)
def test_d9_boundary_chart_assembly(degree, expected):
    from copy import deepcopy

    d1 = SimpleNamespace(
        houses=[SimpleNamespace(sign="Aries", sign_degrees=degree)],
        planets=[
            SimpleNamespace(
                celestial_body="Sun", sign="Aries", sign_degrees=degree, house=1
            )
        ],
    )
    original = deepcopy(d1)
    chart = compute_divisional_chart(d1, "D9")
    assert chart.ascendant.sign == expected
    assert chart.houses[0].sign == expected
    assert chart.houses[0].occupants[0].sign == expected
    assert d1 == original


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


@pytest.mark.parametrize("sign_index", range(12))
@pytest.mark.parametrize(
    "degree", [0.0, nextafter(15.0, 0.0), 15.0, nextafter(30.0, 0.0)]
)
def test_d2_house_numbers_follow_divisional_ascendant(sign_index, degree):
    from copy import deepcopy

    sign = ZODIAC_SIGNS[sign_index]
    # Sun/Moon Hora: the first half of an odd sign is Leo; reverse for even signs.
    expected_ascendant = "Leo" if (sign_index % 2 == 0) == (degree < 15) else "Cancer"
    expected_numbers = (
        {"Cancer": 1, "Leo": 2}
        if expected_ascendant == "Cancer"
        else {"Cancer": 12, "Leo": 1}
    )
    d1 = SimpleNamespace(
        houses=[SimpleNamespace(sign=sign, sign_degrees=degree)],
        planets=[
            SimpleNamespace(
                celestial_body="Sun", sign="Aries", sign_degrees=0.0, house=3
            ),
            SimpleNamespace(
                celestial_body="Moon", sign="Aries", sign_degrees=15.0, house=7
            ),
            SimpleNamespace(
                celestial_body="Mars", sign="Taurus", sign_degrees=0.0, house=9
            ),
            SimpleNamespace(
                celestial_body="Venus", sign="Taurus", sign_degrees=15.0, house=11
            ),
        ],
    )
    before = deepcopy(d1)
    chart = compute_divisional_chart(d1, "D2")
    assert chart.ascendant.sign == expected_ascendant
    asc_index = ZODIAC_SIGNS.index(expected_ascendant)
    expected_signs = ZODIAC_SIGNS[asc_index:] + ZODIAC_SIGNS[:asc_index]
    expected_houses = list(enumerate(expected_signs, start=1))
    assert [(h.number, h.sign) for h in chart.houses] == expected_houses
    assert {
        h.sign: h.number for h in chart.houses if h.sign in expected_numbers
    } == expected_numbers
    assert next(h.sign for h in chart.houses if h.number == 1) == chart.ascendant.sign
    assert [(h.sign, h.lord) for h in chart.houses] == [
        (sign, SIGN_LORDS[sign]) for sign in expected_signs
    ]
    assert [h.d1_house_placement for h in chart.houses] == [
        (ZODIAC_SIGNS.index(sign) - sign_index) % 12 + 1 for sign in expected_signs
    ]
    assert chart.ascendant.d1_house_placement == (
        (ZODIAC_SIGNS.index(expected_ascendant) - sign_index) % 12 + 1
    )
    assert {
        h.sign: [(p.celestial_body, p.sign, p.d1_house_placement) for p in h.occupants]
        for h in chart.houses
        if h.occupants
    } == {
        "Cancer": [("Moon", "Cancer", 7), ("Mars", "Cancer", 9)],
        "Leo": [("Sun", "Leo", 3), ("Venus", "Leo", 11)],
    }
    assert all(not h.occupants for h in chart.houses if h.sign not in expected_numbers)
    assert [
        (h["number"], h["sign"]) for h in chart.to_dict()["houses"]
    ] == expected_houses
    assert d1 == before


@pytest.mark.parametrize(
    "chart_type", [code for code in DIVISIONAL_CHARTS if code != "D1"]
)
def test_divisional_charts_share_complete_ordered_house_structure(chart_type):
    bodies = (
        "Sun",
        "Moon",
        "Mars",
        "Mercury",
        "Jupiter",
        "Venus",
        "Saturn",
        "Rahu",
        "Ketu",
    )
    d1 = SimpleNamespace(
        houses=[SimpleNamespace(sign="Aries", sign_degrees=20.0)],
        planets=[
            SimpleNamespace(
                celestial_body=body, sign="Aries", sign_degrees=2.0 + index * 3, house=1
            )
            for index, body in enumerate(bodies)
        ],
    )
    chart = compute_divisional_chart(d1, chart_type)
    assert [house.number for house in chart.houses] == list(range(1, 13))
    assert chart.houses[0].sign == chart.ascendant.sign
    assert {house.sign for house in chart.houses} == set(ZODIAC_SIGNS)
    occupants = [planet for house in chart.houses for planet in house.occupants]
    assert sorted(planet.celestial_body for planet in occupants) == sorted(bodies)
    assert all(
        planet.sign == house.sign
        for house in chart.houses
        for planet in house.occupants
    )
    # Empty houses must not share mutable occupant lists.
    assert len({id(house.occupants) for house in chart.houses}) == 12
