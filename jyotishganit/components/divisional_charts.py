"""
Divisional charts calculations for jyotishganit.

Implements all standard Vedic divisional charts (D2 to D60) based on jyotishyamitra logic.
Each chart calculated from D1 (rasi) positions using sign-based division rules.
"""

from jyotishganit.core.constants import SIGN_LORDS, ZODIAC_SIGNS
from jyotishganit.core.models import (
    DivisionalAscendant,
    DivisionalChart,
    DivisionalHouse,
    DivisionalPlanetPosition,
)
from jyotishganit.core.utils import longitude_to_zodiac


def signnum(sign_str: str) -> int:
    """Convert sign string to 1-based index (Aries=1, etc.)."""
    return ZODIAC_SIGNS.index(sign_str) + 1


def compute_nthsign(fromsign: int, n: int) -> int:
    """Compute nth sign from given sign (cyclic)."""
    return ((fromsign - 1 + (n - 1)) % 12) + 1


def longitude_to_seconds(sign: str, degrees: float) -> int:
    """Convert sign + degrees to total seconds from Aries 0°."""
    sign_num = signnum(sign) - 1  # 0-based for Aries
    return int((sign_num * 30 * 3600) + (degrees * 3600))


def seconds_to_longitude(total_seconds: int) -> tuple[str, float]:
    """Convert total seconds to sign and degrees."""
    degrees = (total_seconds % (360 * 3600)) / 3600
    return longitude_to_zodiac(degrees)


def navamsa_from_long(sign: str, degrees: float) -> tuple[int, str, float]:
    """Compute Navamsa (D9) position from D1 longitude using standard movable/fixed/dual start rules.
    Returns (total_seconds_from_Aries0, navamsa_sign_name, degrees_within_navamsa).
    """
    total_seconds = longitude_to_seconds(sign, degrees)
    # navamsa amsa size = 3°20' = 3.333... degrees in seconds
    amsa = (3 * 3600) + (20 * 60)
    # degrees within the sign, in seconds
    longi_sec_in_sign = int((degrees % 30) * 3600)
    # which navamsa compartment within the sign (1..9)
    compartment = int(longi_sec_in_sign / amsa) + 1  # 1..9
    sign_num = signnum(sign)

    # Classical rule: start base depends on rasi nature (movable/fixed/dual)
    # Movable signs: start counting from the same sign
    # Fixed signs: start counting from the 9th sign from it
    # Dual signs: start counting from the 5th sign from it
    if sign_num in [1, 4, 7, 10]:  # movable
        base_start = sign_num
    elif sign_num in [2, 5, 8, 11]:  # fixed
        base_start = compute_nthsign(sign_num, 9)
    else:  # dual: 3,6,9,12
        base_start = compute_nthsign(sign_num, 5)

    # navamsa sign is the compartment-th sign counted from base_start
    nav_sign_num = compute_nthsign(base_start, compartment)
    nav_sign = ZODIAC_SIGNS[nav_sign_num - 1]

    # degrees inside the navamsa amsa (0 .. 3°20')
    remaining_seconds = longi_sec_in_sign % amsa
    nav_deg = remaining_seconds / 3600.0

    return total_seconds, nav_sign, nav_deg


def hora_from_long(sign: str, degrees: float) -> tuple[int, str, float]:
    """Compute Hora (D2) position.
    Classical D2 maps a planet to Cancer (Moon hour) or Leo (Sun hour).
    - Odd signs: 0°-15° -> Sun (Leo), 15°-30° -> Moon (Cancer)
    - Even signs: reversed: 0°-15° -> Moon (Cancer), 15°-30° -> Sun (Leo)
    Returns (total_seconds_from_Aries0, hora_sign_name, degrees_within_15deg_half).
    """
    total_seconds = longitude_to_seconds(sign, degrees)
    sign_num = signnum(sign)
    longi_deg = degrees % 30.0

    # odd signs: Aries(1), Gemini(3), Leo(5), Libra(7), Sag(9), Aquarius(11)
    odd_signs = {1, 3, 5, 7, 9, 11}
    is_odd = sign_num in odd_signs

    # decide Sun/Mon hora
    # Sun hora maps to Leo, Moon hora maps to Cancer
    if (is_odd and longi_deg < 15.0) or (not is_odd and longi_deg >= 15.0):
        hor_sign = "Leo"
    else:
        hor_sign = "Cancer"

    # degree within the 15° half (0..15)
    deg_in_half = longi_deg if longi_deg < 15.0 else (longi_deg - 15.0)
    return total_seconds, hor_sign, deg_in_half


