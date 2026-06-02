"""
Aspects component for jyotishganit library.

Calculates planetary aspects according to Vedic astrology rules.
"""

from jyotishganit.core.models import Aspect, House, PlanetPosition

# Planetary aspects in Vedic astrology
PLANETARY_ASPECTS = {
    "Sun": [7],  # 7th house aspect
    "Moon": [7],  # 7th house aspect
    "Mars": [4, 7, 8],  # 4th, 7th, 8th aspects
    "Mercury": [7],  # 7th house aspect
    "Jupiter": [5, 7, 9],  # 5th, 7th, 9th aspects
    "Venus": [7],  # 7th house aspect
    "Saturn": [3, 7, 10],  # 3rd, 7th, 10th aspects
    "Rahu": [5, 9],  # 5th, 9th aspects
    "Ketu": [5, 9],  # 5th, 9th aspects
}


def get_planets_in_house(
    planet_positions: list[PlanetPosition], house_num: int
) -> list[str]:
    """Get list of planets in a specific house."""
    return [p.celestial_body for p in planet_positions if p.house == house_num]


def calculate_conjuncts(planets: list[PlanetPosition]) -> None:
    """Calculate conjunct planets for each planet in the list."""
    # Group planets by house
    house_to_planets: dict[int, list[str]] = {}
    for planet in planets:
        if planet.house not in house_to_planets:
            house_to_planets[planet.house] = []
        house_to_planets[planet.house].append(planet.celestial_body)

    # Set conjuncts for each planet
    for planet in planets:
        conjuncts = house_to_planets[planet.house][:]  # Copy list
        conjuncts.remove(planet.celestial_body)  # Remove self
        planet.conjuncts = conjuncts


def calculate_planet_aspects(planets: list[PlanetPosition]) -> list[Aspect]:
    """Calculate aspects between planets and return list of Aspect objects."""
    aspects = []
    planet_dict = {p.celestial_body: p for p in planets}

    # For each planet and its aspects
    for planet_name, aspects_houses in PLANETARY_ASPECTS.items():
        if planet_name not in planet_dict:
            continue

        planet = planet_dict[planet_name]

        # Calculate aspect houses
        for aspect_house in aspects_houses:
            # Calculate target house for aspect
            temp = (planet.house + aspect_house - 1) % 12
            target_house = 12 if temp == 0 else temp

            # Note: Backward aspects (3,4,8,10) need special handling? For now, using same formula.
            # In Vedic astrology, some aspects are backward, but the formula above handles circular houses.

            # Find planets in target house
            target_planets = get_planets_in_house(planets, target_house)

            for target_planet in target_planets:
                if target_planet == planet_name:
                    continue  # Don't aspect self

                aspect = Aspect(
                    from_body=planet_name, to_body=target_planet, type=str(aspect_house)
                )
                aspects.append(aspect)

    return aspects


def calculate_house_aspects(
    planets: list[PlanetPosition],
) -> dict[int, list[dict[str, str]]]:
    """Calculate which houses are aspected by which planets and aspect types."""
    house_aspects: dict[int, list[dict[str, str]]] = {i: [] for i in range(1, 13)}

    planet_dict = {p.celestial_body: p for p in planets}

    for planet_name, aspect_houses in PLANETARY_ASPECTS.items():
        if planet_name not in planet_dict:
            continue

        planet = planet_dict[planet_name]
        current_house = planet.house

        for aspect_house in aspect_houses:
            # Calculate which house is aspected using corrected formula
            temp = (current_house + aspect_house - 1) % 12
            aspected_house = 12 if temp == 0 else temp

            # Add planet and aspect type to the aspected house list
            house_aspects[aspected_house].append(
                {"aspecting_planet": planet_name, "aspect_type": str(aspect_house)}
            )

    return house_aspects


def aspect_planets_to_houses(
    house_aspects: dict[int, list[dict[str, str]]], houses: list[House]
) -> None:
    """Apply calculated aspects to House objects."""
    for house in houses:
        house_num = house.number
        if house_num in house_aspects:
            # house_aspects[house_num] is already list of dicts with aspecting_planet and aspect_type
            house.aspects_received = house_aspects[house_num]


def calculate_all_aspects(
    planets: list[PlanetPosition], houses: list[House]
) -> tuple[list[Aspect], list[PlanetPosition]]:
    """Calculate conjuncts, planetary aspects, and house aspects.

    Returns:
        aspects: List of Aspect objects for planetary aspects
        planets: Updated planets with conjuncts and aspects populated
    """
    # Calculate conjuncts
    calculate_conjuncts(planets)

    # Calculate planetary aspects
    aspects = calculate_planet_aspects(planets)

    # Calculate house aspects
    house_aspects = calculate_house_aspects(planets)
    aspect_planets_to_houses(house_aspects, houses)

    # Update planets' "gives" and "receives" based on all aspects (planets and houses)
    planet_dict = {p.celestial_body: p for p in planets}

    # Use sets to deduplicate (to_type, to, type) tuples for gives
    gives_sets: dict[str, set[tuple[str, str | int, str]]] = {
        planet_name: set() for planet_name in planet_dict
    }
    receives_sets: dict[str, set[tuple[str, str | int, str]]] = {
        planet_name: set() for planet_name in planet_dict
    }

    # Process planet-to-planet aspects for gives
    for aspect in aspects:
        if aspect.from_body in planet_dict and aspect.to_body in planet_dict:
            gives_sets[aspect.from_body].add(("planet", aspect.to_body, aspect.type))
            receives_sets[aspect.to_body].add(("planet", aspect.from_body, aspect.type))

    # Process planet-to-house aspects for gives (houses don't receive from planets in gives, only receive)
    for house_num, house_aspect_list in house_aspects.items():
        for aspect_info in house_aspect_list:
            planet_name = aspect_info["aspecting_planet"]
            aspect_type = aspect_info["aspect_type"]
            if planet_name in planet_dict:
                gives_sets[planet_name].add(("house", house_num, aspect_type))

    # Convert sets back to lists of dicts
    for planet_name in planet_dict:
        planet = planet_dict[planet_name]
        gives_list = []
        for target_type, target, aspect_type in gives_sets[planet_name]:
            if target_type == "planet":
                gives_list.append({"to_planet": target, "aspect_type": aspect_type})
            elif target_type == "house":
                gives_list.append({"to_house": target, "aspect_type": aspect_type})
        planet.aspects["gives"] = gives_list

        receives_list = []
        for from_type, source, aspect_type in receives_sets[planet_name]:
            if from_type == "planet":
                receives_list.append(
                    {"from_planet": source, "aspect_type": aspect_type}
                )
        planet.aspects["receives"] = receives_list

    return aspects, planets
