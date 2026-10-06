"""Cheshta Bala regressions (issue #16)."""

import contextlib
import io
from datetime import datetime, timedelta
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from jyotishganit.components.strengths import _mean_longitude, compute_chestagbala
from jyotishganit.main import calculate_birth_chart

CHESHTA_PLANETS = ("Mars", "Mercury", "Jupiter", "Venus", "Saturn")


def _cheshtabala(birth, lat, lon, tz):
    with contextlib.redirect_stdout(io.StringIO()):
        chart = calculate_birth_chart(birth, lat, lon, tz)
    return {
        p.celestial_body: p.shadbala["Cheshtabala"]
        for p in chart.d1_chart.planets
        if p.celestial_body in CHESHTA_PLANETS
    }


def test_mean_longitude_at_j2000():
    assert _mean_longitude("Venus", 0.0, 0.0) == pytest.approx(181.979801)
    assert _mean_longitude("Venus", 0.0, 24.0) == pytest.approx(157.979801)
    # Mean Sun = Earth + 180°, Meeus eq. 25.2
    assert (_mean_longitude("Earth", 0.0, 0.0) + 180) % 360 == pytest.approx(280.466457)


@patch("jyotishganit.components.strengths._mean_longitude")
@patch("jyotishganit.components.strengths.calculate_ayanamsa", return_value=0.0)
def test_mean_and_true_longitude_average_across_aries(_, mock_mean_long):
    # Mean Sun 30° (Earth 210°), Mars mean 350°, Mars true 10°: the midpoint
    # is 0°, not 180°, so the kendra is 30° and the bala 10.
    mock_mean_long.side_effect = lambda body, T, ayanamsa: {
        "Earth": 210.0,
        "Mars": 350.0,
    }[body]
    mars = SimpleNamespace(
        celestial_body="Mars", sign="Aries", sign_degrees=10.0, shadbala={}
    )
    person = SimpleNamespace(birth_datetime=datetime(2000, 1, 1), timezone_offset=0)
    compute_chestagbala(SimpleNamespace(planets=[mars]), person)
    assert mars.shadbala["Cheshtabala"] == pytest.approx(10.0)


def test_cheshtabala_stable_over_minutes():
    # Issue #16: Venus swung between 2 and 59 virupas within ten minutes.
    start = datetime(2000, 1, 1, 0, 0)
    values = [
        _cheshtabala(start + timedelta(minutes=m), 28.6139, 77.2090, 0.0)
        for m in (0, 5, 10)
    ]
    for planet in CHESHTA_PLANETS:
        assert max(v[planet] for v in values) - min(v[planet] for v in values) < 0.02, (
            planet
        )


# Published worked examples. Modern mean elements differ from the books'
# 1900-epoch constants, most for Mercury's Seeghrochcha (~13°).
REFERENCE_CHARTS = [
    pytest.param(
        # B.V. Raman, Graha and Bhava Balas, Standard Horoscope
        datetime(1918, 10, 16, 14, 6, 16),
        13.0,
        77 + 35 / 60,
        5 + 10 / 60 + 20 / 3600,
        {
            "Mars": 22.23,
            "Mercury": 2.30,
            "Jupiter": 35.26,
            "Venus": 5.95,
            "Saturn": 21.14,
        },
        id="raman-standard-1918",
    ),
    pytest.param(
        # V.P. Jain example, as used in PyJHora's Shadbala tests
        datetime(1981, 9, 13, 1, 30),
        28 + 39 / 60,
        77 + 13 / 60,
        5.5,
        {
            "Mars": 20.93,
            "Mercury": 28.76,
            "Jupiter": 8.43,
            "Venus": 28.18,
            "Saturn": 5.05,
        },
        id="vp-jain-1981",
    ),
]


@pytest.mark.parametrize("birth,lat,lon,tz,expected", REFERENCE_CHARTS)
def test_cheshtabala_matches_published_examples(birth, lat, lon, tz, expected):
    actual = _cheshtabala(birth, lat, lon, tz)
    for planet, value in expected.items():
        tolerance = 5.0 if planet == "Mercury" else 1.5
        assert actual[planet] == pytest.approx(value, abs=tolerance), planet
