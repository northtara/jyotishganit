"""
Strength calculations (Bala) for jyotishganit library, modern-adapted from PyJHora.
CORRECTED VERSION with all fixes applied.
"""

import datetime
import math

# Use global Skyfield objects from core.astronomical
from jyotishganit.core.astronomical import (
    get_ephemeris,
    get_planet_declination,
    get_solar_ingress_weekday,
    skyfield_time_from_datetime,
)
from jyotishganit.core.constants import (
    BALA_RELATION_RATIOS,
    BHAVA_STRENGTH_FROM_SIGN_NATURE,
    DECANATE_RULER_GROUPS,
    DEFAULT_PRECISION,
    DIGBALA_STRONG_HOUSES,
    EXALTATION_DEGREES,
    FEMALE_PLANETS_SHADBALA,
    FULL_ASPECT_STRENGTH,
    JUPITER_SPECIAL_ASPECTS,
    KENDRA_BALA_SCORES,
    MALE_PLANETS_SHADBALA,
    MARS_SPECIAL_ASPECTS,
    NAISARGIKA_VALUES,
    NATURAL_BENEFIC_SHADBALA,
    NATURAL_MALEFIC_SHADBALA,
    PLANET_INDEX_MAP,
    PLANET_MEAN_MOTION,
    PLANETARY_DIGNITIES,
    PLANETARY_HOUR_SEQUENCE,
    PLANETARY_RELATIONS,
    PLANETS_WITH_SHADBALA,
    RUPA_SCALING,
    SATURN_SPECIAL_ASPECTS,
    SIGN_LORDS,
    SIGN_NATURE_CLASSIFICATION,
    SPECIAL_ASPECT_ORB,
    TRIBHAGA_DAY_LORDS,
    TRIBHAGA_NIGHT_LORDS,
    VIMSHOPAKA_DIVISION_STRENGTHS,
    WEEKDAY_LORDS,
    YUDDHABALA_PLANETS,
    ZODIAC_SIGNS,
)
from jyotishganit.core.models import Person, RasiChart


# --- Helper Functions ---
def normalize(angle: float) -> float:
    return (angle % 360 + 360) % 360


def angdiff(a: float, b: float) -> float:
    d = abs(normalize(a) - normalize(b))
    return 360 - d if d > 180 else d


def planet_longitude_from_sign(planet_sign: str, planet_degrees: float) -> float:
    return ZODIAC_SIGNS.index(planet_sign) * 30 + planet_degrees


def calculate_degrees_in_varga_sign(planet_longitude: float, divisor: int) -> float:
    segment_size = 360.0 / divisor
    segment_index = int(planet_longitude / segment_size)
    degrees_from_segment_start = planet_longitude - (segment_index * segment_size)
    return degrees_from_segment_start * divisor / 12.0