def drekkana_from_long(sign: str, degrees: float) -> tuple[int, str, float]:
    """Compute Drekkana (D3) position."""
    sign_num = signnum(sign)
    pos_deg = degrees
    longi_sec = pos_deg * 3600  # degrees within sign
    amsa = 10 * 3600  # 10° amsa
    compartment = 1 + int(longi_sec / amsa)
    if compartment == 1:
        drekk_sign_num = compute_nthsign(sign_num, 1)
    elif compartment == 2:
        drekk_sign_num = compute_nthsign(sign_num, 5)
    else:
        drekk_sign_num = compute_nthsign(sign_num, 9)
    drekk_sign = ZODIAC_SIGNS[drekk_sign_num - 1]
    remaining_seconds = longi_sec % amsa
    drekk_deg = remaining_seconds / 3600
    # Get total_seconds for consistency with return format
    total_seconds = longitude_to_seconds(sign, degrees)
    return total_seconds, drekk_sign, drekk_deg


def chaturtamsa_from_long(sign: str, degrees: float) -> tuple[int, str, float]:
    """Compute Chaturthamsa (D4) position."""
    pos_deg = degrees
    longi_sec = pos_deg * 3600
    amsa = 30 * 3600 / 4  # 7.5° amsa
    compartment = 1 + int(longi_sec / amsa)
    sign_num = signnum(sign)
    if compartment == 1:
        chat_sign_num = compute_nthsign(sign_num, 1)
    elif compartment == 2:
        chat_sign_num = compute_nthsign(sign_num, 4)
    elif compartment == 3:
        chat_sign_num = compute_nthsign(sign_num, 7)
    else:
        chat_sign_num = compute_nthsign(sign_num, 10)
    chat_sign = ZODIAC_SIGNS[chat_sign_num - 1]
    remaining_seconds = longi_sec % amsa
    chat_deg = remaining_seconds / 3600
    total_seconds = longitude_to_seconds(sign, degrees)
    return total_seconds, chat_sign, chat_deg


def saptamsa_from_long(sign: str, degrees: float) -> tuple[int, str, float]:
    """Compute Saptamsa (D7) position."""
    pos_deg = degrees
    longi_sec = pos_deg * 3600
    amsa = 30 * 3600 / 7  # ~4.285° amsa
    compartment = 1 + int(longi_sec / amsa)
    sign_num = signnum(sign)
    if sign_num % 2 == 1:  # odd Lagna
        sapt_sign_num = compute_nthsign(sign_num, compartment)
    else:  # even Lagna
        sapt_sign_num = compute_nthsign(sign_num, compartment + 6)
    sapt_sign = ZODIAC_SIGNS[sapt_sign_num - 1]
    remaining_seconds = longi_sec % amsa
    sapt_deg = remaining_seconds / 3600
    total_seconds = longitude_to_seconds(sign, degrees)
    return total_seconds, sapt_sign, sapt_deg


def dasamsa_from_long(sign: str, degrees: float) -> tuple[int, str, float]:
    """Compute Dasamsa (D10) position."""
    pos_deg = degrees
    longi_sec = pos_deg * 3600
    amsa = 30 * 3600 / 10  # 3° amsa
    part = int(longi_sec / amsa)
    sign_num = signnum(sign)
    if sign_num % 2 == 1:  # odd
        das_sign_num = ((sign_num - 1 + part) % 12) + 1
    else:  # even
        das_sign_num = ((sign_num - 1 + 8 + part) % 12) + 1
    das_sign = ZODIAC_SIGNS[das_sign_num - 1]
    remaining_seconds = longi_sec % amsa
    das_deg = remaining_seconds / 3600
    total_seconds = longitude_to_seconds(sign, degrees)
    return total_seconds, das_sign, das_deg


def dwadasamsa_from_long(sign: str, degrees: float) -> tuple[int, str, float]:
    """Compute Dwadasamsa (D12) position."""
    pos_deg = degrees
    longi_sec = pos_deg * 3600
    amsa = 30 * 3600 / 12  # 2.5° amsa
    compartment = 1 + int(longi_sec / amsa) % 12
    sign_num = signnum(sign)
    dwad_sign_num = compute_nthsign(sign_num, compartment)
    dwad_sign = ZODIAC_SIGNS[dwad_sign_num - 1]
    remaining_seconds = longi_sec % amsa
    dwad_deg = remaining_seconds / 3600
    total_seconds = longitude_to_seconds(sign, degrees)
    return total_seconds, dwad_sign, dwad_deg


