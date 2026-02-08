"""
Vimshottari Dasha calculations for jyotishganit. (CORRECTED VERSION)

Calculates Vimshottari Dasha periods with mahadasha, antardasha, and pratyantardashas levels.
This version fixes fundamental errors in constants and calculation formulas.
"""

from collections import OrderedDict
from datetime import datetime, timedelta
from typing import Any

from jyotishganit.core.astronomical import (
    calculate_ayanamsa,
    get_ephemeris,
    skyfield_time_from_datetime,
)
from jyotishganit.core.constants import (
    HUMAN_LIFE_SPAN_FOR_VIMSHOTTARI,
    VIMSHOTTARI_ADHIPATI_LIST,
    VIMSHOTTARI_DASHA_DURATIONS,
    YEAR_DURATION_DAYS,
)
from jyotishganit.core.models import Dashas


def _get_moon_nakshatra_at_birth(t, ayanamsa: float) -> tuple[int, float]:
    """Calculate Moon's nakshatra and position within it at birth."""
    eph = get_ephemeris()
    pos = eph["earth"].at(t).observe(eph["moon"]).apparent()
    _, lon, _ = pos.ecliptic_latlon()
    moon_lon_tropical = lon.degrees

    moon_lon_sidereal = (moon_lon_tropical - ayanamsa) % 360

    nakshatra_span = 360.0 / 27.0
    nak_index = int(moon_lon_sidereal / nakshatra_span)
    remainder_degrees = moon_lon_sidereal % nakshatra_span

    return nak_index, remainder_degrees


def calculate_dasha_start_date(
    birth_datetime: datetime, timezone_offset: float, ayanamsa: float
) -> tuple[str, datetime]:
    """
    CORRECTED: Calculate the start date and lord of the mahadasa active at birth.
    """
    t = skyfield_time_from_datetime(birth_datetime, timezone_offset)
    nak_index, remainder_degs = _get_moon_nakshatra_at_birth(t, ayanamsa)

    # Correctly determine the dasha lord from the 9-planet sequence
    lord_index = nak_index % len(VIMSHOTTARI_ADHIPATI_LIST)
    lord = VIMSHOTTARI_ADHIPATI_LIST[lord_index]

    nakshatra_span = 360.0 / 27.0
    total_dasha_years = VIMSHOTTARI_DASHA_DURATIONS[lord]
    total_dasha_days = total_dasha_years * YEAR_DURATION_DAYS

    # Calculate elapsed portion based on moon's travel within the nakshatra
    elapsed_percentage = remainder_degs / nakshatra_span
    elapsed_days = total_dasha_days * elapsed_percentage

    dasha_start_date = birth_datetime - timedelta(days=elapsed_days)

    return lord, dasha_start_date


def get_next_adhipati(current_lord: str, direction: int = 1) -> str:
    """Returns the next lord in the CORRECT 9-planet Vimshottari sequence."""
    current_index = VIMSHOTTARI_ADHIPATI_LIST.index(current_lord)
    next_index = (current_index + direction) % len(VIMSHOTTARI_ADHIPATI_LIST)
    return VIMSHOTTARI_ADHIPATI_LIST[next_index]