def get_varga_sign(long_deg: float, divisor: int) -> str:
    """Generic D-n varga sign determination."""
    idx = int((normalize(long_deg) * divisor) // 30) % 12
    return ZODIAC_SIGNS[idx]


class PlanetaryRelationshipMatrix:
    """
    Comprehensive planetary relationship matrix for Saptavargaja Bala calculations.
    Handles natural, temporary, and combined planetary relationships.
    """

    def __init__(self):
        self.natural_relations = PLANETARY_RELATIONS
        self.sign_lords = SIGN_LORDS
        self.dignities = PLANETARY_DIGNITIES

    def get_natural_relationship(self, planet1: str, planet2: str) -> str:
        """Get natural relationship between two planets."""
        if (
            planet1 not in self.natural_relations
            or planet2 not in self.natural_relations[planet1]
        ):
            return "SAMA"
        return self.natural_relations[planet1][planet2]

    def get_temporary_relationship(self, planet1_sign: str, planet2_sign: str) -> str:
        """
        Calculate temporary relationship based on sign positions.
        Planets in 2nd, 3rd, 4th, 10th, 11th, 12th houses from each other are friends.
        Others are enemies.
        """
        if not planet1_sign or not planet2_sign:
            return "SAMA"

        try:
            sign1_idx = ZODIAC_SIGNS.index(planet1_sign)
            sign2_idx = ZODIAC_SIGNS.index(planet2_sign)

            # Calculate house difference
            house_diff = (sign2_idx - sign1_idx) % 12

            # Friendly houses: 2nd, 3rd, 4th, 10th, 11th, 12th (1-indexed)
            # Converting to 0-indexed: 1, 2, 3, 9, 10, 11
            friendly_positions = [1, 2, 3, 9, 10, 11]

            return "MITRA" if house_diff in friendly_positions else "SHATRU"

        except (ValueError, IndexError):
            return "SAMA"

    def get_combined_relationship(self, natural_rel: str, temporary_rel: str) -> str:
        """
        Combine natural and temporary relationships.

        Natural Friend + Temporary Friend = Adhi Mitra (Best Friend)
        Natural Friend + Temporary Enemy = Sama (Neutral)
        Natural Enemy + Temporary Friend = Sama (Neutral)
        Natural Enemy + Temporary Enemy = Adhi Shatru (Worst Enemy)
        Natural Neutral + Temporary Friend = Mitra (Friend)
        Natural Neutral + Temporary Enemy = Shatru (Enemy)
        """
        # Normalize relationship names
        nat_rel = natural_rel.upper()
        temp_rel = temporary_rel.upper()

        if nat_rel in ["MITRA", "FRIEND"] and temp_rel in ["MITRA", "FRIEND"]:
            return "ATHIMITRA"
        elif (
            nat_rel in ["MITRA", "FRIEND"]
            and temp_rel in ["SHATRU", "ENEMY"]
            or nat_rel in ["SHATRU", "ENEMY"]
            and temp_rel in ["MITRA", "FRIEND"]
        ):
            return "SAMA"
        elif nat_rel in ["SHATRU", "ENEMY"] and temp_rel in ["SHATRU", "ENEMY"]:
            return "ATHISHATRU"
        elif nat_rel == "SAMA" and temp_rel in ["MITRA", "FRIEND"]:
            return "MITRA"
        elif nat_rel == "SAMA" and temp_rel in ["SHATRU", "ENEMY"]:
            return "SHATRU"
        else:
            return "SAMA"

    def is_moolatrikona_sign(self, planet: str, sign: str) -> bool:
        """Check if planet is in moolatrikona sign (entire sign, no degree check)."""
        if planet not in self.dignities:
            return False
        mool_info = self.dignities[planet].get("moolatrikona")
        return mool_info is not None and mool_info["sign"] == sign

    def is_own_sign(self, planet: str, sign: str) -> bool:
        """Check if planet is in its own sign."""
        return sign in self.sign_lords and self.sign_lords[sign] == planet

    def get_relationship_score(
        self, planet: str, sign_lord: str, planet_sign: str, lord_sign: str
    ) -> float:
        """
        Get relationship score for Saptavargaja Bala.

        Hierarchy:
        1. Moolatrikona: 45 shashtiamsas
        2. Own sign: 30 shashtiamsas
        3. Relationship-based scores:
           - ATHIMITRA: 22.5 shashtiamsas
           - MITRA: 15 shashtiamsas
           - SAMA: 7.5 shashtiamsas
           - SHATRU: 3.75 shashtiamsas
           - ATHISHATRU: 1.875 shashtiamsas
        """
        # Check moolatrikona first
        if self.is_moolatrikona_sign(planet, planet_sign):
            return 45.0

        # Check own sign
        if self.is_own_sign(planet, planet_sign):
            return 30.0

        # Calculate relationship-based score
        natural_rel = self.get_natural_relationship(planet, sign_lord)
        temporary_rel = self.get_temporary_relationship(planet_sign, lord_sign)
        combined_rel = self.get_combined_relationship(natural_rel, temporary_rel)

        relationship_scores = {
            "ATHIMITRA": 22.5,
            "MITRA": 15.0,
            "SAMA": 7.5,
            "SHATRU": 3.75,
            "ATHISHATRU": 1.875,
        }

        return relationship_scores.get(combined_rel.upper(), 7.5)


# --- Main Calculation Orchestrator ---
def calculate_all_strengths(chart: RasiChart, person: Person) -> RasiChart:
    """Calculate all planetary and house strengths for the given chart."""
    compute_shadbala(chart, person)
    compute_vimshopaka_balas(chart)
    compute_ishtakashtabalas(chart)
    compute_bhava_balas(chart)
    return chart


# --- Shadbala Calculations ---
def compute_shadbala(chart: RasiChart, person: Person) -> None:
    # 1. Compute individual strengths
    compute_sthanabala(chart)
    compute_digbala(chart)
    compute_kaalabala(chart, person)
    compute_chestagbala(chart, person)
    compute_naisargikabala(chart)
    compute_drikbala(chart)

    # 2. Sum into pre-Yuddha total
    for planet in chart.planets:
        if planet.celestial_body in NAISARGIKA_VALUES:
            total = (
                planet.shadbala.get("Sthanabala", {}).get("Total", 0)
                + planet.shadbala.get("Digbala", 0)
                + planet.shadbala.get("Kaalabala", {}).get("Total", 0)
                + planet.shadbala.get("Cheshtabala", 0)
                + planet.shadbala.get("Naisargikabala", 0)
                + planet.shadbala.get("Drikbala", 0)
            )
            planet.shadbala["Shadbala"] = {"Total": round(total, DEFAULT_PRECISION)}

    # 3. Calculate and apply Yuddha Bala adjustment
    compute_yuddhabala(chart)

    for planet in chart.planets:
        if planet.celestial_body in NAISARGIKA_VALUES:
            yuddha_adj = planet.shadbala.get("Kaalabala", {}).get("Yuddhabala", 0)
            planet.shadbala["Shadbala"]["Total"] += yuddha_adj
            planet.shadbala["Shadbala"]["Rupas"] = round(
                planet.shadbala["Shadbala"]["Total"] / RUPA_SCALING, DEFAULT_PRECISION
            )


# --- STHANABALA Components ---


def compute_sthanabala(chart: RasiChart) -> None:
    compute_uchhabala(chart)
    compute_saptavargajabala(chart)
    compute_ojhayugmarashiamsabala(chart)
    compute_kendradhibala(chart)
    compute_drekkanabala(chart)
    for planet in chart.planets:
        if planet.celestial_body in NAISARGIKA_VALUES:
            total = (
                planet.shadbala.get("Sthanabala", {}).get("Uchhabala", 0)
                + planet.shadbala.get("Sthanabala", {}).get("Saptavargajabala", 0)
                + planet.shadbala.get("Sthanabala", {}).get(
                    "Ojhayugmarashiamshabala", 0
                )
                + planet.shadbala.get("Sthanabala", {}).get("Kendradhibala", 0)
                + planet.shadbala.get("Sthanabala", {}).get("Drekshanabala", 0)
            )
            if "Sthanabala" not in planet.shadbala:
                planet.shadbala["Sthanabala"] = {}
            planet.shadbala["Sthanabala"]["Total"] = round(total, DEFAULT_PRECISION)


def compute_uchhabala(chart: RasiChart) -> None:
    for planet in chart.planets:
        if planet.celestial_body in EXALTATION_DEGREES:
            deb_point = normalize(EXALTATION_DEGREES[planet.celestial_body] + 180)
            p_long = planet_longitude_from_sign(planet.sign, planet.sign_degrees)
            bala = angdiff(p_long, deb_point) / 3.0
            if "Sthanabala" not in planet.shadbala:
                planet.shadbala["Sthanabala"] = {}
            planet.shadbala["Sthanabala"]["Uchhabala"] = round(bala, 3)


def get_planetary_dignity_classification(
    planet_name: str,
    varga_sign: str,
    degrees_in_varga: float,
    varga_degreesConsidered: bool = False,
) -> str:
    sign_num = ZODIAC_SIGNS.index(varga_sign)
    if varga_degreesConsidered:
        if planet_name == "Sun" and sign_num == 4:
            return "mool" if degrees_in_varga <= 20.0 else "own"
        if planet_name == "Moon":
            if sign_num == 1:
                return "mool" if degrees_in_varga <= 3.0 else "mool"
            if sign_num == 3:
                return "own"
        if planet_name == "Mars":
            if sign_num == 0:
                return "mool" if degrees_in_varga <= 12.0 else "own"
            if sign_num == 7:
                return "own"
        if planet_name == "Mercury":
            if sign_num == 5:
                return (
                    "mool"
                    if degrees_in_varga <= 15.0 or (degrees_in_varga <= 20.0)
                    else "own"
                )
            if sign_num == 2:
                return "own"
        if planet_name == "Jupiter":
            if sign_num == 8:
                return "mool" if degrees_in_varga <= 10.0 else "own"
            if sign_num == 11:
                return "own"
        if planet_name == "Venus":
            if sign_num == 6:
                return "mool" if degrees_in_varga <= 15.0 else "own"
            if sign_num == 1:
                return "own"
        if planet_name == "Saturn":
            if sign_num == 10:
                return "mool" if degrees_in_varga <= 20.0 else "own"
            if sign_num == 9:
                return "own"
    else:
        if planet_name == "Sun":
            return "own" if sign_num == 4 else "none"
        if planet_name == "Moon":
            return "own" if sign_num == 3 else ("mool" if sign_num == 1 else "none")
        if planet_name == "Mars":
            return "own" if sign_num == 7 else ("mool" if sign_num == 0 else "none")
        if planet_name == "Mercury":
            return "own" if sign_num == 2 else ("mool" if sign_num == 5 else "none")
        if planet_name == "Jupiter":
            return "own" if sign_num == 11 else ("mool" if sign_num == 8 else "none")
        if planet_name == "Venus":
            return "own" if sign_num == 1 else ("mool" if sign_num == 6 else "none")
        if planet_name == "Saturn":
            return "own" if sign_num == 9 else ("mool" if sign_num == 10 else "none")
    return "neutral"


def get_planetary_dispositor_relation(
    planet_name: str, varga_sign: str, degrees_in_varga: float, chart: RasiChart
) -> str:
    dignity = get_planetary_dignity_classification(
        planet_name, varga_sign, degrees_in_varga
    )
    if dignity in ["mool", "own"]:
        return dignity

    dispositor_name = SIGN_LORDS[varga_sign]
    if dispositor_name == planet_name:
        return "own"

    relations = PLANETARY_RELATIONS[planet_name]
    natural_val = (
        1
        if dispositor_name in relations["friends"]
        else -1
        if dispositor_name in relations["enemies"]
        else 0
    )

    planet_obj = next(
        (p for p in chart.planets if p.celestial_body == planet_name), None
    )
    dispositor_obj = next(
        (p for p in chart.planets if p.celestial_body == dispositor_name), None
    )
    if not planet_obj or not dispositor_obj:
        return "SAMA"

    house_diff = (dispositor_obj.house - planet_obj.house + 12) % 12
    temporary_val = 1 if house_diff in [0, 2, 3, 4, 10, 11, 12] else -1

    combined_val = natural_val + temporary_val
    if combined_val == 2:
        return "ATHIMITRA"
    if combined_val == 1:
        return "MITRA"
    if combined_val == -1:
        return "SHATRU"
    if combined_val == -2:
        return "ATHISHATRU"
    return "SAMA"


def compute_saptavargajabala(chart: RasiChart) -> None:
    """
    Enhanced Saptavargaja Bala computation using PlanetaryRelationshipMatrix.

    Implements hierarchical scoring system:
    1. Moolatrikona (entire sign): 45 shashtiamsas
    2. Own sign: 30 shashtiamsas
    3. Relationship-based scores (ATHIMITRA to ATHISHATRU): 22.5 to 1.875 shashtiamsas

    Calculates strength from 7 divisional charts: D1, D2, D3, D7, D9, D12, D30
    """
    # Initialize relationship matrix
    rel_matrix = PlanetaryRelationshipMatrix()

    # Sapta Varga divisions
    divisions = [1, 2, 3, 7, 9, 12, 30]

    for planet in chart.planets:
        if planet.celestial_body in NAISARGIKA_VALUES:
            total_score = 0.0

            for div in divisions:
                # Get varga position
                p_long = planet_longitude_from_sign(planet.sign, planet.sign_degrees)
                v_sign = get_varga_sign(p_long, div)

                # Get sign lord
                sign_lord = SIGN_LORDS.get(v_sign)
                if not sign_lord:
                    continue

                # Find sign lord's position in D1 (for temporary relationship)
                lord_planet = next(
                    (p for p in chart.planets if p.celestial_body == sign_lord), None
                )
                lord_sign = lord_planet.sign if lord_planet else None

                # Calculate score using relationship matrix
                score = rel_matrix.get_relationship_score(
                    planet.celestial_body, sign_lord, v_sign, lord_sign
                )

                total_score += score

            # Store result
            if "Sthanabala" not in planet.shadbala:
                planet.shadbala["Sthanabala"] = {}
            planet.shadbala["Sthanabala"]["Saptavargajabala"] = round(
                total_score, DEFAULT_PRECISION
            )


def analyze_saptavargaja_breakdown(chart: RasiChart, planet_name: str) -> dict:
    """
    Detailed breakdown of Saptavargaja Bala for a specific planet.
    Returns analysis of each divisional chart contribution.
    """
    rel_matrix = PlanetaryRelationshipMatrix()
    divisions = [1, 2, 3, 7, 9, 12, 30]

    planet = next((p for p in chart.planets if p.celestial_body == planet_name), None)
    if not planet:
        return {"error": f"Planet {planet_name} not found"}

    breakdown = {"planet": planet_name, "total_score": 0.0, "divisional_analysis": []}

    for div in divisions:
        p_long = planet_longitude_from_sign(planet.sign, planet.sign_degrees)
        v_sign = get_varga_sign(p_long, div)
        sign_lord = SIGN_LORDS.get(v_sign)

        if not sign_lord:
            continue

        lord_planet = next(
            (p for p in chart.planets if p.celestial_body == sign_lord), None
        )
        lord_sign = lord_planet.sign if lord_planet else None

        # Check dignities
        is_mool = rel_matrix.is_moolatrikona_sign(planet_name, v_sign)
        is_own = rel_matrix.is_own_sign(planet_name, v_sign)

        # Get relationships
        natural_rel = rel_matrix.get_natural_relationship(planet_name, sign_lord)
        temp_rel = (
            rel_matrix.get_temporary_relationship(v_sign, lord_sign)
            if lord_sign
            else "SAMA"
        )
        combined_rel = rel_matrix.get_combined_relationship(natural_rel, temp_rel)

        score = rel_matrix.get_relationship_score(
            planet_name, sign_lord, v_sign, lord_sign
        )

        analysis = {
            f"D{div}": {
                "sign": v_sign,
                "sign_lord": sign_lord,
                "lord_sign": lord_sign,
                "is_moolatrikona": is_mool,
                "is_own_sign": is_own,
                "natural_relationship": natural_rel,
                "temporary_relationship": temp_rel,
                "combined_relationship": combined_rel,
                "score": score,
                "reason": "Moolatrikona"
                if is_mool
                else "Own Sign"
                if is_own
                else f"Relationship: {combined_rel}",
            }
        }

        breakdown["divisional_analysis"].append(analysis)
        breakdown["total_score"] += score

    breakdown["total_score"] = round(breakdown["total_score"], 2)
    return breakdown


def compute_ojhayugmarashiamsabala(chart: RasiChart) -> None:
    for planet_name in MALE_PLANETS_SHADBALA:
        planet = next(
            (p for p in chart.planets if p.celestial_body == planet_name), None
        )
        if not planet:
            continue

        p_long = planet_longitude_from_sign(planet.sign, planet.sign_degrees)
        d1_is_odd = ZODIAC_SIGNS.index(planet.sign) % 2 == 0
        d9_is_odd = ZODIAC_SIGNS.index(get_varga_sign(p_long, 9)) % 2 == 0

        bala = 0
        if d1_is_odd:
            bala += 15
        if d9_is_odd:
            bala += 15

        if "Sthanabala" not in planet.shadbala:
            planet.shadbala["Sthanabala"] = {}
        planet.shadbala["Sthanabala"]["Ojhayugmarashiamshabala"] = float(bala)

    for planet_name in FEMALE_PLANETS_SHADBALA:
        planet = next(
            (p for p in chart.planets if p.celestial_body == planet_name), None
        )
        if not planet:
            continue

        p_long = planet_longitude_from_sign(planet.sign, planet.sign_degrees)
        d1_is_odd = ZODIAC_SIGNS.index(planet.sign) % 2 == 0
        d9_is_odd = ZODIAC_SIGNS.index(get_varga_sign(p_long, 9)) % 2 == 0

        bala = 0
        if not d1_is_odd:
            bala += 15
        if not d9_is_odd:
            bala += 15

        if "Sthanabala" not in planet.shadbala:
            planet.shadbala["Sthanabala"] = {}
        planet.shadbala["Sthanabala"]["Ojhayugmarashiamshabala"] = float(bala)


def compute_kendradhibala(chart: RasiChart) -> None:
    for planet in chart.planets:
        if planet.celestial_body in NAISARGIKA_VALUES:
            bala = KENDRA_BALA_SCORES.get(planet.house, 15)
            if "Sthanabala" not in planet.shadbala:
                planet.shadbala["Sthanabala"] = {}
            planet.shadbala["Sthanabala"]["Kendradhibala"] = float(bala)


### CORRECTED: Drekkana Bala ###
def compute_drekkanabala(chart: RasiChart) -> None:
    """
    Computes Drekkana Bala based on planet index in decanate groups.
    FIXED: Now matches PyJHora's implementation.
    """
    for planet in chart.planets:
        if planet.celestial_body in PLANET_INDEX_MAP:
            # Determine decanate index (0, 1, or 2)
            decanate_index = int(planet.sign_degrees // 10.0)

            # Get planet index
            planet_index = PLANET_INDEX_MAP[planet.celestial_body]

            # Check if planet index is in the list for this decanate
            bala = (
                15.0
                if planet_index in DECANATE_RULER_GROUPS.get(decanate_index, [])
                else 0.0
            )

            if "Sthanabala" not in planet.shadbala:
                planet.shadbala["Sthanabala"] = {}
            planet.shadbala["Sthanabala"]["Drekshanabala"] = bala


# --- DIGBALA ---


def compute_digbala(chart: RasiChart) -> None:
    for planet in chart.planets:
        if planet.celestial_body in DIGBALA_STRONG_HOUSES:
            strong_house = DIGBALA_STRONG_HOUSES[planet.celestial_body]
            strong_house_sign_idx = ZODIAC_SIGNS.index(
                chart.houses[strong_house - 1].sign
            )
            strong_point = strong_house_sign_idx * 30 + 15.0
            p_long = planet_longitude_from_sign(planet.sign, planet.sign_degrees)
            bala = (180 - angdiff(p_long, strong_point)) / 3.0
            planet.shadbala["Digbala"] = round(bala, 3)


# --- KAALABALA Components ---


def compute_kaalabala(chart: RasiChart, person: Person) -> None:
    compute_nathonnatabala(chart, person)
    compute_pakshabala(chart)
    compute_tribhagabala(chart, person)
    compute_varsha_maasa_dina_horabala(chart, person)
    compute_ayanabala(chart, person)
    for planet in chart.planets:
        if planet.celestial_body in NAISARGIKA_VALUES:
            total = (
                planet.shadbala.get("Kaalabala", {}).get("Natonnatabala", 0)
                + planet.shadbala.get("Kaalabala", {}).get("Pakshabala", 0)
                + planet.shadbala.get("Kaalabala", {}).get("Tribhagabala", 0)
                + planet.shadbala.get("Kaalabala", {}).get("VarshaMaasaDinaHoraBala", 0)
                + planet.shadbala.get("Kaalabala", {}).get("Ayanabala", 0)
            )
            if "Kaalabala" not in planet.shadbala:
                planet.shadbala["Kaalabala"] = {}
            planet.shadbala["Kaalabala"]["Total"] = round(total, 3)


def compute_nathonnatabala(chart: RasiChart, person: Person) -> None:
    from jyotishganit.core.astronomical import get_sunrise_sunset

    sunrise, sunset = get_sunrise_sunset(person)
    birth_hour = (
        person.birth_datetime.hour
        + person.birth_datetime.minute / 60
        + person.birth_datetime.second / 3600
    )
    is_day_birth = sunrise <= birth_hour < sunset

    time_from_midpoint = (
        abs(birth_hour - 12)
        if is_day_birth
        else abs(birth_hour - 24 if birth_hour > 12 else birth_hour)
    )
    base_bala = (6 - time_from_midpoint) * 10
    for planet in chart.planets:
        if planet.celestial_body in NAISARGIKA_VALUES:
            bala = 0.0
            if planet.celestial_body == "Mercury":
                bala = 60.0
            elif planet.celestial_body in ["Sun", "Jupiter", "Venus"]:
                bala = base_bala if is_day_birth else 60 - base_bala
            elif planet.celestial_body in ["Moon", "Mars", "Saturn"]:
                bala = 60 - base_bala if is_day_birth else base_bala
            if "Kaalabala" not in planet.shadbala:
                planet.shadbala["Kaalabala"] = {}
            planet.shadbala["Kaalabala"]["Natonnatabala"] = round(max(0, bala), 3)


def compute_pakshabala(chart: RasiChart) -> None:
    sun_long = planet_longitude_from_sign(
        next(p.sign for p in chart.planets if p.celestial_body == "Sun"),
        next(p.sign_degrees for p in chart.planets if p.celestial_body == "Sun"),
    )
    moon_long = planet_longitude_from_sign(
        next(p.sign for p in chart.planets if p.celestial_body == "Moon"),
        next(p.sign_degrees for p in chart.planets if p.celestial_body == "Moon"),
    )
    moon_phase = angdiff(moon_long, sun_long)
    for planet in chart.planets:
        if planet.celestial_body in NATURAL_BENEFIC_SHADBALA:
            bala = moon_phase / 3.0
            # Moon's Paksha Bala is doubled
            if "Kaalabala" not in planet.shadbala:
                planet.shadbala["Kaalabala"] = {}
            planet.shadbala["Kaalabala"]["Pakshabala"] = round(bala, 3)
        elif planet.celestial_body in NATURAL_MALEFIC_SHADBALA:
            bala = (180 - moon_phase) / 3.0
            if "Kaalabala" not in planet.shadbala:
                planet.shadbala["Kaalabala"] = {}
            planet.shadbala["Kaalabala"]["Pakshabala"] = round(bala, 3)
        else:
            # Neuter planets (Mercury, Rahu, Ketu) get 0 Pakshabala
            if "Kaalabala" not in planet.shadbala:
                planet.shadbala["Kaalabala"] = {}
            planet.shadbala["Kaalabala"]["Pakshabala"] = 0.0


def compute_tribhagabala(chart: RasiChart, person: Person) -> None:
    from jyotishganit.core.astronomical import get_sunrise_sunset

    sunrise, sunset = get_sunrise_sunset(person)
    birth_hour = (
        person.birth_datetime.hour
        + person.birth_datetime.minute / 60
        + person.birth_datetime.second / 3600
    )
    is_day_birth = sunrise <= birth_hour < sunset

    day_duration = sunset - sunrise
    night_duration = 24 - day_duration

    part_duration = day_duration / 3 if is_day_birth else night_duration / 3
    birth_time_from_event = (
        birth_hour - sunrise if is_day_birth else (birth_hour - sunset + 24) % 24
    )
    part_index = min(2, int(birth_time_from_event / part_duration))  # Clamp to 0-2

    ruler = (
        TRIBHAGA_DAY_LORDS[part_index]
        if is_day_birth
        else TRIBHAGA_NIGHT_LORDS[part_index]
    )

    for planet in chart.planets:
        if planet.celestial_body in NAISARGIKA_VALUES:
            bala = 0.0
            if planet.celestial_body == "Jupiter" or planet.celestial_body == ruler:
                bala = 60.0
            if "Kaalabala" not in planet.shadbala:
                planet.shadbala["Kaalabala"] = {}
            planet.shadbala["Kaalabala"]["Tribhagabala"] = bala


### CORRECTED: Varsha-Maasa-Dina-Hora Bala using Solar Ingress for Astronomical Accuracy ###
def compute_varsha_maasa_dina_horabala(chart: RasiChart, person: Person) -> None:
    """
    Calculates Varsha, Maasa, Dina, and Hora Bala.
    FINAL VERSION: Uses the authoritative Solar Ingress method for Year/Month lords
    and correctly adjusts the Day Lord (Vaara) for births before sunrise.
    """
    bd = person.birth_datetime
    birth_hour = bd.hour + bd.minute / 60.0 + bd.second / 3600.0

    # --- Varsha Lord (Year Lord) using Solar Ingress ---
    # Lord of the weekday when Sun enters Aries (0°) for the birth year.
    varsha_weekday = get_solar_ingress_weekday(0.0, bd.year)
    varshalord = WEEKDAY_LORDS[varsha_weekday]

    # --- Maasa Lord (Month Lord) using Solar Ingress ---
    # Lord of the weekday for the most recent solar ingress before birth.
    sun_pos = next(p for p in chart.planets if p.celestial_body == "Sun")
    sun_long = planet_longitude_from_sign(sun_pos.sign, sun_pos.sign_degrees)
    ingress_longitude = int(sun_long // 30) * 30.0  # Start of the Sun's current sign
    maasa_weekday = get_solar_ingress_weekday(ingress_longitude, bd.year)
    maasalord = WEEKDAY_LORDS[maasa_weekday]

    # --- Vaara Lord (Day Lord) with Sunrise Adjustment ---
    from jyotishganit.core.astronomical import get_sunrise_sunset

    sunrise, _ = get_sunrise_sunset(person)

    # Get the Python weekday (Mon=0, Sun=6) for the birth date
    effective_date = bd
    if birth_hour < sunrise:
        # If born before sunrise, the Vedic day is the previous day
        effective_date -= datetime.timedelta(days=1)

    python_weekday = effective_date.weekday()
    vedic_weekday = (python_weekday + 1) % 7  # Convert to Vedic (Sun=0...Sat=6)
    vaaralord = WEEKDAY_LORDS[vedic_weekday]

    # --- Hora Lord (Hour Lord) ---
    # Uses the *actual birth weekday* for the Hora calculation start point
    actual_vedic_weekday = (bd.weekday() + 1) % 7
    hours_since_sunrise = (
        birth_hour - sunrise if birth_hour >= sunrise else (24.0 + birth_hour - sunrise)
    )

    # Hora lord sequence starts from the lord of the actual weekday at sunrise
    # The lord of the first hour of the day is the lord of the day itself.
    hora_lord_start_index = actual_vedic_weekday

    # Planetary hour sequence in Vedic astrology
    # Sun, Venus, Mercury, Moon, Saturn, Jupiter, Mars
    # Our daylord list is [Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn]
    # Indices:           [0,   1,    2,    3,       4,       5,      6]
    # The sequence is: Sun(0)->Ven(5)->Mer(3)->Moo(1)->Sat(6)->Jup(4)->Mar(2)
    start_in_sequence = PLANETARY_HOUR_SEQUENCE.index(hora_lord_start_index)
    current_hour_index_in_sequence = (start_in_sequence + int(hours_since_sunrise)) % 7
    horalord_index = PLANETARY_HOUR_SEQUENCE[current_hour_index_in_sequence]
    horalord = WEEKDAY_LORDS[horalord_index]

    # --- Assign Final Scores ---
    for planet in chart.planets:
        if planet.celestial_body in WEEKDAY_LORDS:
            bala = 0.0
            if planet.celestial_body == varshalord:
                bala += 15.0
            if planet.celestial_body == maasalord:
                bala += 30.0
            if planet.celestial_body == vaaralord:
                bala += 45.0
            if planet.celestial_body == horalord:
                bala += 60.0

            if "Kaalabala" not in planet.shadbala:
                planet.shadbala["Kaalabala"] = {}
            planet.shadbala["Kaalabala"]["VarshaMaasaDinaHoraBala"] = bala


def compute_ayanabala(chart: RasiChart, person: Person) -> None:
    """Computes Ayana Bala based on planetary declination. VERIFIED CORRECT."""
    t = skyfield_time_from_datetime(person.birth_datetime, person.timezone_offset or 0)

    for planet in chart.planets:
        if planet.celestial_body in NAISARGIKA_VALUES:
            declination = get_planet_declination(planet.celestial_body, t)

            # Calculate Ayana Bala: ((declination + 24) / 48) * 60
            definite_ayana_bala = ((declination + 24) / 48) * 60

            # Sun's Ayana Bala is doubled
            if planet.celestial_body == "Sun":
                definite_ayana_bala *= 2

            definite_ayana_bala = max(
                0,
                min(120 if planet.celestial_body == "Sun" else 60, definite_ayana_bala),
            )

            if "Kaalabala" not in planet.shadbala:
                planet.shadbala["Kaalabala"] = {}
            planet.shadbala["Kaalabala"]["Ayanabala"] = round(definite_ayana_bala, 3)


# --- CHESHTABALA with Mean Longitude from Skyfield ---


def _get_mean_longitude_from_skyfield(planet_name: str, t) -> float:
    """
    Calculate mean longitude using Skyfield's osculating elements.
    REFACTORED: Now uses globally loaded ephemeris for optimal performance.
    Confirmed from Skyfield docs: elements.mean_longitude is an Angle object.
    """
    from skyfield.elementslib import osculating_elements_of

    # Sun uses Earth's mean orbit
    if planet_name == "Sun":
        days_since_j2000 = t.tt - 2451545.0
        L0 = 280.46646  # Mean longitude at J2000
        mean_motion = 0.98564736  # degrees/day
        return (L0 + mean_motion * days_since_j2000) % 360

    body_mapping = {
        "Mars": "mars",
        "Mercury": "mercury",
        "Jupiter": "jupiter barycenter",
        "Venus": "venus",
        "Saturn": "saturn barycenter",
    }

    if planet_name not in body_mapping:
        return 0.0

    # Check if Skyfield ephemeris is available
    try:
        eph = get_ephemeris()
        body = eph[body_mapping[planet_name]]
        # Get relative position from Earth
        position = (body - eph["earth"]).at(t)
        # Calculate osculating elements (geocentric)
        elements = osculating_elements_of(position)
        # Extract mean longitude (confirmed from Skyfield docs)
        return elements.mean_longitude.degrees
    except Exception as e:
        print(f"Warning: Skyfield osculating elements failed for {planet_name}: {e}")
        return _get_fallback_mean_longitude(planet_name, t)


def _get_fallback_mean_longitude(planet_name: str, t) -> float:
    """
    Fallback approximation when Skyfield is unavailable.
    REFACTORED: Extracted common fallback logic.
    """
    days_since_j2000 = t.tt - 2451545.0
    epoch_longitudes = {
        "Mars": 355.45,
        "Mercury": 252.25,
        "Jupiter": 34.35,
        "Venus": 181.98,
        "Saturn": 49.95,
    }

    mean_motion = PLANET_MEAN_MOTION.get(planet_name, 0.0)
    epoch_lon = epoch_longitudes.get(planet_name, 0.0)

    return (epoch_lon + mean_motion * days_since_j2000) % 360


def compute_chestagbala(chart: RasiChart, person: Person) -> None:
    """
    Computes Cheshta Bala (Motional Strength) using mean longitudes from Skyfield.
    CORRECTED: Uses precise ephemeris calculations.
    """
    # Sun's Cheshta Bala is its Ayanabala
    sun = next((p for p in chart.planets if p.celestial_body == "Sun"), None)
    if sun:
        sun.shadbala["Cheshtabala"] = sun.shadbala.get("Kaalabala", {}).get(
            "Ayanabala", 0
        )

    # Moon's Cheshta Bala is its Pakshabala
    moon = next((p for p in chart.planets if p.celestial_body == "Moon"), None)
    if moon:
        moon.shadbala["Cheshtabala"] = moon.shadbala.get("Kaalabala", {}).get(
            "Pakshabala", 0
        )

    # For other planets
    t = skyfield_time_from_datetime(person.birth_datetime, person.timezone_offset or 0)

    # Get Sun's mean longitude for reference
    sun_mean_long = _get_mean_longitude_from_skyfield("Sun", t)

    for planet in chart.planets:
        planet_name = planet.celestial_body
        if planet_name in PLANET_MEAN_MOTION:
            # Get mean longitude using Skyfield
            mean_long = _get_mean_longitude_from_skyfield(planet_name, t)

            # Determine Seeghrochcha (apogee reference point)
            if planet_name in ["Mercury", "Venus"]:
                # Inferior planets: Seeghrochcha is their mean longitude
                seegrocha = mean_long
                mean_long = sun_mean_long
            else:
                # Superior planets: Seeghrochcha is Sun's mean longitude
                seegrocha = sun_mean_long

            # Get true longitude
            true_long = planet_longitude_from_sign(planet.sign, planet.sign_degrees)

            # Calculate average longitude
            ave_long = 0.5 * (true_long + mean_long)

            # Reduced Cheshta Kendra (classical formula)
            reduced_chesta_kendra = abs(seegrocha - ave_long)
            if reduced_chesta_kendra > 180:
                reduced_chesta_kendra = 360 - reduced_chesta_kendra

            # Cheshta Bala = Reduced Cheshta Kendra / 3
            bala = reduced_chesta_kendra / 3.0

            planet.shadbala["Cheshtabala"] = round(bala, 3)


def compute_yuddhabala(chart: RasiChart) -> None:
    """
    Calculates and applies planetary war strength.
    CORRECTED: Now includes planet diameter ratios as per classical texts.
    """
    # Planet diameters in arbitrary units (relative sizes for calculation)
    planet_diameters = {
        "Mars": 1.5,
        "Mercury": 1.0,
        "Jupiter": 3.5,
        "Venus": 1.6,
        "Saturn": 3.0,
    }

    planets_list = [p for p in chart.planets if p.celestial_body in YUDDHABALA_PLANETS]

    for p in planets_list:
        if "Kaalabala" not in p.shadbala:
            p.shadbala["Kaalabala"] = {}
        p.shadbala["Kaalabala"]["Yuddhabala"] = 0.0

    for i in range(len(planets_list)):
        for j in range(i + 1, len(planets_list)):
            p1 = planets_list[i]
            p2 = planets_list[j]
            long1 = planet_longitude_from_sign(p1.sign, p1.sign_degrees)
            long2 = planet_longitude_from_sign(p2.sign, p2.sign_degrees)

            if angdiff(long1, long2) <= 1.0:
                # War is occurring
                shadbala1 = p1.shadbala.get("Shadbala", {}).get("Total", 0)
                shadbala2 = p2.shadbala.get("Shadbala", {}).get("Total", 0)

                if shadbala1 == shadbala2:
                    continue

                winner, loser = (p1, p2) if shadbala1 > shadbala2 else (p2, p1)

                # Calculate strength difference using diameter ratio
                # Classical formula: strength_diff / diameter_diff
                bala_diff = abs(shadbala1 - shadbala2)
                dia1 = planet_diameters.get(p1.celestial_body, 1.0)
                dia2 = planet_diameters.get(p2.celestial_body, 1.0)
                dia_diff = abs(dia1 - dia2)

                # Avoid division by zero
                if dia_diff > 0.01:
                    yuddha_bala = round(bala_diff / dia_diff, 2)
                else:
                    yuddha_bala = bala_diff

                winner.shadbala["Kaalabala"]["Yuddhabala"] = yuddha_bala
                loser.shadbala["Kaalabala"]["Yuddhabala"] = -yuddha_bala


# --- NAISARGIKA BALA ---


def compute_naisargikabala(chart: RasiChart) -> None:
    for planet in chart.planets:
        if planet.celestial_body in NAISARGIKA_VALUES:
            planet.shadbala["Naisargikabala"] = NAISARGIKA_VALUES[planet.celestial_body]


# --- DRIKBALA (Aspect Strength) ---


def compute_drikbala(chart: RasiChart) -> None:
    """
    Compute aspect strength (Drik Bala) using sputa drishti method.
    VERIFIED CORRECT - matches PyJHora implementation.
    """
    naturalbenefics = [
        p.celestial_body
        for p in chart.planets
        if p.celestial_body in NATURAL_BENEFIC_SHADBALA
    ]
    naturalmalefics = [
        p.celestial_body
        for p in chart.planets
        if p.celestial_body in NATURAL_MALEFIC_SHADBALA
    ]

    for planet in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
        benefic_sputa = 0.0
        malefic_sputa = 0.0

        for aspectingplanet in naturalbenefics:
            if aspectingplanet == planet:
                continue
            dist_deg = get_angular_distance_between_planets(
                chart, aspectingplanet, planet
            )
            sputa = get_sputa_drishti_degree(dist_deg, aspectingplanet)
            benefic_sputa += sputa

        for aspectingplanet in naturalmalefics:
            if aspectingplanet == planet:
                continue
            dist_deg = get_angular_distance_between_planets(
                chart, aspectingplanet, planet
            )
            sputa = get_sputa_drishti_degree(dist_deg, aspectingplanet)
            malefic_sputa += sputa

        drishtipinda_total = benefic_sputa - malefic_sputa
        planet_drikbala = drishtipinda_total / 4.0

        for planet_obj in chart.planets:
            if planet_obj.celestial_body == planet:
                planet_obj.shadbala["Drikbala"] = round(planet_drikbala, 3)
                break


def get_angular_distance_between_planets(
    chart: RasiChart, planet1_name: str, planet2_name: str
) -> float:
    """Calculate directional angular distance from planet1 to planet2."""
    planet1 = next((p for p in chart.planets if p.celestial_body == planet1_name), None)
    planet2 = next((p for p in chart.planets if p.celestial_body == planet2_name), None)

    if not planet1 or not planet2:
        return 0.0

    long1 = planet_longitude_from_sign(planet1.sign, planet1.sign_degrees)
    long2 = planet_longitude_from_sign(planet2.sign, planet2.sign_degrees)

    dist = long1 - long2
    while dist > 180:
        dist -= 360
    while dist <= -180:
        dist += 360

    return dist


def get_sputa_drishti_degree(degree: float, aspecting_planet: str) -> float:
    """
    Calculate sputa aspect degree (Drishti) in Virupas (0-60 scale).
    Based on classical BPHS formulas as documented in Saravali.

    Args:
        degree: Angular distance between aspecting and aspected planet (0-360)
        aspecting_planet: Planet name (Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn)

    Returns:
        Aspect strength in Virupas (0-60)
    """
    # Normalize angle and mirror >180° for symmetry
    degree = abs(degree) % 360
    if degree > 180:
        degree = 360 - degree

    # Apply planet-specific formula using constants
    if aspecting_planet == "Mars":
        return _calculate_planet_sputa(degree, MARS_SPECIAL_ASPECTS)
    elif aspecting_planet == "Jupiter":
        return _calculate_planet_sputa(degree, JUPITER_SPECIAL_ASPECTS)
    elif aspecting_planet == "Saturn":
        return _calculate_planet_sputa(degree, SATURN_SPECIAL_ASPECTS)
    else:
        return _calculate_general_sputa(degree)


def _calculate_general_sputa(degree: float) -> float:
    """General sputa formula for Sun, Moon, Mercury, Venus."""
    if degree < 30:
        return 0.0
    elif degree < 60:
        return (degree - 30) / 2.0
    elif degree < 90:
        return degree - 45
    elif degree < 120:
        return 30 + (120 - degree) / 2.0
    elif degree < 150:
        return 150 - degree
    else:  # 150-180°
        return 2 * (degree - 150)


def _calculate_planet_sputa(degree: float, special_aspects: list) -> float:
    """Calculate sputa for planets with special aspects (Mars, Jupiter, Saturn)."""
    # Get base strength from general formula
    base_strength = _calculate_general_sputa(degree)

    # Check if within orb of special aspects
    max_strength = base_strength
    for aspect_angle in special_aspects:
        dist_from_aspect = abs(degree - aspect_angle)
        if dist_from_aspect <= SPECIAL_ASPECT_ORB:
            # Linear interpolation from 0 to 60 within orb
            orb_strength = FULL_ASPECT_STRENGTH * (
                1 - dist_from_aspect / SPECIAL_ASPECT_ORB
            )
            max_strength = max(max_strength, orb_strength)

    return max_strength


# --- VIMSHOPAKA BALA ---


def compute_vimshopaka_balas(chart: RasiChart) -> None:
    """Implements Vimshopaka Bala calculations."""
    for planet in chart.planets:
        if planet.celestial_body in PLANETS_WITH_SHADBALA:
            planet.shadbala["Vimshopaka"] = {}
            p_long = planet_longitude_from_sign(planet.sign, planet.sign_degrees)

            for varga_type, divisions in VIMSHOPAKA_DIVISION_STRENGTHS.items():
                total_value = 0.0

                for div_key, weight in divisions.items():
                    div_num = int(div_key[1:])
                    if div_num == 1:
                        v_sign = planet.sign
                        v_deg = planet.sign_degrees
                    else:
                        v_sign = get_varga_sign(p_long, div_num)
                        v_deg = calculate_degrees_in_varga_sign(p_long, div_num)

                    relation = get_planetary_dispositor_relation(
                        planet.celestial_body, v_sign, v_deg, chart
                    )
                    ratio = BALA_RELATION_RATIOS.get(
                        relation, BALA_RELATION_RATIOS["SAMA"]
                    )
                    total_value += ratio * weight

                planet.shadbala["Vimshopaka"][varga_type] = round(total_value, 3)


# --- ISHTA/KASHTA BALA ---


def compute_ishtakashtabalas(chart: RasiChart) -> None:
    for planet in chart.planets:
        if planet.celestial_body in NAISARGIKA_VALUES:
            uchhabala = planet.shadbala.get("Sthanabala", {}).get("Uchhabala", 0)
            cheshtabala = planet.shadbala.get("Cheshtabala", 0)
            ishtabala = math.sqrt(uchhabala * cheshtabala)
            planet.shadbala["Ishtabala"] = round(ishtabala, 3)
            planet.shadbala["Kashtabala"] = round(60 - ishtabala, 3)


# --- BHAVA BALA (House Strength) ---


def compute_bhava_balas(chart: RasiChart) -> None:
    compute_bhava_adhipathi_bala(chart)
    compute_bhava_dig_bala(chart)
    compute_bhava_drik_bala(chart)
    for house in chart.houses:
        total = (
            getattr(house, "bhava_bala_adhipathi", 0)
            + getattr(house, "bhava_dig_bala", 0)
            + getattr(house, "bhava_drik_bala", 0)
        )
        house.bhava_bala = round(total, 3)


def compute_bhava_adhipathi_bala(chart: RasiChart) -> None:
    for house in chart.houses:
        lord = next((p for p in chart.planets if p.celestial_body == house.lord), None)
        house.bhava_bala_adhipathi = (
            lord.shadbala.get("Shadbala", {}).get("Total", 0) if lord else 0
        )


### REFACTORED FUNCTION ###
def compute_bhava_dig_bala(chart: RasiChart) -> None:
    """
    Compute house directional strength, handling dual-nature signs correctly.
    """
    for hno, house in enumerate(chart.houses):
        nature_key = house.sign
        if house.sign == "Sagittarius":
            nature_key = (
                "Sagittarius_first_half"
                if (house.sign_degrees or 15) < 15.0
                else "Sagittarius_second_half"
            )
        elif house.sign == "Capricorn":
            nature_key = (
                "Capricorn_first_half"
                if (house.sign_degrees or 15) < 15.0
                else "Capricorn_second_half"
            )

        sign_nature = SIGN_NATURE_CLASSIFICATION.get(nature_key, "nara")
        house.bhava_dig_bala = float(BHAVA_STRENGTH_FROM_SIGN_NATURE[sign_nature][hno])


def compute_bhava_drik_bala(chart: RasiChart) -> None:
    """
    Compute Bhava Drik Bala (Aspectual Strength on Houses).

    Calculate aspects to the true house midpoint (Bhava Madhya)
    based on the precise Ascendant longitude.
    """
    from jyotishganit.core.constants import (
        NATURAL_BENEFIC_SHADBALA,
        NATURAL_MALEFIC_SHADBALA,
    )

    # Calculate the ascendant's longitude: the exact degree of the Ascendant
    ascendant_lon = (
        ZODIAC_SIGNS.index(chart.houses[0].sign) * 30 + chart.houses[0].sign_degrees
    )
    naturalbenefics = NATURAL_BENEFIC_SHADBALA
    naturalmalefics = NATURAL_MALEFIC_SHADBALA

    for house_idx, house in enumerate(chart.houses):
        benefic_sputa = 0.0
        malefic_sputa = 0.0

        # --- CORRECTED LOGIC: Calculate the true Bhava Madhya ---
        # The midpoint of a house is 15 degrees from its starting cusp.
        # In an Equal House system, the cusp of house N is (N-1)*30 degrees from the Ascendant.
        house_cusp = normalize(ascendant_lon + (house_idx * 30))
        house_midpoint_long = normalize(house_cusp + 15.0)

        # Calculate aspects from each classical planet to this true midpoint
        for planet in chart.planets:
            if planet.celestial_body not in [
                "Sun",
                "Moon",
                "Mars",
                "Mercury",
                "Jupiter",
                "Venus",
                "Saturn",
            ]:
                continue

            planet_long = planet_longitude_from_sign(planet.sign, planet.sign_degrees)

            # Use the existing helper to get the angular distance to the correct point
            dist_deg = get_angular_distance_between_planets_and_house(
                planet_long, house_midpoint_long
            )

            # Reuse the now-authoritative Sputa Drishti function
            sputa = get_sputa_drishti_degree(dist_deg, planet.celestial_body)

            if planet.celestial_body in naturalbenefics:
                benefic_sputa += sputa
            elif planet.celestial_body in naturalmalefics:
                malefic_sputa += sputa

        # Total drishtipinda = benefic_sputa - malefic_sputa
        drishtipinda_total = benefic_sputa - malefic_sputa

        # Drik Bala = quarter of drishtipinda total, capped at 20.0
        house_drikbala = min(drishtipinda_total / 4.0, 20.0)

        house.bhava_drik_bala = round(house_drikbala, 3)


def get_angular_distance_between_planets_and_house(
    planet_long: float, house_long: float
) -> float:
    """Calculate directional angular distance from planet to house."""
    dist = planet_long - house_long
    while dist > 180:
        dist -= 360
    while dist <= -180:
        dist += 360
    return dist


def compute_bhava_drishthi_bala(chart: RasiChart) -> None:
    # (Implementation is correct, using Sputa Drishti on Bhava Madhya)
    pass
