"""
Main API entry point for jyotishganit Vedic astrology library.

Provides functions to calculate complete birth charts with JSON-LD output.
"""

from datetime import datetime, timedelta
from typing import Any

import jyotishganit.components.ashtakavarga as ashtakavarga
import jyotishganit.components.aspects as aspects
import jyotishganit.components.divisional_charts as divisional_charts
import jyotishganit.components.houses as houses
import jyotishganit.components.panchanga as panchanga
import jyotishganit.components.strengths as strengths
import jyotishganit.dasha.vimshottari as vimshottari
from jyotishganit.core.astronomical import calculate_all_positions
from jyotishganit.core.constants import DIVISIONAL_CHARTS
from jyotishganit.core.models import Person, RasiChart, VedicBirthChart
from jyotishganit.core.utils import longitude_to_nakshatra, longitude_to_zodiac


def calculate_birth_chart(
    birth_date: datetime,
    latitude: float,
    longitude: float,
    timezone_offset: float = 0.0,
    location_name: str | None = None,
    name: str | None = None,
) -> VedicBirthChart:
    """
    Calculate complete Vedic birth chart with all components.
    """
    birth_date - timedelta(hours=timezone_offset)

    # Create person info
    person = Person(
        birth_datetime=birth_date,
        latitude=latitude,
        longitude=longitude,
        timezone_offset=timezone_offset,
        name=name,
    )

    # Calculate astronomical positions
    ayanamsa, asc_lon, planets = calculate_all_positions(person)

    # Calculate houses
    house_objects = houses.calculate_houses(asc_lon)
    houses.update_house_occupants(house_objects, planets)

    # Calculate aspects, conjuncts, and house aspects
    aspects_list, planets = aspects.calculate_all_aspects(planets, house_objects)

    # Compute lord placements and lordship data
    houses.compute_lord_data(planets, house_objects)

    # Set ascendant details on house 1
    asc_sign, asc_degrees = longitude_to_zodiac(asc_lon)
    asc_nak, asc_pada, asc_deity = longitude_to_nakshatra(asc_lon)
    house_objects[0].sign_degrees = asc_degrees
    house_objects[0].nakshatra = asc_nak
    house_objects[0].pada = asc_pada
    house_objects[0].nakshatra_deity = asc_deity

    # Create D1 chart
    d1_chart = RasiChart(planets=planets, houses=house_objects)

    # Panchanga
    pancha = panchanga.create_panchanga(birth_date, timezone_offset, ayanamsa.value)

    # Divisional charts
    div_charts = {}
    for chart_code in list(DIVISIONAL_CHARTS.keys())[1:]:  # Skip D1
        div_chart = divisional_charts.compute_divisional_chart(d1_chart, chart_code)
        div_charts[chart_code.lower()] = div_chart

    # Ashtakavarga
    asc_sign, _ = longitude_to_zodiac(asc_lon)
    av = ashtakavarga.calculate_ashtakavarga_for_chart(d1_chart, asc_sign)

    # Planetary strengths (Shadbala)
    strengths.calculate_all_strengths(d1_chart, person)

    # Vimshottari Dashas
    dashas = vimshottari.calculate_vimshottari_dashas(
        birth_date, timezone_offset, latitude, longitude, ayanamsa.value
    )

    # Create complete chart
    birth_chart = VedicBirthChart(
        person=person,
        ayanamsa=ayanamsa,
        panchanga=pancha,
        d1_chart=d1_chart,
        divisional_charts=div_charts,
        ashtakavarga=av,
        dashas=dashas,
    )

    return birth_chart


def get_birth_chart_json(chart: VedicBirthChart) -> dict[str, Any]:
    """
    Convert birth chart to JSON-LD dictionary.

    Args:
        chart: VedicBirthChart object

    Returns:
        Dict with JSON-LD structured data
    """
    return chart.to_dict()


def get_birth_chart_json_string(chart: VedicBirthChart, indent: int = 2) -> str:
    """
    Convert birth chart to formatted JSON-LD string.

    Args:
        chart: VedicBirthChart object
        indent: JSON indentation level

    Returns:
        JSON-formatted string
    """
    import json

    d = chart.to_dict()
    return json.dumps(d, indent=indent, ensure_ascii=False)
