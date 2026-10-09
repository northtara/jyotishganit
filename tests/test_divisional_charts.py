"""Divisional mapping and chart-assembly regressions; no ephemeris required."""

from copy import deepcopy
from fractions import Fraction
from math import nextafter
from types import SimpleNamespace

import pytest

from jyotishganit.components import divisional_charts as divisional
from jyotishganit.components.divisional_charts import (
    compute_divisional_chart,
    compute_divisional_position_for_type,
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


# Selected classical sign sequences, independent of the production branching.
# PVR, Vedic Astrology: An Integrated Approach, section 6.2, pp. 52-60:
# https://www.vedicastrologer.org/articles/vedic_astro_textbook.pdf
# Each start is a zero-based destination for the first part of each natal sign.
EQUAL_VARGAS = [
    (2, divisional.hora_from_long, (4, 3) * 6, None),
    (3, divisional.drekkana_from_long, tuple(range(12)), 4),
    (4, divisional.chaturtamsa_from_long, tuple(range(12)), 3),
    (7, divisional.saptamsa_from_long, (0, 7, 2, 9, 4, 11, 6, 1, 8, 3, 10, 5), 1),
    (9, divisional.navamsa_from_long, (0, 9, 6, 3) * 3, 1),
    (10, divisional.dasamsa_from_long, (0, 9, 2, 11, 4, 1, 6, 3, 8, 5, 10, 7), 1),
    (12, divisional.dwadasamsa_from_long, tuple(range(12)), 1),
    (16, divisional.shodasamsa_from_long, (0, 4, 8) * 4, 1),
    (20, divisional.vimsamsa_from_long, (0, 8, 4) * 4, 1),
    (24, divisional.chaturvimsamsa_from_long, (4, 3) * 6, 1),
    (27, divisional.sapta_vimsamsa_from_long, (0, 3, 6, 9) * 3, 1),
    (40, divisional.khavedamsa_from_long, (0, 6) * 6, 1),
    (45, divisional.akshavedamsa_from_long, (0, 4, 8) * 4, 1),
    (60, divisional.shashtiamsa_from_long, tuple(range(12)), 1),
]


@pytest.mark.parametrize("sign_index", range(12))
@pytest.mark.parametrize(
    "factor,mapper,starts,stride",
    EQUAL_VARGAS,
    ids=[f"D{row[0]}" for row in EQUAL_VARGAS],
)
def test_equal_varga_exact_input_boundaries(sign_index, factor, mapper, starts, stride):
    boundaries = [Fraction(30 * index, factor) for index in range(1, factor)]
    # Include integer inputs, subnormal zero neighbor, and the last valid float.
    degrees = list(range(30)) + [nextafter(0.0, 30.0), nextafter(30.0, 0.0)]
    degrees += [
        float(Fraction(30, factor) * (part + fraction))
        for part in range(factor)
        for fraction in (Fraction(1, 4), Fraction(1, 2), Fraction(3, 4))
    ]
    for boundary in boundaries:
        edge = float(boundary)
        degrees.extend((nextafter(edge, 0.0), edge, nextafter(edge, 30.0)))
    sign = ZODIAC_SIGNS[sign_index]
    for degree in degrees:
        exact = Fraction(degree)
        # Count crossed rational thresholds instead of duplicating integer division.
        part = sum(exact >= boundary for boundary in boundaries)
        target = (
            (starts[sign_index] + stride * part) % 12
            if stride
            else (starts[sign_index] if part == 0 else 7 - starts[sign_index])
        )
        expected_sign = ZODIAC_SIGNS[target]
        expected_remainder = float(exact - Fraction(30 * part, factor))
        seconds, actual_sign, remainder = mapper(sign, degree)
        context = (factor, sign, degree)
        assert actual_sign == expected_sign, context
        assert remainder == expected_remainder, context
        assert seconds == int(sign_index * 30 * 3600 + degree * 3600), context
        assert (
            compute_divisional_position_for_type(sign, degree, f"D{factor}")
            == expected_sign
        ), context

        d1 = SimpleNamespace(
            houses=[SimpleNamespace(sign=sign, sign_degrees=degree)],
            planets=[
                SimpleNamespace(
                    celestial_body="Sun", sign=sign, sign_degrees=degree, house=7
                )
            ],
        )
        original = deepcopy(d1)
        chart = compute_divisional_chart(d1, f"D{factor}")
        assert chart.ascendant.sign == expected_sign, context
        assert chart.houses[0].sign == expected_sign, context
        assert chart.houses[0].occupants[0].sign == expected_sign, context
        assert chart.houses[0].occupants[0].d1_house_placement == 7, context
        assert d1 == original, context


@pytest.mark.parametrize(
    "degree,expected",
    [
        (70 / 3, "Libra"),
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