def _generate_sub_periods(
    parent_lord: str,
    parent_start_date: datetime,
    parent_duration_days: float,
    current_level: int,
    max_depth: int,
) -> OrderedDict[str, Any]:
    """
    Generate nested sub-periods with proper naming:
    - Level 2: antardashas
    - Level 3: pratyantardashas
    """
    if current_level > max_depth:
        return OrderedDict()

    # Level name mapping
    level_names = {2: "antardashas", 3: "pratyantardashas"}

    sub_periods = OrderedDict()
    current_sub_period_start = parent_start_date

    # Sequence of sub-lords always starts from the parent lord
    sub_lord = parent_lord

    for _ in range(len(VIMSHOTTARI_ADHIPATI_LIST)):
        # CORRECT FORMULA: Sub_Period = Parent_Period * (Sub_Lord_Duration / 120)
        sub_period_duration_days = parent_duration_days * (
            VIMSHOTTARI_DASHA_DURATIONS[sub_lord] / HUMAN_LIFE_SPAN_FOR_VIMSHOTTARI
        )

        sub_period_end_date = current_sub_period_start + timedelta(
            days=sub_period_duration_days
        )

        sub_period_data: dict[str, Any] = {
            "start": current_sub_period_start,
            "end": sub_period_end_date,
        }

        # Generate next level if requested
        if current_level + 1 <= max_depth and current_level + 1 in level_names:
            next_level_name = level_names[current_level + 1]
            sub_period_data[next_level_name] = _generate_sub_periods(
                sub_lord,
                current_sub_period_start,
                sub_period_duration_days,
                current_level + 1,
                max_depth,
            )

        sub_periods[sub_lord] = sub_period_data

        current_sub_period_start = sub_period_end_date
        sub_lord = get_next_adhipati(sub_lord)

    return sub_periods


def _extract_current_periods(
    all_periods: dict[str, Any], current_datetime: datetime
) -> dict[str, Any]:
    """
    Extracts the currently active mahadasha, antardasha, and pratyantardasha
    in the same nested structure as 'all_periods'.
    """
    current_structure: dict[str, Any] = {"mahadashas": OrderedDict()}
    mahadashas = all_periods.get("mahadashas", {})

    for md_lord, md_data in mahadashas.items():
        if md_data["start"] <= current_datetime < md_data["end"]:
            # Found current Mahadasha
            current_md = {
                "start": md_data["start"],
                "end": md_data["end"],
                "antardashas": OrderedDict(),
            }

            antardashas = md_data.get("antardashas", {})
            for ad_lord, ad_data in antardashas.items():
                if ad_data["start"] <= current_datetime < ad_data["end"]:
                    # Found current Antardasha
                    current_ad = {
                        "start": ad_data["start"],
                        "end": ad_data["end"],
                        "pratyantardashas": OrderedDict(),
                    }

                    pratyantardashas = ad_data.get("pratyantardashas", {})
                    for pd_lord, pd_data in pratyantardashas.items():
                        if pd_data["start"] <= current_datetime < pd_data["end"]:
                            # Found current Pratyantardasha
                            current_pd = {
                                "start": pd_data["start"],
                                "end": pd_data["end"],
                            }
                            current_ad["pratyantardashas"][pd_lord] = current_pd
                            break  # Found PD, no need to check others in this AD

                    current_md["antardashas"][ad_lord] = current_ad
                    break  # Found AD, no need to check others in this MD

            current_structure["mahadashas"][md_lord] = current_md
            break  # Found MD, no need to check other MDs

    return current_structure


