"""
Ashtakavarga calculation for jyotishganit library.

Implements the classical Ashtakavarga method as described in Maharishi Parashara's
Brihat Parashara Hora Shastra, with individual Bhinna Ashtakavarga charts for
each planet and the Sarvashtakavarga total.
"""

from jyotishganit.core.constants import ZODIAC_SIGNS

# Authenticate Ashtakavarga Calculation Tables
# Derived directly from Maharishi Parashara's Brihat Parashara Hora Shastra
BENEFIC_HOUSES = {
    "Sun": {
        "Sun": [1, 2, 4, 7, 8, 9, 10, 11],  # 48 Bindus
        "Moon": [3, 6, 10, 11],
        "Mars": [1, 2, 4, 7, 8, 9, 10, 11],
        "Mercury": [3, 5, 6, 9, 10, 11, 12],
        "Jupiter": [5, 6, 9, 11],
        "Venus": [6, 7, 12],
        "Saturn": [1, 2, 4, 7, 8, 9, 10, 11],
        "Lagna": [3, 4, 6, 10, 11, 12],
    },
    "Moon": {
        "Sun": [3, 6, 7, 8, 10, 11],  # 49 Bindus
        "Moon": [1, 3, 6, 7, 10, 11],
        "Mars": [2, 3, 5, 6, 9, 10, 11],
        "Mercury": [1, 3, 4, 5, 7, 8, 10, 11],
        "Jupiter": [1, 4, 7, 8, 10, 11, 12],
        "Venus": [3, 4, 5, 7, 9, 10, 11],
        "Saturn": [3, 5, 6, 11],
        "Lagna": [3, 6, 10, 11],
    },
    "Mars": {
        "Sun": [3, 5, 6, 10, 11],  # 39 Bindus
        "Moon": [3, 6, 11],
        "Mars": [1, 2, 4, 7, 8, 10, 11],
        "Mercury": [3, 5, 6, 11],
        "Jupiter": [6, 10, 11, 12],
        "Venus": [6, 8, 11, 12],
        "Saturn": [1, 4, 7, 8, 9, 10, 11],
        "Lagna": [1, 3, 6, 10, 11],
    },
    "Mercury": {
        "Sun": [5, 6, 9, 11, 12],  # 54 Bindus
        "Moon": [2, 4, 6, 8, 10, 11],
        "Mars": [1, 2, 4, 7, 8, 9, 10, 11],
        "Mercury": [1, 3, 5, 6, 9, 10, 11, 12],
        "Jupiter": [6, 8, 11, 12],
        "Venus": [1, 2, 3, 4, 5, 8, 9, 11],
        "Saturn": [1, 2, 4, 7, 8, 9, 10, 11],
        "Lagna": [1, 2, 4, 6, 8, 10, 11],
    },
    "Jupiter": {
        "Sun": [1, 2, 3, 4, 7, 8, 9, 10, 11],  # 56 Bindus
        "Moon": [2, 5, 7, 9, 11],
        "Mars": [1, 2, 4, 7, 8, 10, 11],
        "Mercury": [1, 2, 4, 5, 6, 9, 10, 11],
        "Jupiter": [1, 2, 3, 4, 7, 8, 10, 11],
        "Venus": [2, 5, 6, 9, 10, 11],
        "Saturn": [3, 5, 6, 12],
        "Lagna": [1, 2, 4, 5, 6, 7, 9, 10, 11],
    },
    "Venus": {
        "Sun": [8, 11, 12],  # 52 Bindus
        "Moon": [1, 2, 3, 4, 5, 8, 9, 11, 12],
        "Mars": [3, 5, 6, 9, 11, 12],
        "Mercury": [3, 5, 6, 9, 11],
        "Jupiter": [5, 8, 9, 10, 11],
        "Venus": [1, 2, 3, 4, 5, 8, 9, 10, 11],
        "Saturn": [3, 4, 5, 8, 9, 10, 11],
        "Lagna": [1, 2, 3, 4, 5, 8, 9, 11],
    },
    "Saturn": {
        "Sun": [1, 2, 4, 7, 8, 10, 11],  # 39 Bindus
        "Moon": [3, 6, 11],
        "Mars": [3, 5, 6, 10, 11, 12],
        "Mercury": [6, 8, 9, 10, 11, 12],
        "Jupiter": [5, 6, 11, 12],
        "Venus": [6, 11, 12],
        "Saturn": [3, 5, 6, 11],
        "Lagna": [1, 3, 4, 6, 10, 11],
    },
}


