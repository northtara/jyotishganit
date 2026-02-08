"""
Houses component for jyotishganit library.

Calculates houses in the birth chart.
"""

from jyotishganit.core.constants import SIGN_LORDS, ZODIAC_SIGNS
from jyotishganit.core.models import House, PlanetPosition


def calculate_houses(ascendant_longitude: float) -> list[House]:
    """Calculate the 12 houses for a birth chart using equal house system.

    Args:
        ascendant_longitude: Longitude of the ascendant (0-360 degrees)

    Returns:
        List of 12 House objects
    """
    houses = []

    # House lords in Vedic astrology (same for all)

    # House purposes/groups
    dhrma_houses = [1, 5, 9]
    artha_houses = [2, 6, 10]
    kama_houses = [3, 7, 11]
    moksha_houses = [4, 8, 12]
    kendra_houses = [1, 4, 7, 10]
    trikona_houses = [1, 5, 9]
    trik_houses = [6, 8, 12]
    upachaya_houses = [3, 6, 11]

    for house_num in range(1, 13):
        # Calculate sign for this house
        # Find where this house starts relative to ascendant
        house_start_lon = (ascendant_longitude + (house_num - 1) * 30) % 360
        sign_index = int(house_start_lon // 30)
        sign = ZODIAC_SIGNS[sign_index]

        # Sign lord
        sign_lord = {
            "Aries": "Mars",
            "Taurus": "Venus",
            "Gemini": "Mercury",
            "Cancer": "Moon",
            "Leo": "Sun",
            "Virgo": "Mercury",
            "Libra": "Venus",
            "Scorpio": "Mars",
            "Sagittarius": "Jupiter",
            "Capricorn": "Saturn",
            "Aquarius": "Saturn",
            "Pisces": "Jupiter",
        }[sign]

        # Determine house purposes
        purposes = []
        if house_num in dhrma_houses:
            purposes.append("Dharma")
        if house_num in artha_houses:
            purposes.append("Artha")
        if house_num in kama_houses:
            purposes.append("Kama")
        if house_num in moksha_houses:
            purposes.append("Moksha")
        if house_num in kendra_houses:
            purposes.append("Kendra")
        if house_num in trikona_houses:
            purposes.append("Trikona")
        if house_num in trik_houses:
            purposes.append("Trik")
        if house_num in upachaya_houses:
            purposes.append("Upachaya")

        house = House(
            number=house_num,
            sign=sign,
            lord=sign_lord,
            bhava_bala=0.0,  # Placeholder, would need calculation
            occupants=[],  # To be filled later when planets are calculated
            aspects_received=[],  # To be filled later when aspects are calculated
            purposes=purposes,
        )
        houses.append(house)

    return houses


def update_house_occupants(
    houses: list[House], planets_positions: list[PlanetPosition]
) -> None:
    """Update house occupants based on planet positions.

    Args:
        houses: List of House objects
        planets_positions: List of PlanetPosition objects
    """
    # Reset occupants
    for house in houses:
        house.occupants = []

    # Add planets to appropriate houses
    for planet in planets_positions:
        house_num = planet.house
        if 1 <= house_num <= 12:
            houses[house_num - 1].occupants.append(planet)


def compute_lord_data(planets: list[PlanetPosition], houses: list[House]) -> None:
    """Compute lord placement data for houses and lordship houses for planets."""
    # Create planet to signs mapping
    planet_to_signs: dict[str, list[str]] = {}
    for sign, lord in SIGN_LORDS.items():
        if lord not in planet_to_signs:
            planet_to_signs[lord] = []
        planet_to_signs[lord].append(sign)

    # Planet dict for quick lookup
    planet_dict = {p.celestial_body: p for p in planets}

    # Update houses with lord placements
    for house in houses:
        lord = house.lord
        if lord in planet_dict:
            planet = planet_dict[lord]
            house.lord_placed_sign = planet.sign
            house.lord_placed_house = planet.house

    # Update planets with lordship houses
    for planet in planets:
        if planet.celestial_body in planet_to_signs:
            signs = planet_to_signs[planet.celestial_body]
            planet.has_lordship_houses = []
            for sign in signs:
                for h in houses:
                    if h.sign == sign:
                        planet.has_lordship_houses.append(h.number)
