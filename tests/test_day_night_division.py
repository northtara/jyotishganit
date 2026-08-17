"""The day/night division: polar latitudes, and the UTC day rollover.

Three of Kaalabala's five sub-balas need to know whether a birth is by day or by
night, how long that day or night was, and when it began. Three things got the
wrong answer:

1. Inside the polar circles the Sun does not rise in local winter and does not
   set in local summer, so `get_sunrise_sunset` returned `None` and the caller
   raised `TypeError`, losing the whole chart.
2. A sunset that falls on the next UTC day came back as a negative local hour, so
   a noon birth in New York was classified as a night birth and its day came out
   -8.99 hours long.
3. Natonnata bala ran off its 0-60 scale whenever the birth was more than six
   hours from noon or midnight — a pre-dawn winter birth at any latitude.
"""

from datetime import datetime, timedelta

import pytest

from jyotishganit.core.astronomical import (
    get_sunrise_sunset,
    is_birth_daytime,
    sun_altitude_degrees,
)
from jyotishganit.core.models import Person
from jyotishganit.main import calculate_birth_chart


def _person(when, lat, lon, offset):
    return Person(
        birth_datetime=when, latitude=lat, longitude=lon, timezone_offset=offset
    )


# New York, 4 July 1990, local noon: the Sun 68 degrees up.
NEW_YORK_NOON = _person(datetime(1990, 7, 4, 12, 0), 40.7128, -74.0060, -4.0)
# Tromso, inside the Arctic circle, in each solstice season.
TROMSO_POLAR_NIGHT = _person(datetime(1988, 12, 21, 11, 0), 69.6492, 18.9553, 1.0)
TROMSO_MIDNIGHT_SUN = _person(datetime(1988, 6, 21, 11, 0), 69.6492, 18.9553, 2.0)
# The first day of Tromso's midnight-sun season has one real sunrise but no
# sunset within the local civil day.
TROMSO_SUNRISE_ONLY = _person(datetime(1988, 5, 16, 12, 0), 69.6492, 18.9553, 2.0)
TROMSO_BEFORE_LAST_SUNRISE = _person(
    datetime(1988, 5, 16, 0, 30), 69.6492, 18.9553, 2.0
)
# An ordinary mid-latitude case, unaffected by any of the corrections.
DELHI = _person(datetime(1995, 8, 20, 14, 45), 28.6139, 77.2090, 5.5)
# Also ordinary, and also mid-latitude: a winter birth before sunrise is more
# than six hours from midnight, which is what takes Natonnata off its scale.
DELHI_PRE_DAWN = _person(datetime(1995, 1, 20, 6, 30), 28.6139, 77.2090, 5.5)


def test_sunset_after_midnight_utc_stays_in_the_evening():
    """The local hour must wrap in both directions, not only above 24."""
    sunrise, sunset = get_sunrise_sunset(NEW_YORK_NOON)

    assert sunrise == pytest.approx(5.50, abs=0.05)
    assert sunset == pytest.approx(20.51, abs=0.05)
    assert sunset - sunrise == pytest.approx(15.0, abs=0.1)


def test_a_noon_birth_in_new_york_is_a_day_birth():
    assert sun_altitude_degrees(NEW_YORK_NOON) == pytest.approx(68.1, abs=0.5)
    assert is_birth_daytime(NEW_YORK_NOON) is True


def test_polar_night_collapses_sunrise_and_sunset_onto_solar_noon():
    """The limit of the ordinary definition as the day length goes to zero."""
    sunrise, sunset = get_sunrise_sunset(TROMSO_POLAR_NIGHT)

    assert sunrise == sunset
    assert sunrise == pytest.approx(11.71, abs=0.1)
    assert is_birth_daytime(TROMSO_POLAR_NIGHT) is False
    assert sun_altitude_degrees(TROMSO_POLAR_NIGHT) < 0


def test_midnight_sun_collapses_them_onto_lower_culmination():
    """The limit as the day length goes to twenty-four hours."""
    sunrise, sunset = get_sunrise_sunset(TROMSO_MIDNIGHT_SUN)

    assert sunrise == sunset
    assert sunrise == pytest.approx(0.76, abs=0.2)
    assert is_birth_daytime(TROMSO_MIDNIGHT_SUN) is True
    assert sun_altitude_degrees(TROMSO_MIDNIGHT_SUN) > 0