def _extract_upcoming_periods(
    all_periods: dict[str, Any], current_datetime: datetime
) -> dict[str, Any]:
    """
    Extracts the next 3 antardashas, potentially crossing mahadasha boundaries,
    starting from the end of the current antardasha.
    """
    flat_antardashas: list[Any] = []
    mahadashas = all_periods.get("mahadashas", {})

    # 1. Flatten all antardashas into a single ordered list
    for md_lord, md_data in mahadashas.items():
        antardashas = md_data.get("antardashas", {})
        for ad_lord, ad_data in antardashas.items():
            # Store references to reconstruct the structure later
            flat_antardashas.append(
                {
                    "md_lord": md_lord,
                    "ad_lord": ad_lord,
                    "ad_data": ad_data,
                    "md_data": {"start": md_data["start"], "end": md_data["end"]},
                }
            )

    if not flat_antardashas:
        return {"mahadashas": OrderedDict()}

    # 2. Find the index of the current antardasha
    current_ad_index = -1
    for i, ad_info in enumerate(flat_antardashas):
        if ad_info["ad_data"]["start"] <= current_datetime < ad_info["ad_data"]["end"]:
            current_ad_index = i
            break

    # Handle edge case where current_datetime is before the first dasha
    if current_ad_index == -1:
        for i, ad_info in enumerate(flat_antardashas):
            if ad_info["ad_data"]["start"] > current_datetime:
                current_ad_index = i - 1  # Start collecting from the next item
                break

    # If still not found or at the very end, return empty
    if current_ad_index is None or current_ad_index >= len(flat_antardashas) - 1:
        return {"mahadashas": OrderedDict()}

    # 3. Get the next 3 antardashas from the list
    start_index = current_ad_index + 1
    upcoming_ads_list = flat_antardashas[start_index : start_index + 3]

    # 4. Rebuild the required nested dictionary structure
    upcoming_periods: dict[str, Any] = {"mahadashas": OrderedDict()}
    for ad_info in upcoming_ads_list:
        md_lord = ad_info["md_lord"]
        ad_lord = ad_info["ad_lord"]

        # If this Mahadasha isn't in our results yet, add its main info
        if md_lord not in upcoming_periods["mahadashas"]:
            upcoming_periods["mahadashas"][md_lord] = {
                "start": ad_info["md_data"]["start"],
                "end": ad_info["md_data"]["end"],
                "antardashas": OrderedDict(),
            }

        # Add the antardasha to its corresponding Mahadasha
        upcoming_periods["mahadashas"][md_lord]["antardashas"][ad_lord] = ad_info[
            "ad_data"
        ]

    return upcoming_periods


def calculate_vimshottari_dashas(
    person_birth_datetime: datetime,
    timezone_offset: float,
    latitude: float,  # Retained for API consistency, not used in this calculation
    longitude: float,  # Retained for API consistency, not used in this calculation
    ayanamsa_degrees: float,
    max_depth: int = 3,
) -> Dashas:
    """
    Main function to calculate all Vimshottari dasha periods using corrected logic.
    """
    # 1. Calculate the starting Dasha lord and its precise start datetime
    dasha_lord_at_birth, cycle_start_date = calculate_dasha_start_date(
        person_birth_datetime, timezone_offset, ayanamsa_degrees
    )

    # 2. Generate the properly nested "all" periods structure
    all_periods: dict[str, Any] = {"mahadashas": OrderedDict()}
    current_lord = dasha_lord_at_birth
    current_start_date = cycle_start_date

    for _ in range(len(VIMSHOTTARI_ADHIPATI_LIST)):
        duration_years = VIMSHOTTARI_DASHA_DURATIONS[current_lord]
        duration_days = duration_years * YEAR_DURATION_DAYS
        end_date = current_start_date + timedelta(days=duration_days)

        mahadasha_data: dict[str, Any] = {"start": current_start_date, "end": end_date}

        # Generate antardashas (and potentially pratyantardashas)
        if max_depth >= 2:
            mahadasha_data["antardashas"] = _generate_sub_periods(
                parent_lord=current_lord,
                parent_start_date=current_start_date,
                parent_duration_days=duration_days,
                current_level=2,
                max_depth=max_depth,
            )

        all_periods["mahadashas"][current_lord] = mahadasha_data

        current_start_date = end_date
        current_lord = get_next_adhipati(current_lord)

    # 4. Calculate Dasha balance
    balance = {}
    birth_mahadasha = all_periods["mahadashas"][dasha_lord_at_birth]
    remaining_days = (
        birth_mahadasha["end"] - person_birth_datetime
    ).total_seconds() / (24 * 3600)
    balance[dasha_lord_at_birth] = round(remaining_days / YEAR_DURATION_DAYS, 4)

    # 5. Extract current and upcoming periods using current time
    current_time = datetime.now()
    current_periods = _extract_current_periods(all_periods, current_time)
    upcoming_periods = _extract_upcoming_periods(all_periods, current_time)

    return Dashas(
        balance=balance,
        all=all_periods,
        current=current_periods,
        upcoming=upcoming_periods,
    )


