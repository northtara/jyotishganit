"""
Data models for jyotishganit library.

This module defines the core data structures used throughout the library.
All classes are designed to be immutable and serializable for JSON-LD output.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from jyotishganit.core.constants import MIN_REQUIRED_SHADBALA


@dataclass
class Person:
    """Represents a person with birth details."""

    birth_datetime: datetime
    latitude: float  # Degrees
    longitude: float  # Degrees
    timezone_offset: float = 0.0  # Hours UTC
    timezone: str | None = None
    name: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "@type": "Person",
            "name": self.name,
            "birthDate": self.birth_datetime.isoformat() + "+00:00",  # UTC opaque
            "birthPlace": {
                "@type": "Place",
                "geo": {
                    "@type": "GeoCoordinates",
                    "latitude": self.latitude,
                    "longitude": self.longitude,
                },
            },
        }


@dataclass
class Ayanamsa:
    """Represents an ayanamsa value."""

    name: str
    value: float  # Degrees

    def to_dict(self) -> dict[str, Any]:
        return {"@type": "Ayanamsa", "name": self.name, "value": self.value}


@dataclass
class Panchanga:
    """Represents the five limbs of panchanga."""

    tithi: str
    nakshatra: str
    yoga: str
    karana: str
    vaara: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "@type": "Panchanga",
            "tithi": self.tithi,
            "nakshatra": self.nakshatra,
            "yoga": self.yoga,
            "karana": self.karana,
            "vaara": self.vaara,
        }


@dataclass
class PlanetDignities:
    """Consolidated dignities for a planet."""

    dignity: str = "none"  # "deep_exaltation", "exalted", "deep_debilitation", "debilitated", "moolatrikona", "own_sign", "friendly", "neutral", "enemy"
    planet_tattva: str = "Water"
    rashi_tattva: str = "Water"
    friendly_tattvas: list[str] = field(default_factory=lambda: ["Water"])

    def to_dict(self) -> dict[str, Any]:
        return {
            "@type": "PlanetDignities",
            "dignity": self.dignity,
            "planetTattva": self.planet_tattva,
            "rashiTattva": self.rashi_tattva,
            "friendlyTattvas": self.friendly_tattvas,
        }


@dataclass
class PlanetPosition:
    """Represents a planet's position in the chart."""

    celestial_body: str
    sign: str
    sign_degrees: float
    nakshatra: str
    pada: int
    nakshatra_deity: str
    house: int
    motion_type: str  # "direct", "retrograde", or "stationary"
    shadbala: dict[str, Any]
    dignities: PlanetDignities
    conjuncts: list[str]
    aspects: dict[str, list[dict[str, Any]]]  # gives and receives
    has_lordship_houses: list[int] = field(default_factory=list)

    def _format_shadbala(self) -> dict[str, Any]:
        """Format shadbala data into the proper grouped JSON structure."""
        formatted = {}

        # Handle Sthanabala group
        sthana = self.shadbala.get("Sthanabala", {})
        if sthana:
            formatted["Sthanabala"] = {
                "Uchhabala": sthana.get("Uchhabala", 0),
                "Saptavargajabala": sthana.get("Saptavargajabala", 0),
                "Ojhayugmarashiamshabala": sthana.get("Ojhayugmarashiamshabala", 0),
                "Kendradhibala": sthana.get("Kendradhibala", 0),
                "Drekshanabala": sthana.get("Drekshanabala", 0),
                "Total": sthana.get("Total", 0),
            }

        # Handle Digbala (single value)
        if "Digbala" in self.shadbala:
            formatted["Digbala"] = self.shadbala["Digbala"]

        # Handle Kaalabala group
        kaala = self.shadbala.get("Kaalabala", {})
        if kaala:
            formatted["Kaalabala"] = {
                "Natonnatabala": kaala.get("Natonnatabala", 0),
                "Pakshabala": kaala.get("Pakshabala", 0),
                "Tribhagabala": kaala.get("Tribhagabala", 0),
                "VarshaMaasaDinaHoraBala": kaala.get("VarshaMaasaDinaHoraBala", 0),
                "Ayanabala": kaala.get("Ayanabala", 0),
                "Total": kaala.get("Total", 0),
                "Yuddhabala": kaala.get("Yuddhabala", 0),
            }

        # Handle single-value components
        single_components = [
            "Cheshtabala",
            "Naisargikabala",
            "Drikbala",
            "Ishtabala",
            "Kashtabala",
        ]
        for component in single_components:
            if component in self.shadbala:
                formatted[component] = self.shadbala[component]

        # Handle final Shadbala group (capital S)
        shadbala_final = self.shadbala.get("Shadbala", {})
        if shadbala_final:
            rupas = shadbala_final.get("Rupas", 0)
            min_required = MIN_REQUIRED_SHADBALA.get(self.celestial_body, 0)
            meets_requirement = "Yes" if rupas >= min_required else "No"

            formatted["Shadbala"] = {
                "Total": shadbala_final.get("Total", 0),
                "Rupas": rupas,
                "MinRequired": min_required,
                "MeetsRequirement": meets_requirement,
            }

        return formatted

    def to_dict(self) -> dict[str, Any]:
        return {
            "@type": "PlanetPosition",
            "celestialBody": self.celestial_body,
            "sign": self.sign,
            "signDegrees": self.sign_degrees,
            "nakshatra": self.nakshatra,
            "pada": self.pada,
            "nakshatraDeity": self.nakshatra_deity,
            "house": self.house,
            "motion_type": self.motion_type,
            "shadbala": self._format_shadbala(),
            "dignities": self.dignities.to_dict(),
            "conjuncts": self.conjuncts,
            "aspects": self.aspects,
            "hasLordshipHouses": self.has_lordship_houses,
        }


