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


def test_spica_catalogue_loads_into_data_directory(monkeypatch, tmp_path):
    # The Hipparcos catalogue must go through the library's loader (DATA_DIR),
    # not Skyfield's default loader, which saves into the working directory.
    from io import BytesIO
    from unittest.mock import MagicMock

    import pandas as pd
    from skyfield.data import hipparcos

    from jyotishganit.components import panchanga
    from jyotishganit.core import astronomical

    fake_loader = MagicMock()
    fake_loader.open.return_value = BytesIO(b"")
    spica_row = pd.DataFrame(
        {
            "ra_hours": [201.298 / 15],
            "dec_degrees": [-11.161],
            "ra_mas_per_year": [-42.5],
            "dec_mas_per_year": [-31.73],
            "parallax_mas": [12.44],
            "epoch_year": [1991.25],
        },
        index=pd.Index([65474], name="hip"),
    )
    monkeypatch.setattr(astronomical, "loader", fake_loader)
    monkeypatch.setattr(hipparcos, "load_dataframe", lambda f: spica_row)
    monkeypatch.chdir(tmp_path)
    astronomical._get_spica.cache_clear()
    try:
        spica = astronomical._get_spica()
        fake_loader.open.assert_called_once_with(hipparcos.URL)
        assert spica.ra.hours == pytest.approx(201.298 / 15)
        assert panchanga.get_spica_star_object() is spica
        assert list(tmp_path.iterdir()) == []
    finally:
        astronomical._get_spica.cache_clear()