def calculate_bhinna_ashtakavarga(
    planet: str, natal_chart: dict[str, int], benefic_houses: dict
) -> dict[str, int]:
    """
    Calculate individual Bhinna Ashtakavarga chart for a specific planet.

    Args:
        planet: The planet for which to calculate BAV (Sun, Moon, Mars, etc.)
        natal_chart: Dict mapping planet/lagna names to sign indices (0-11)
        benefic_houses: Benefic houses lookup table

    Returns:
        Dict of sign names to bindu count
    """
    # Initialize BAV chart as dictionary with zero bindus
    bav_chart = dict.fromkeys(ZODIAC_SIGNS, 0)

    # Contributors list
    contributors = [
        "Sun",
        "Moon",
        "Mars",
        "Mercury",
        "Jupiter",
        "Venus",
        "Saturn",
        "Lagna",
    ]

    # Iterate through each contributor
    for contributor in contributors:
        # Get sign index where contributor is located
        contributor_sign = natal_chart[contributor]

        # Get benefic house set for this combination
        benefic_house_set = benefic_houses[planet][contributor]

        # For each benefic house number, calculate target sign and add bindu
        for house_num in benefic_house_set:
            # Calculate target sign index (house_num - 1 because houses are 1-12, indices 0-11)
            target_sign_index = (contributor_sign + house_num - 1) % 12

            # Get sign name and add one bindu
            sign_name = ZODIAC_SIGNS[target_sign_index]
            bav_chart[sign_name] += 1

    return bav_chart


def calculate_ashtakavarga(
    natal_chart: dict[str, int],
) -> dict[str, dict[str, dict[str, int]]]:
    """
    Calculate all Ashtakavarga charts including individual BAVs and SAV.

    Args:
        natal_chart: Dict mapping planet/lagna names to sign indices (0-11)

    Returns:
        Dict with 'bhav' containing individual planet charts and 'sav' containing total
    """
    # Individual Bhinna Ashtakavarga charts
    bhav_charts = {}
    planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

    for planet in planets:
        bhav_charts[planet] = calculate_bhinna_ashtakavarga(
            planet, natal_chart, BENEFIC_HOUSES
        )

    # Calculate Sarvashtakavarga (SAV) by summing all BAVs
    sav_chart = dict.fromkeys(ZODIAC_SIGNS, 0)
    for planet in planets:
        for sign, bindus in bhav_charts[planet].items():
            sav_chart[sign] += bindus

    return {"bhav": bhav_charts, "sav": sav_chart}


def create_natal_chart_sign_mapping(d1_chart, ascendant_sign: str) -> dict[str, int]:
    """
    Create sign mapping dictionary from D1 chart.

    Args:
        d1_chart: RasiChart object
        ascendant_sign: Ascendant sign string

    Returns:
        Dict mapping planet/lagna to sign index (0-11)
    """
    # Map sign strings to 0-based indices
    sign_to_index = {sign: idx for idx, sign in enumerate(ZODIAC_SIGNS)}

    natal_chart = {}

    # Add planets
    for planet in d1_chart.planets:
        natal_chart[planet.celestial_body] = sign_to_index[planet.sign]

    # Add Lagna (ascendant)
    natal_chart["Lagna"] = sign_to_index[ascendant_sign]

    return natal_chart


def calculate_ashtakavarga_for_chart(d1_chart, ascendant_sign: str):
    """
    Main function to calculate ashtakvarga for a birth chart.

    Args:
        d1_chart: RasiChart object
        ascendant_sign: String representing ascendant sign

    Returns:
        Ashtakavarga object
    """
    from jyotishganit.core.models import Ashtakavarga

    # Create natal chart sign mapping
    natal_chart = create_natal_chart_sign_mapping(d1_chart, ascendant_sign)

    # Calculate ashtakvarga
    result = calculate_ashtakavarga(natal_chart)

    return Ashtakavarga(bhav=result["bhav"], sav=result["sav"])