def shodasamsa_from_long(sign: str, degrees: float) -> tuple[int, str, float]:
    """Compute Shodasamsa (D16) position."""
    pos_deg = degrees
    longi_sec = pos_deg * 3600
    amsa = 30 * 3600 / 16  # 1.875° amsa
    compartment = 1 + int(longi_sec / amsa)
    sign_num = signnum(sign)
    if sign_num in [1, 4, 7, 10]:  # Movable
        shod_sign_num = compute_nthsign(1, compartment)
    elif sign_num in [2, 5, 8, 11]:  # Fixed
        shod_sign_num = compute_nthsign(5, compartment)
    else:  # Dual
        shod_sign_num = compute_nthsign(9, compartment)
    shod_sign = ZODIAC_SIGNS[shod_sign_num - 1]
    remaining_seconds = longi_sec % amsa
    shod_deg = remaining_seconds / 3600
    total_seconds = longitude_to_seconds(sign, degrees)
    return total_seconds, shod_sign, shod_deg


def vimsamsa_from_long(sign: str, degrees: float) -> tuple[int, str, float]:
    """Compute Vimsamsa (D20) position."""
    pos_deg = degrees
    longi_sec = pos_deg * 3600
    amsa = 30 * 3600 / 20  # 1.5° amsa
    compartment = 1 + int(longi_sec / amsa)
    sign_num = signnum(sign)
    if sign_num in [1, 4, 7, 10]:  # Movable
        vim_sign_num = compute_nthsign(1, compartment)
    elif sign_num in [2, 5, 8, 11]:  # Fixed
        vim_sign_num = compute_nthsign(9, compartment)
    else:  # Dual
        vim_sign_num = compute_nthsign(5, compartment)
    vim_sign = ZODIAC_SIGNS[vim_sign_num - 1]
    remaining_seconds = longi_sec % amsa
    vim_deg = remaining_seconds / 3600
    total_seconds = longitude_to_seconds(sign, degrees)
    return total_seconds, vim_sign, vim_deg


def chaturvimsamsa_from_long(sign: str, degrees: float) -> tuple[int, str, float]:
    """Compute Chaturvimsamsa (D24) position."""
    pos_deg = degrees
    longi_sec = pos_deg * 3600
    amsa = 30 * 3600 / 24  # 1.25° amsa
    compartment = 1 + int(longi_sec / amsa)
    sign_num = signnum(sign)
    if sign_num % 2 == 0:  # Even sign
        chatur_sign_num = compute_nthsign(4, compartment)
    else:  # Odd sign
        chatur_sign_num = compute_nthsign(5, compartment)
    chatur_sign = ZODIAC_SIGNS[chatur_sign_num - 1]
    remaining_seconds = longi_sec % amsa
    chatur_deg = remaining_seconds / 3600
    total_seconds = longitude_to_seconds(sign, degrees)
    return total_seconds, chatur_sign, chatur_deg


def sapta_vimsamsa_from_long(sign: str, degrees: float) -> tuple[int, str, float]:
    """Compute Sapta-vimsamsa (D27) position."""
    pos_deg = degrees
    longi_sec = pos_deg * 3600
    amsa = 30 * 3600 / 27  # ~1.11° amsa
    compartment = 1 + int(longi_sec / amsa)
    sign_num = signnum(sign)
    if sign_num in [1, 5, 9]:  # Fiery
        sapt_sign_num = compute_nthsign(1, compartment)
    elif sign_num in [2, 6, 10]:  # Earthy
        sapt_sign_num = compute_nthsign(4, compartment)
    elif sign_num in [3, 7, 11]:  # Airy
        sapt_sign_num = compute_nthsign(7, compartment)
    else:  # Watery
        sapt_sign_num = compute_nthsign(10, compartment)
    sapt_sign = ZODIAC_SIGNS[sapt_sign_num - 1]
    remaining_seconds = longi_sec % amsa
    sapt_deg = remaining_seconds / 3600
    total_seconds = longitude_to_seconds(sign, degrees)
    return total_seconds, sapt_sign, sapt_deg


