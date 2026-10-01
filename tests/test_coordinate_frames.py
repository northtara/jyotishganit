"""Frame consistency and independent numerical regressions.

Reference snapshots use Swiss Ephemeris 2.10.03, Moshier, True Citra, and
Skyfield's TT/UT1 inputs (including the same delta-T for houses). Swiss
Ephemeris is not a runtime or test dependency. Planet tolerances allow for
different ephemerides; the retained linear mean-node model needs a wider one.
"""

import math
from datetime import datetime
from itertools import product

import numpy as np
import pytest
from skyfield import almanac
from skyfield.api import load
from skyfield.framelib import (
    ICRS_to_J2000,
    ecliptic_frame,
    itrs,
)
from skyfield.nutationlib import mean_obliquity

from jyotishganit.core import astronomical
from jyotishganit.core.astronomical import (
    calculate_all_positions,
    calculate_ascendant,
    calculate_mean_node_longitude,
    calculate_solar_ingress,
    calculate_true_obliquity,
    get_ephemeris,
    get_planet_declination,
    get_timescale,
    skyfield_time_from_datetime,
    tropical_to_sidereal,
)
from jyotishganit.core.constants import ZODIAC_SIGNS
from jyotishganit.core.models import Person


@pytest.fixture(scope="module")
def timescale():
    return load.timescale(builtin=True)


# Compare the scalar ascendant formula with a Cartesian construction: the
# intersection of the local horizon plane and the date's ecliptic plane.
# The dot product with local east selects the rising intersection.
ASCENDANT_CASES = list(
    product(
        (1900, 1950, 1980, 1992, 2000, 2010, 2025, 2050),
        (0, 6, 12, 18),
        (-60.0, -33.87, 0.0, 28.6139, 40.7128, 51.5074, 60.0),
    )
)


@pytest.mark.parametrize("year,hour,latitude", ASCENDANT_CASES)
def test_ascendant_matches_eastern_horizon_geometry(timescale, year, hour, latitude):
    t = timescale.utc(year, 5, 14, hour)
    longitude = -74.0060
    phi, lam = np.radians([latitude, longitude])
    terrestrial_to_icrf = itrs.rotation_at(t).T
    zenith = terrestrial_to_icrf @ np.array(
        [np.cos(phi) * np.cos(lam), np.cos(phi) * np.sin(lam), np.sin(phi)]
    )
    east = terrestrial_to_icrf @ np.array([-np.sin(lam), np.cos(lam), 0.0])
    ecliptic_rotation = ecliptic_frame.rotation_at(t)
    intersection = np.cross(zenith, ecliptic_rotation[2])
    if np.dot(intersection, east) < 0:
        intersection = -intersection
    x, y, _ = ecliptic_rotation @ intersection
    expected = math.degrees(math.atan2(y, x)) % 360.0
    actual = calculate_ascendant(t, latitude, longitude, ayanamsa=0.0)
    error = (actual - expected + 180.0) % 360.0 - 180.0
    assert abs(error) < 1e-8


@pytest.mark.parametrize("year", [1900, 1992, 2025, 2050])
def test_true_obliquity_matches_skyfield_frame(timescale, year):
    t = timescale.utc(year, 5, 14)
    # Rotation from the true equator to the ecliptic is a tilt about x.
    tilt = ecliptic_frame.rotation_at(t) @ t.M.T
    expected = math.degrees(math.atan2(tilt[1, 2], tilt[1, 1]))
    assert calculate_true_obliquity(t) == pytest.approx(expected, abs=1e-10)


@pytest.mark.parametrize("year", [1900, 1992, 2025, 2050])
def test_mean_node_matches_mean_to_true_frame_rotation(timescale, year):
    t = timescale.utc(year, 5, 14)
    centuries = (t.tt - 2451545.0) / 36525.0
    node = math.radians((125.04452 - 1934.136261 * centuries) % 360.0)
    epsilon = math.radians(mean_obliquity(t.tdb) / 3600.0)
    # A zero-latitude mean-ecliptic vector expressed in mean-equatorial axes.
    mean_equatorial = np.array(
        [
            math.cos(node),
            math.sin(node) * math.cos(epsilon),
            math.sin(node) * math.sin(epsilon),
        ]
    )
    mean_rotation = t.precession_matrix() @ ICRS_to_J2000
    icrf = mean_rotation.T @ mean_equatorial
    x, y, _ = ecliptic_frame.rotation_at(t) @ icrf
    expected = math.degrees(math.atan2(y, x)) % 360.0
    assert calculate_mean_node_longitude(t) == pytest.approx(expected, abs=1e-9)