@dataclass
class House:
    """Represents a house in the chart."""

    number: int
    sign: str
    lord: str
    bhava_bala: float
    occupants: list[PlanetPosition]
    aspects_received: list[dict[str, Any]]
    purposes: list[str]
    lord_placed_sign: str = ""
    lord_placed_house: int = 0
    # For ascendant house only (number=1)
    sign_degrees: float | None = None
    nakshatra: str | None = None
    pada: int | None = None
    nakshatra_deity: str | None = None

    def to_dict(self) -> dict[str, Any]:
        d = {
            "@type": "House",
            "number": self.number,
            "sign": self.sign,
            "lord": self.lord,
            "lordPlacedSign": self.lord_placed_sign,
            "lordPlacedHouse": self.lord_placed_house,
            "bhavaBala": self.bhava_bala,
            "occupants": [p.to_dict() for p in self.occupants],
            "aspectsReceived": self.aspects_received,
            "purposes": self.purposes,
        }
        # Add ascendant details for house 1
        if self.number == 1:
            if self.sign_degrees is not None:
                d["signDegrees"] = self.sign_degrees
            if self.nakshatra is not None:
                d["nakshatra"] = self.nakshatra
            if self.pada is not None:
                d["pada"] = self.pada
            if self.nakshatra_deity is not None:
                d["nakshatraDeity"] = self.nakshatra_deity
        return d


@dataclass
class RasiChart:
    """Represents a Rasi (D1) or Bhav chart."""

    planets: list[PlanetPosition]
    houses: list[House]

    def to_dict(self) -> dict[str, Any]:
        return {"@type": "RasiChart", "houses": [h.to_dict() for h in self.houses]}


@dataclass
class DivisionalAscendant:
    """Ascendant in divisional charts."""

    sign: str
    d1_house_placement: int  # D1 house where D1 asc sign falls

    def to_dict(self) -> dict[str, Any]:
        return {
            "@type": "DivisionalAscendant",
            "sign": self.sign,
            "d1HousePlacement": self.d1_house_placement,
        }


@dataclass
class DivisionalPlanetPosition:
    """Planet position in divisional charts."""

    celestial_body: str
    sign: str
    d1_house_placement: int  # D1 house where D1 sign belongs

    def to_dict(self) -> dict[str, Any]:
        return {
            "@type": "DivisionalPlanetPosition",
            "celestialBody": self.celestial_body,
            "sign": self.sign,
            "d1HousePlacement": self.d1_house_placement,
        }


@dataclass
class DivisionalHouse:
    """House in divisional charts."""

    number: int
    sign: str
    lord: str
    d1_house_placement: int
    occupants: list[DivisionalPlanetPosition] = field(default_factory=list)
    aspects_received: list[dict[str, Any]] = field(default_factory=list)
    purposes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "@type": "DivisionalHouse",
            "number": self.number,
            "sign": self.sign,
            "lord": self.lord,
            "d1HousePlacement": self.d1_house_placement,
            "occupants": [p.to_dict() for p in self.occupants],
            "aspectsReceived": self.aspects_received,
            "purposes": self.purposes,
        }