# For testing the corrected script
if __name__ == "__main__":
    birth = datetime(1994, 10, 23, 10, 20, 0)
    tz = 5.5
    lat = 19.9993
    lng = 73.79

    # Calculate a fresh ayanamsa for the birth time
    t = skyfield_time_from_datetime(birth, tz)
    ayanamsa = calculate_ayanamsa(t)
    print(f"Using Ayanamsa: {ayanamsa:.4f} degrees")

    # Calculate dashas up to Pratyantardasha (level 3)
    dashas = calculate_vimshottari_dashas(birth, tz, lat, lng, ayanamsa, max_depth=3)

    print("\n--- Dasha Balance at Birth ---")
    for lord, years in dashas.balance.items():
        print(f"{lord}: {years:.2f} years remaining")

    print("\n--- Full Dasha Tree (Sample) ---")
    # Let's inspect the Venus Mahadasha
    venus_md = dashas.all["mahadashas"].get("Venus")
    if venus_md:
        print(
            f"Venus Mahadasha: {venus_md['start'].strftime('%Y-%m-%d')} to {venus_md['end'].strftime('%Y-%m-%d')}"
        )

        # Inspect the Venus-Saturn bhukti using 'antardashas' key
        venus_antardashas = venus_md.get("antardashas", {})
        saturn_bhukti = venus_antardashas.get("Saturn")
        if saturn_bhukti:
            print(
                f"  Saturn Bhukti: {saturn_bhukti['start'].strftime('%Y-%m-%d')} to {saturn_bhukti['end'].strftime('%Y-%m-%d')}"
            )

            # Inspect the Pratyantardashas within Venus-Saturn using 'pratyantardashas' key
            pratyantars = saturn_bhukti.get("pratyantardashas", {})
            if pratyantars:
                print("    Pratyantardashas:")
                for pr_lord, pr_data in list(pratyantars.items())[
                    :3
                ]:  # Print first 3 for brevity
                    print(
                        f"      {pr_lord.ljust(8)}: {pr_data['start'].strftime('%Y-%m-%d')}"
                    )

    print("\n--- Current Dasha Period (as of now) ---")
    current_mahadashas = dashas.current.get("mahadashas", {})
    if not current_mahadashas:
        print("Could not determine current dasha.")
    else:
        current_md_lord = list(current_mahadashas.keys())[0]
        current_md_data = current_mahadashas[current_md_lord]

        current_antardashas = current_md_data.get("antardashas", {})
        current_ad_lord = list(current_antardashas.keys())[0]
        current_ad_data = current_antardashas[current_ad_lord]

        current_pratyantardashas = current_ad_data.get("pratyantardashas", {})
        current_pd_lord = list(current_pratyantardashas.keys())[0]
        current_pd_data = current_pratyantardashas[current_pd_lord]

        print(
            f"MD: {current_md_lord} ({current_md_data['start'].strftime('%Y-%m-%d')} to {current_md_data['end'].strftime('%Y-%m-%d')})"
        )
        print(
            f"AD: {current_ad_lord} ({current_ad_data['start'].strftime('%Y-%m-%d')} to {current_ad_data['end'].strftime('%Y-%m-%d')})"
        )
        print(
            f"PD: {current_pd_lord} ({current_pd_data['start'].strftime('%Y-%m-%d')} to {current_pd_data['end'].strftime('%Y-%m-%d')})"
        )

    print("\n--- Upcoming Antardashas ---")
    upcoming_mahadashas = dashas.upcoming.get("mahadashas", {})
    if not upcoming_mahadashas:
        print("No upcoming antardashas found.")
    else:
        for md_lord, md_data in upcoming_mahadashas.items():
            for ad_lord, ad_data in md_data.get("antardashas", {}).items():
                print(
                    f"{md_lord.ljust(8)} - {ad_lord.ljust(8)}: {ad_data['start'].strftime('%Y-%m-%d')} to {ad_data['end'].strftime('%Y-%m-%d')}"
                )