@pytest.mark.parametrize(
    "birth,latitude,longitude,offset,delta_t,ayanamsa,ascendant,positions",
    [
        (
            datetime(1900, 1, 1, 12),
            51.5,
            -0.12,
            0.0,
            -1.9738683756666824,
            22.4496899355,
            2.4876517554,
            [
                258.2141202962,
                257.1741282453,
                261.8037389530,
                237.1903248919,
                218.7839860957,
                284.5471102877,
                245.3253263793,
                236.6851368209,
            ],
        ),
        (
            datetime(1992, 5, 14, 8, 20),
            28.6139,
            77.2090,
            5.5,
            58.654300237499875,
            23.7441439096,
            71.2397598197,
            [
                29.8213737725,
                178.0534484241,
                342.5439086391,
                11.2612379057,
                131.1578027997,
                21.5876859474,
                294.5736532980,
                248.9601265519,
            ],
        ),
        (
            datetime(2025, 1, 15, 12),
            -33.87,
            151.2,
            11.0,
            69.13963570833337,
            24.1912496573,
            345.0394356998,
            [
                270.9311092447,
                104.5168392143,
                92.4464070892,
                255.4486121616,
                47.7889800383,
                318.0170229866,
                321.5187101739,
                336.5628389677,
            ],
        ),
    ],
)
def test_birth_positions_against_independent_reference(
    monkeypatch,
    birth,
    latitude,
    longitude,
    offset,
    delta_t,
    ayanamsa,
    ascendant,
    positions,
):
    # Freeze TT-UT1 so updates to Skyfield's Earth-rotation tables do not
    # change the inputs used to generate these independent reference values.
    reference_timescale = load.timescale(builtin=True, delta_t=delta_t)
    monkeypatch.setattr(astronomical, "get_timescale", lambda: reference_timescale)
    person = Person(birth, latitude, longitude, offset)
    actual_ayanamsa, actual_ascendant, planets = calculate_all_positions(person)
    assert actual_ayanamsa.name == "True Chitra Paksha"
    assert actual_ayanamsa.value == pytest.approx(ayanamsa, abs=0.1 / 3600.0)
    assert actual_ascendant == pytest.approx(ascendant, abs=0.1 / 3600.0)
    assert [p.celestial_body for p in planets] == [
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
    for planet, expected in zip(planets[:-1], positions, strict=True):
        actual = ZODIAC_SIGNS.index(planet.sign) * 30 + planet.sign_degrees
        error = (actual - expected + 180.0) % 360.0 - 180.0
        tolerance = 10.0 if planet.celestial_body == "Rahu" else 2.0
        assert abs(error) * 3600.0 < tolerance, planet.celestial_body
    rahu = ZODIAC_SIGNS.index(planets[-2].sign) * 30 + planets[-2].sign_degrees
    ketu = ZODIAC_SIGNS.index(planets[-1].sign) * 30 + planets[-1].sign_degrees
    assert (ketu - rahu) % 360.0 == pytest.approx(180.0, abs=1e-10)


def test_tropical_solar_ingress_matches_equinox_of_date():
    ts = get_timescale()
    events, seasons = almanac.find_discrete(
        ts.utc(2025, 1, 1), ts.utc(2025, 6, 1), almanac.seasons(get_ephemeris())
    )
    expected = events[seasons == 0][0].utc_datetime()
    actual = calculate_solar_ingress(0.0, 2025)
    assert abs((actual - expected).total_seconds()) < 120.0


@pytest.mark.parametrize(
    "birth,offset,declinations",
    [
        (
            datetime(1900, 1, 1, 12),
            0.0,
            [-23.0230133032, -21.3617524367, -23.6116457093],
        ),
        (
            datetime(1992, 5, 14, 8, 20),
            5.5,
            [18.6651885800, -12.9809427623, 1.2679020442],
        ),
        (
            datetime(2025, 1, 15, 12),
            11.0,
            [-21.1084972073, 21.8588472646, 25.0196843185],
        ),
    ],
)
def test_declinations_against_equator_of_date_reference(birth, offset, declinations):
    t = skyfield_time_from_datetime(birth, offset)
    for name, expected in zip(["Sun", "Moon", "Mars"], declinations, strict=True):
        assert get_planet_declination(name, t) == pytest.approx(
            expected, abs=2.0 / 3600.0
        )


@pytest.mark.parametrize(
    "tropical,ayanamsa,expected",
    [(0.0, 24.0, 336.0), (360.0, 0.0, 0.0), (721.0, 24.0, 337.0)],
)
def test_sidereal_longitudes_wrap(tropical, ayanamsa, expected):
    assert tropical_to_sidereal(tropical, ayanamsa) == pytest.approx(expected)