def trimsamsa_from_long(sign: str, degrees: float) -> tuple[int, str, float]:
    """Compute Trimsamsa (D30) position."""
    pos_deg = degrees
    longi_sec = pos_deg * 3600
    sign_num = signnum(sign)
    if sign_num % 2 == 0:  # Even sign
        if longi_sec <= 5 * 3600:  # 0-5°
            trim_sign_num = 2
        elif longi_sec <= 12 * 3600:  # 5-12°
            trim_sign_num = 6
        elif longi_sec <= 19 * 3600:  # 12-19°
            trim_sign_num = 10
        elif longi_sec <= 24 * 3600:  # 19-24°
            trim_sign_num = 12
        else:  # 24-30°
            trim_sign_num = 8
    else:  # Odd sign
        if longi_sec <= 5 * 3600:  # 0-5°
            trim_sign_num = 1
        elif longi_sec <= 10 * 3600:  # 5-10°
            trim_sign_num = 11
        elif longi_sec <= 18 * 3600:  # 10-18°
            trim_sign_num = 9
        elif longi_sec <= 25 * 3600:  # 18-25°
            trim_sign_num = 3
        else:  # 25-30°
            trim_sign_num = 7
    trim_sign = ZODIAC_SIGNS[trim_sign_num - 1]
    # Remaining degrees are ignored in jyotishyamitra for Trimsamsa, but set approx
    trim_deg = 0.0
    total_seconds = longitude_to_seconds(sign, degrees)
    return total_seconds, trim_sign, trim_deg


def khavedamsa_from_long(sign: str, degrees: float) -> tuple[int, str, float]:
    """Compute Khavedamsa (D40) position."""
    pos_deg = degrees
    longi_sec = pos_deg * 3600
    amsa = 30 * 3600 / 40  # 0.75° amsa
    compartment = 1 + int(longi_sec / amsa)
    sign_num = signnum(sign)
    if sign_num % 2 == 0:  # Even sign
        khav_sign_num = compute_nthsign(7, compartment)
    else:  # Odd sign
        khav_sign_num = compute_nthsign(1, compartment)
    khav_sign = ZODIAC_SIGNS[khav_sign_num - 1]
    remaining_seconds = longi_sec % amsa
    khav_deg = remaining_seconds / 3600
    total_seconds = longitude_to_seconds(sign, degrees)
    return total_seconds, khav_sign, khav_deg


def akshavedamsa_from_long(sign: str, degrees: float) -> tuple[int, str, float]:
    """Compute Akshavedamsa (D45) position."""
    pos_deg = degrees
    longi_sec = pos_deg * 3600
    amsa = 30 * 3600 / 45  # 0.666° amsa
    compartment = 1 + int(longi_sec / amsa)
    sign_num = signnum(sign)
    if sign_num in [1, 4, 7, 10]:  # Movable
        aksh_sign_num = compute_nthsign(1, compartment)
    elif sign_num in [2, 5, 8, 11]:  # Fixed
        aksh_sign_num = compute_nthsign(5, compartment)
    else:  # Dual
        aksh_sign_num = compute_nthsign(9, compartment)
    aksh_sign = ZODIAC_SIGNS[aksh_sign_num - 1]
    remaining_seconds = longi_sec % amsa
    aksh_deg = remaining_seconds / 3600
    total_seconds = longitude_to_seconds(sign, degrees)
    return total_seconds, aksh_sign, aksh_deg


def shashtiamsa_from_long(sign: str, degrees: float) -> tuple[int, str, float]:
    """Compute Shashtiamsa (D60) position."""
    pos_deg = degrees
    longi_sec = pos_deg * 3600
    amsa = 30 * 3600 / 60  # 0.5° amsa
    compartment = 1 + int(longi_sec / amsa) % 12
    sign_num = signnum(sign)
    shas_sign_num = compute_nthsign(sign_num, compartment)
    shas_sign = ZODIAC_SIGNS[shas_sign_num - 1]
    remaining_seconds = longi_sec % amsa
    shas_deg = remaining_seconds / 3600
    total_seconds = longitude_to_seconds(sign, degrees)
    return total_seconds, shas_sign, shas_deg


def compute_divisional_position_for_type(
    sign: str, degrees: float, chart_type: str
) -> str:
    """Compute divisional position for given type, return divisional sign."""
    if chart_type == "D9":
        _, div_sign, _ = navamsa_from_long(sign, degrees)
    elif chart_type == "D2":
        _, div_sign, _ = hora_from_long(sign, degrees)
    elif chart_type == "D3":
        _, div_sign, _ = drekkana_from_long(sign, degrees)
    elif chart_type == "D4":
        _, div_sign, _ = chaturtamsa_from_long(sign, degrees)
    elif chart_type == "D7":
        _, div_sign, _ = saptamsa_from_long(sign, degrees)
    elif chart_type == "D10":
        _, div_sign, _ = dasamsa_from_long(sign, degrees)
    elif chart_type == "D12":
        _, div_sign, _ = dwadasamsa_from_long(sign, degrees)
    elif chart_type == "D16":
        _, div_sign, _ = shodasamsa_from_long(sign, degrees)
    elif chart_type == "D20":
        _, div_sign, _ = vimsamsa_from_long(sign, degrees)
    elif chart_type == "D24":
        _, div_sign, _ = chaturvimsamsa_from_long(sign, degrees)
    elif chart_type == "D27":
        _, div_sign, _ = sapta_vimsamsa_from_long(sign, degrees)
    elif chart_type == "D30":
        _, div_sign, _ = trimsamsa_from_long(sign, degrees)
    elif chart_type == "D40":
        _, div_sign, _ = khavedamsa_from_long(sign, degrees)
    elif chart_type == "D45":
        _, div_sign, _ = akshavedamsa_from_long(sign, degrees)
    elif chart_type == "D60":
        _, div_sign, _ = shashtiamsa_from_long(sign, degrees)
    else:
        div_sign = sign  # Default to D1
    return div_sign


