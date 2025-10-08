# ॐ गं गणपतये नमः

# jyotishganit

[![PyPI version](https://badge.fury.io/py/jyotishganit.svg)](https://badge.fury.io/py/jyotishganit)
[![Python Version](https://img.shields.io/pypi/pyversions/jyotishganit.svg)](https://pypi.org/project/jyotishganit/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://pepy.tech/badge/jyotishganit)](https://pepy.tech/project/jyotishganit)
[![GitHub](https://img.shields.io/github/stars/northtara/jyotishganit?style=social)](https://github.com/northtara/jyotishganit)

**Professional grade Vedic Astrology Computation Library for Python**

jyotishganit is a comprehensive, high precision Python library that brings the ancient wisdom of Jyotisha (Vedic Astrology) to modern computational environments. Built with astronomical accuracy using NASA JPL ephemeris data and designed for both researchers and practitioners, it provides complete birth chart generation with traditional Indian astrological elements.

## Key Features

- **Astronomical Precision**: NASA JPL DE421 ephemeris data via Skyfield for research grade accuracy
- **Complete Birth Charts**: Full D1-D60 divisional chart calculations following Vedic principles  
- **Panchanga System**: Traditional five limb almanac with Tithi, Nakshatra, Yoga, Karana, Vaara
- **Shadbala Calculations**: Six fold planetary strength analysis with detailed breakdowns
- **Dasha Periods**: Vimshottari Dasha system with precise planetary periods. With more under development
- **Cross-Platform**: Works seamlessly on Windows, macOS, and Linux
- **JSON-LD Output**: Structured data format for modern web integration
- **Developer-Friendly**: Clean Python API with comprehensive documentation

## 🚀 Quick Start

```bash
pip install jyotishganit
```

```python
from datetime import datetime
from jyotishganit import calculate_birth_chart, get_birth_chart_json_string

# Generate a complete Vedic birth chart
chart = calculate_birth_chart(
    birth_date=datetime(1996, 7, 4, 9, 10, 0), # 4th July 1996 9:10 am
    latitude=18.404,   # Karmala, India  
    longitude=75.195,
    timezone_offset=5.5,  # IST
    name="Bhampu"
)

# Access key astrological data
print(f"Ascendant: {chart.d1_chart.houses[0].sign}")
print(f"Moon Sign: {chart.d1_chart.planets[1].sign}")  # Moon is index 1
print(f"Nakshatra: {chart.panchanga.nakshatra}")

# Save the entire chart as JSON
with open("birth_chart.json", "w") as json_file:
    json_file.write(get_birth_chart_json_string(chart))

print("Birth chart saved to birth_chart.json")
```

Expected output:
```
Ascendant: Leo
Moon Sign: Aquarius
Nakshatra: Dhanishta
Birth chart saved to birth_chart.json
```

## Comprehensive Astrological Components

### Astronomical Foundation
- **Planetary Positions**: All 9 Vedic grahas (Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu)
- **True Chitra Paksha Ayanamsa**: Precise sidereal zodiac alignment using Spica star reference
- **House System**: Traditional whole sign houses with accurate cusp calculations
- **Cross-Platform Data Storage**: Follows OS conventions for ephemeris data storage

### Panchanga (Vedic Almanac)
```python
panchanga = chart.panchanga
print(f"Tithi: {panchanga.tithi}")           # Lunar day (1-30)
print(f"Nakshatra: {panchanga.nakshatra}")   # Moon's constellation
print(f"Yoga: {panchanga.yoga}")             # Sun-Moon combination
print(f"Karana: {panchanga.karana}")         # Half lunar day
print(f"Vaara: {panchanga.vaara}")           # Weekday
```

Expected output:
```
Tithi: Krishna Chaturthi
Nakshatra: Dhanishta
Yoga: Priti
Karana: Balava
Vaara: Thursday
```

### Divisional Charts (Varga Chakra)
Complete D1-D60 chart calculations following traditional Vedic methods:

| Chart | Sanskrit Name                | Significance                                | Usage                                                                 |
|-------|------------------------------|--------------------------------------------|----------------------------------------------------------------------|
| D1    | Rasi                         | General life, personality                   | Primary analysis of overall tendencies and potential                 |
| D2    | Hora                         | Wealth and financial potential              | Detailed analysis of financial prosperity, assets, and savings       |
| D3    | Drekkana                     | Courage, siblings, and personal efforts    | Analysis of relationships with siblings and personal drive           |
| D4    | Chaturthamsa                 | Fixed assets, property, happiness          | Analysis of real estate, home life, and general well-being           |
| D7    | Saptamsa                     | Children, progeny, and creativity          | Analysis of potential for and relationship with children             |
| D9    | Navamsa                      | Marriage, dharma, spiritual growth         | Reveals inner potential, spouse characteristics, and destiny after marriage |
| D10   | Dasamsa                      | Career, profession, social status          | Detailed analysis of professional life, achievements, and public reputation |
| D12   | Dwadasamsa                   | Parents, ancestors, lineage                | Analysis of parental and ancestral karma, and inherited traits       |
| D16   | Shodasamsa                    | Vehicles, luxuries, material comforts      | Evaluation of worldly pleasures, happiness, and conveyances          |
| D24   | Chaturvimsamsa               | Education and learning                      | Analysis of higher education, knowledge, and academic achievements   |
| D27   | Bhamsha / Saptavimsamsa      | Physical strength and weaknesses           | Evaluation of overall vitality, stamina, and resilience              |
| D30   | Trimsamsa                     | Misfortunes, evils, and suffering         | Analysis of adversities, health issues, and hidden troubles          |
| D60   | Shashtiamsa                  | Past life karmas, deep-rooted destiny      | Final confirmation for predictions, revealing inherited blessings and karmic debt |


```python
# Access any divisional chart
navamsa = chart.divisional_charts['d9']
for house in navamsa.houses:
    for planet in house.occupants:
        print(f"{planet.celestial_body} in {planet.sign}")
```

Expected output:
```
Venus in Gemini
Rahu in Gemini
Mars in Cancer
Jupiter in Virgo
Moon in Libra
Saturn in Scorpio
Ketu in Sagittarius
Mercury in Capricorn
Sun in Pisces
```

### Shadbala (Six-Fold Strength System)
Comprehensive planetary strength analysis with traditional calculations:

```python
sun = chart.d1_chart.planets[0]  # Sun
shadbala = sun.shadbala['Shadbala']

print(f"Total Shadbala: {shadbala['Total']:.2f}")
print(f"Strength in Rupas: {shadbala['Rupas']:.2f}")

# Detailed breakdown
print(f"Positional Strength: {shadbala['Sthanabala']:.2f}")
print(f"Temporal Strength: {shadbala['Kaalabala']:.2f}")  
print(f"Directional Strength: {shadbala['Digbala']:.2f}")
print(f"Motional Strength: {shadbala['Cheshtabala']:.2f}")
print(f"Natural Strength: {shadbala['Naisargikabala']:.2f}")
print(f"Aspectual Strength: {shadbala['Drikbala']:.2f}")
```

Expected output:
```
Total Shadbala: 587.09
Strength in Rupas: 9.79
Positional Strength: 130.87
Temporal Strength: 222.92
Directional Strength: 48.78
Motional Strength: 117.13
Natural Strength: 60.00
Aspectual Strength: 7.39
```

### Ashtakavarga System
Traditional point-based strength calculation:

```python
# Get Sarvashtakavarga (combined points for all planets)
sarva = chart.ashtakavarga.sav
for sign, points in sarva.items():
    print(f"{sign}: {points} points")

# Individual planet ashtakavarga (Bhinnashktakavarga)  
sun_ak = chart.ashtakavarga.bhav['Sun']
print(f"Sun's contribution to each sign: {sun_ak}")
```

Expected output:
```
Aries: 31 points
Taurus: 27 points
Gemini: 29 points
Cancer: 24 points
Leo: 27 points
Virgo: 24 points
Libra: 33 points
Scorpio: 31 points
Sagittarius: 27 points
Capricorn: 29 points
Aquarius: 22 points
Pisces: 33 points
Sun's contribution to each sign: {'Aries': 6, 'Taurus': 4, 'Gemini': 4, 'Cancer': 3, 'Leo': 3, 'Virgo': 2, 'Libra': 5, 'Scorpio': 6, 'Sagittarius': 4, 'Capricorn': 4, 'Aquarius': 3, 'Pisces': 4}
```

### Dasha Periods (Planetary Periods)
Precise Vimshottari Dasha calculations:

```python
dashas = chart.dashas
print('\n\n'.join(['Mahadasha: %s\n  Start: %s\n  End:   %s' % (lord, md['start'], md['end']) for lord, md in list(dashas.upcoming['mahadashas'].items())[:3]]))
```
**Expected output:**
```
Mahadasha: Jupiter
    Start: 2017-06-21 
    End:   2033-06-22 
```
## Planetary Dignities

Access planetary dignities for any planet. Example (Mars):

```python
mars = next(p for p in chart.d1_chart.planets if p.celestial_body == "Mars")
print(f"Mars dignities: {mars.dignities}")
```
Expected output:
```
Mars dignities: PlanetDignities(dignity='neutral', planet_tattva='Fire', rashi_tattva='Earth', friendly_tattvas=['Air', 'Fire'])
```

### Graha Drishti (Planetary Aspects)  
Traditional Vedic aspectual relationships:
```python
# Planets aspecting and aspected
jupiter = next(p for p in chart.d1_chart.planets if p.celestial_body == "Jupiter")

# Houses aspected by Jupiter
houses_aspected = [aspect['to_house'] for aspect in jupiter.aspects['gives'] if 'to_house' in aspect]
print(f"Jupiter aspects houses: {houses_aspected}")

# Planets aspecting Jupiter  
aspected_by = [aspect['from_planet'] for aspect in jupiter.aspects['receives']]
print(f"Jupiter is aspected by: {aspected_by}")
```

Expected output:
```
Jupiter aspects houses: [1, 11, 9]
Jupiter is aspected by: ['Mars', 'Saturn', 'Mercury', 'Sun']
```


### Installation

#### Standard Installation
```bash
pip install jyotishganit
```

#### Development Installation  
```bash
git clone https://github.com/northtara/jyotishganit.git
cd jyotishganit
pip install -e .
```

### Data Storage
Ephemeris data is automatically stored in platform-appropriate locations:
- **Windows**: `%LOCALAPPDATA%\jyotishganit\`
- **macOS**: `~/Library/Application Support/jyotishganit/`  
- **Linux**: `~/.local/share/jyotishganit/`

## Testing & Validation

jyotishganit includes comprehensive test suites ensuring calculation accuracy:

```bash
# Run all tests
python -m pytest tests/

# Run specific test categories  
python -m pytest tests/test_panchanga.py      # Panchanga calculations
python -m pytest tests/test_strengths.py     # Shadbala calculations
python -m pytest tests/test_birth_charts.py  # Complete chart generation
python -m pytest tests/test_cross_platform.py # Platform compatibility

# Package validation
python validate_package.py
```

### Calculation Accuracy
- **Planetary Positions**: Accurate to arc-seconds using JPL ephemeris
- **Ayanamsa**: True Chitra Paksha based on Spica star position  
- **Traditional Methods**: Follows classical Vedic texts (Brihat Parashara Hora Shastra, etc.)
- **Cross-Verification**: Calculations verified against established Jyotisha software

## API Reference

### Core Functions

```python
from jyotishganit import calculate_birth_chart, get_birth_chart_json, Person

# Main calculation function
chart = calculate_birth_chart(
    birth_date=datetime,     # Local birth time
    latitude=float,          # Geographic latitude  
    longitude=float,         # Geographic longitude
    timezone_offset=float,   # Hours from UTC (e.g., 5.5 for IST)
    location_name=str,       # Optional location name
    name=str                 # Optional person name
) -> VedicBirthChart

# JSON output functions  
json_dict = get_birth_chart_json(chart)           # -> Dict[str, Any]
json_string = get_birth_chart_json_string(chart)  # -> str
```

### Data Models

#### VedicBirthChart
The complete birth chart container with all astrological data:

```python
chart.person            # Person: Birth details and location
chart.ayanamsa          # Ayanamsa: Calculated ayanamsa value  
chart.panchanga         # Panchanga: Five-limb almanac data
chart.d1_chart          # RasiChart: Primary birth chart (D1)
chart.divisional_charts # Dict[str, RasiChart]: D2-D60 charts
chart.ashtakavarga      # Dict: Ashtakavarga point system
chart.dashas           # Dashas: Vimshottari dasha periods
```

#### PlanetPosition  
Individual planetary data with comprehensive details:

```python
planet.celestial_body   # str: Planet name
planet.sign            # str: Zodiac sign 
planet.sign_degrees    # float: Degrees within sign
planet.nakshatra       # str: Lunar constellation
planet.pada            # int: Nakshatra quarter (1-4)
planet.house           # int: House number (1-12)
planet.dignities       # List[str]: Astrological dignities
planet.shadbala        # Dict: Six-fold strength calculations
planet.aspects_houses  # List[int]: Houses aspected
planet.aspected_by     # List[str]: Planets aspecting this one
```

## Contributing

We welcome contributions from the Vedic astrology and Python communities!

### Development Setup
```bash
git clone https://github.com/northtara/jyotishganit.git
cd jyotishganit
pip install -r requirements-dev.txt
pip install -e .
```

### Running Tests
```bash
pytest tests/                    # All tests
python validate_package.py      # Package validation
black jyotishganit/             # Code formatting
mypy jyotishganit/              # Type checking  
```

### Contribution Guidelines
-  **Focus**: Maintain accuracy to traditional Vedic astrology principles
-  **Testing**: Include comprehensive tests for new features
-  **Documentation**: Update docstrings and README for API changes
-  **Performance**: Consider computational efficiency for large-scale usage

## License

**MIT License** - see [LICENSE](LICENSE) file for details.

##  Acknowledgments

- **Astronomical Foundation**: Built on [Skyfield](https://rhodesmill.org/skyfield/) (MIT License) for precise ephemeris calculations
- **Traditional Wisdom**: Calculations follow classical Vedic texts, including but not limited to Brihat Parashara Hora Shastra, Saravali, Surya Siddhanta
- **Modern Integration**: Designed for contemporary software development while preserving ancient accuracy

## Project Status

| Aspect | Status |
|--------|---------|
| **Stability** | ✅ Production Ready |
| **Testing** | ✅ Comprehensive Test Suite |  
| **Documentation** | ✅ Complete API Documentation |
| **Cross-Platform** | ✅ Windows, macOS, Linux |
| **Python Versions** | ✅ 3.8, 3.9, 3.10, 3.11, 3.12 |
| **CI/CD** | ✅ GitHub Actions |
| **Package Quality** | ✅ PyPI Best Practices |

---

Built with reverence for the ancient science of Jyotish and modern software engineering excellence by the team behind Northtara.ai

*|| श्री कृष्णार्पणमस्तु ||*