@dataclass
class DivisionalChart:
    """Represents a divisional chart."""

    chart_type: str  # "d9", "d4", etc.
    ascendant: DivisionalAscendant
    houses: list[DivisionalHouse]

    def to_dict(self) -> dict[str, Any]:
        return {
            "@type": f"{self.chart_type.upper()}Chart",
            "ascendant": self.ascendant.to_dict(),
            "houses": [h.to_dict() for h in self.houses],
        }


@dataclass
class Aspect:
    """Represents a planetary aspect."""

    from_body: str
    to_body: str | None  # None for house aspect
    type: str  # "5th", "7th", "3rd", etc.

    def to_dict(self) -> dict[str, Any]:
        result = {"@type": "Aspect", "from": self.from_body, "type": self.type}
        if self.to_body:
            result["to"] = self.to_body
        else:
            result["to"] = f"House{self.to_body}"  # Corrected
        return result


@dataclass
class Ashtakavarga:
    """Represents Ashtakavarga calculations."""

    bhav: dict[
        str, dict[str, int]
    ]  # Individual Bhinna Ashtakavarga charts (sign -> bindu)
    sav: dict[str, int]  # Sarvashtakavarga (total) (sign -> bindu)

    def to_dict(self) -> dict[str, Any]:
        result = {"@type": "Ashtakavarga", "sav": self.sav}
        # Add individual Bhinna charts
        for planet, bindus in self.bhav.items():
            result[f"{planet.lower()}Bhav"] = bindus
        return result


@dataclass
class VedicBirthChart:
    """Complete Vedic birth chart."""

    person: Person
    ayanamsa: Ayanamsa
    panchanga: Panchanga
    d1_chart: RasiChart
    divisional_charts: dict[str, DivisionalChart]
    ashtakavarga: Ashtakavarga
    dashas: Dashas

    def to_dict(self) -> dict[str, Any]:
        """Convert to final JSON-LD dict."""
        return {
            "@context": "https://jyotishganit.org/vocab/v1.jsonld",
            "@type": "VedicBirthChart",
            "person": self.person.to_dict(),
            "ayanamsa": self.ayanamsa.to_dict(),
            "panchanga": self.panchanga.to_dict(),
            "d1Chart": self.d1_chart.to_dict(),
            "divisionalCharts": {
                k: v.to_dict() for k, v in self.divisional_charts.items()
            },
            "ashtakavarga": self.ashtakavarga.to_dict(),
            "dashas": self.dashas.to_dict(),
        }


@dataclass
class DashaPeriod:
    """Represents a dasha period with start and end dates."""

    lord: str
    start_date: datetime
    end_date: datetime | None = None
    subperiods: list[DashaPeriod] = field(default_factory=list)
    level: str = ""  # mahadasha, antardasha, pratyantardasha, etc.

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "@type": "DashaPeriod",
            "lord": self.lord,
            "startDate": self.start_date.strftime("%d-%m-%Y"),
            "level": self.level,
        }
        if self.end_date:
            d["endDate"] = self.end_date.strftime("%d-%m-%Y")
        if self.subperiods:
            d["subperiods"] = [sp.to_dict() for sp in self.subperiods]
        return d


@dataclass
class Dashas:
    """Represents all dasha periods: all, current, upcoming."""

    balance: dict[str, float]  # Remaining balance of mahadashas at birth
    all: dict[str, Any]  # nested: {md_lord: {ad_lord: {pd_lord: period_data}}}
    current: dict[
        str, Any
    ]  # nested: current {md_lord: {ad_lord: {pd_lord: period_data}}}
    upcoming: dict[str, Any]  # nested: {md_lord: {ad_lord: {pd_lord: period_data}}}

    def _serialize_datetime_tree(self, period_data: dict[str, Any]) -> dict[str, Any]:
        """Recursively serialize datetime objects in the period tree to strings."""
        if isinstance(period_data, dict):
            result: dict[str, Any] = {}
            for key, value in period_data.items():
                if isinstance(value, dict):
                    result[key] = self._serialize_datetime_tree(value)
                elif isinstance(value, datetime):
                    result[key] = value.strftime("%Y-%m-%d")  # ISO date format
                else:
                    result[key] = value
            return result
        return period_data

    def to_dict(self) -> dict[str, Any]:
        return {
            "@type": "Dashas",
            "balance": self.balance,
            "all": self._serialize_datetime_tree(self.all),
            "current": self._serialize_datetime_tree(self.current),
            "upcoming": self._serialize_datetime_tree(self.upcoming),
        }