def test_a_single_polar_transition_event_is_preserved():
    """A one-event date is not the same as a fully polar date."""
    at_midnight = _person(datetime(1988, 5, 16, 0, 0), 69.6492, 18.9553, 2.0)
    at_noon = TROMSO_SUNRISE_ONLY

    midnight_events = get_sunrise_sunset(at_midnight)
    noon_events = get_sunrise_sunset(at_noon)

    assert midnight_events == noon_events
    assert midnight_events[0] == pytest.approx(1.49, abs=0.05)
    assert midnight_events[1] == 24.0


def test_daytime_uses_the_same_horizon_as_sunrise_and_sunset():
    """The solar disc is visible before its centre reaches zero altitude."""
    sunrise, sunset = get_sunrise_sunset(DELHI)
    after_sunrise = _person(
        datetime(1995, 8, 20) + timedelta(hours=sunrise, minutes=1),
        28.6139,
        77.2090,
        5.5,
    )
    before_sunset = _person(
        datetime(1995, 8, 20) + timedelta(hours=sunset, minutes=-1),
        28.6139,
        77.2090,
        5.5,
    )

    assert sun_altitude_degrees(after_sunrise) < 0.0
    assert sun_altitude_degrees(before_sunset) < 0.0
    assert is_birth_daytime(after_sunrise) is True
    assert is_birth_daytime(before_sunset) is True


@pytest.mark.parametrize(
    ("label", "person"),
    [
        ("polar night", TROMSO_POLAR_NIGHT),
        ("midnight sun", TROMSO_MIDNIGHT_SUN),
        ("before last sunrise", TROMSO_BEFORE_LAST_SUNRISE),
        ("after last sunrise", TROMSO_SUNRISE_ONLY),
    ],
)
def test_a_polar_birth_produces_a_chart(label, person):
    """This used to raise TypeError and take the whole chart with it."""
    chart = calculate_birth_chart(
        person.birth_datetime,
        person.latitude,
        person.longitude,
        timezone_offset=person.timezone_offset,
    )

    assert len(chart.d1_chart.houses) == 12
    for planet in chart.d1_chart.planets:
        if planet.celestial_body in {"Rahu", "Ketu"}:
            continue
        assert planet.shadbala["Kaalabala"]["Total"] is not None


@pytest.mark.parametrize(
    "person",
    [NEW_YORK_NOON, TROMSO_POLAR_NIGHT, TROMSO_MIDNIGHT_SUN, DELHI, DELHI_PRE_DAWN],
    ids=["new-york", "polar-night", "midnight-sun", "delhi", "delhi-pre-dawn"],
)
def test_natonnata_bala_stays_on_its_scale(person):
    """Natonnata runs 0 to 60 shashtiamsas.

    Two ways it used to overshoot: a misclassified day/night sends a noon birth
    down the night branch, which returns 120; and a birth more than six hours
    from the midpoint overshoots on its own, which needs no polar latitude and no
    misclassification — an ordinary Delhi winter birth at 06:30 scored 65.
    """
    chart = calculate_birth_chart(
        person.birth_datetime,
        person.latitude,
        person.longitude,
        timezone_offset=person.timezone_offset,
    )

    for planet in chart.d1_chart.planets:
        natonnata = (planet.shadbala or {}).get("Kaalabala", {}).get("Natonnatabala")
        if natonnata is None:
            continue
        assert 0.0 <= float(natonnata) <= 60.0, f"{planet.celestial_body}: {natonnata}"


@pytest.mark.parametrize("hour", [0, 3, 6, 9, 12, 15, 18, 21])
def test_day_state_and_the_sunrise_window_agree_where_both_are_defined(hour):
    """The direct day-state predicate agrees with the event window."""
    person = _person(datetime(1995, 8, 20, hour, 0), 28.6139, 77.2090, 5.5)
    sunrise, sunset = get_sunrise_sunset(person)

    assert sunrise < sunset
    assert is_birth_daytime(person) is (sunrise <= hour < sunset)