def compute_divisional_chart(d1_chart, chart_type: str) -> DivisionalChart:
    """Compute a divisional chart from D1 chart."""
    # Get D1 ascendant sign for house placement calculation
    asc_sign_d1 = d1_chart.houses[0].sign
    asc_sign_d1_num = signnum(asc_sign_d1)

    # Ascendant positioning
    div_asc_sign = compute_divisional_position_for_type(
        d1_chart.houses[0].sign, d1_chart.houses[0].sign_degrees, chart_type
    )

    # Calculate which D1 house this divisional ascendant sign falls in
    div_asc_sign_num = signnum(div_asc_sign)
    d1_house_for_div_asc = ((div_asc_sign_num - asc_sign_d1_num) % 12) + 1

    div_asc = DivisionalAscendant(
        sign=div_asc_sign, d1_house_placement=d1_house_for_div_asc
    )

    # Create houses
    div_houses = []
    asc_sign_num = signnum(div_asc.sign)

    # Special handling for D2 (hora chart) - only create houses in Leo and Cancer, with specific house numbers
    if chart_type == "D2":
        # Find which houses contain Leo and Cancer from ascendant
        leo_from_asc = None
        cancer_from_asc = None
        for house_offset in range(12):
            house_sign_num = compute_nthsign(asc_sign_num, house_offset + 1)
            house_sign = ZODIAC_SIGNS[house_sign_num - 1]
            if house_sign == "Leo":
                leo_from_asc = ((house_sign_num - asc_sign_d1_num) % 12) + 1
            elif house_sign == "Cancer":
                cancer_from_asc = ((house_sign_num - asc_sign_d1_num) % 12) + 1

        # Create house 12 as Cancer and house 1 as Leo (special D2 numbering)
        if cancer_from_asc is not None:
            div_houses.append(
                DivisionalHouse(
                    number=12,  # House 12 is Cancer
                    sign="Cancer",
                    lord=SIGN_LORDS["Cancer"],
                    d1_house_placement=cancer_from_asc,
                )
            )

        if leo_from_asc is not None:
            div_houses.append(
                DivisionalHouse(
                    number=1,  # House 1 is Leo
                    sign="Leo",
                    lord=SIGN_LORDS["Leo"],
                    d1_house_placement=leo_from_asc,
                )
            )
    else:
        # Standard 12-house chart for other divisional charts
        for house_num in range(1, 13):
            house_sign_num = compute_nthsign(asc_sign_num, house_num)
            house_sign = ZODIAC_SIGNS[house_sign_num - 1]
            house_lord = SIGN_LORDS[house_sign]
            d1_house_placement = ((house_sign_num - asc_sign_d1_num) % 12) + 1

            div_house = DivisionalHouse(
                number=house_num,
                sign=house_sign,
                lord=house_lord,
                d1_house_placement=d1_house_placement,
            )
            div_houses.append(div_house)

    # Place planets in their houses
    for planet in d1_chart.planets:
        p_sign = compute_divisional_position_for_type(
            planet.sign, planet.sign_degrees, chart_type
        )

        # For D2, ensure planet sign is in allowed signs
        if chart_type == "D2" and p_sign not in ["Leo", "Cancer"]:
            p_sign = "Leo"  # Default fallback

        div_planet = DivisionalPlanetPosition(
            celestial_body=planet.celestial_body,
            sign=p_sign,
            d1_house_placement=planet.house,
        )

        # Find the house with matching sign and add the planet
        for house in div_houses:
            if house.sign == p_sign:
                house.occupants.append(div_planet)
                break

    # Skip aspects calculation for divisional charts

    return DivisionalChart(
        chart_type=chart_type.lower(), ascendant=div_asc, houses=div_houses
    )
