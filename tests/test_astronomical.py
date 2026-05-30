import pytest

from jyotishganit.core.astronomical import calculate_obliquity


class FakeTime:
    def __init__(self, tt):
        self.tt = tt


def test_calculate_obliquity_at_j2000():
    t = FakeTime(tt=2451545.0)

    assert calculate_obliquity(t) == pytest.approx(84381.448 / 3600.0)


def test_calculate_obliquity_one_julian_century_after_j2000():
    t = FakeTime(tt=2451545.0 + 36525.0)
    expected_arcsec = 84381.448 - 46.8150 - 0.00059 + 0.001813

    assert calculate_obliquity(t) == pytest.approx(expected_arcsec / 3600.0)
