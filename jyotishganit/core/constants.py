# In core/constants.py
"""
Constants and data structures for jyotishganit library.
Centralizes all static astrological data for consistency and maintainability.
"""

# Zodiac signs
ZODIAC_SIGNS = [
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
]

# Nakshatras (27 lunar mansions)
NAKSHATRAS = [
    "Ashwini",
    "Bharani",
    "Krittika",
    "Rohini",
    "Mrigashira",
    "Ardra",
    "Punarvasu",
    "Pushya",
    "Ashlesha",
    "Magha",
    "Purva Phalguni",
    "Uttara Phalguni",
    "Hasta",
    "Chitra",
    "Swati",
    "Vishakha",
    "Anuradha",
    "Jyeshtha",
    "Mula",
    "Purva Ashadha",
    "Uttara Ashadha",
    "Shravana",
    "Dhanishta",
    "Shatabhisha",
    "Purva Bhadrapada",
    "Uttara Bhadrapada",
    "Revati",
]

# Nakshatra deities
NAKSHATRA_DEITIES = [
    "Ashwini Kumaras",
    "Yama",
    "Agni",
    "Brahma",
    "Soma",
    "Rudra",
    "Aditi",
    "Brihaspati",
    "Nagas",
    "Pitris",
    "Aryaman",
    "Bhaga",
    "Surya",
    "Vishwakarma",
    "Vayu",
    "Indra-Agni",
    "Mitra",
    "Indra",
    "Nirriti",
    "Apah",
    "Vishvedevatas",
    "Vishnu",
    "Vasus",
    "Varuna",
    "Ajikapada",
    "Ahirbudhnya",
    "Pushan",
]

# Karana names - Authoritative Vedic ordering
# 7 Movable (Chara) Karanas - repeat 8 times (positions 1-56)
# 4 Fixed (Sthira) Karanas - occur once each (positions 57-60)
MOVABLE_KARANAS = ["Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti"]
FIXED_KARANAS = ["Shakuni", "Chatushpada", "Naga", "Kimstughna"]
# Yoga names (27)
YOGA_NAMES = [
    "Vishkambha",
    "Priti",
    "Ayushman",
    "Saubhagya",
    "Shobhana",
    "Atiganda",
    "Sukarma",
    "Dhriti",
    "Shula",
    "Ganda",
    "Vriddhi",
    "Dhruva",
    "Vyaghata",
    "Harshana",
    "Vajra",
    "Siddhi",
    "Vyatipata",
    "Variyana",
    "Parigha",
    "Shiva",
    "Siddha",
    "Sadhya",
    "Shubha",
    "Shukla",
    "Brahma",
    "Indra",
    "Vaidhriti",
]

# Tithi names (30)
TITHI_NAMES = [
    "Shukla Pratipada",
    "Shukla Dwitiya",
    "Shukla Tritiya",
    "Shukla Chaturthi",
    "Shukla Panchami",
    "Shukla Shashthi",
    "Shukla Saptami",
    "Shukla Ashtami",
    "Shukla Navami",
    "Shukla Dashami",
    "Shukla Ekadashi",
    "Shukla Dwadashi",
    "Shukla Trayodashi",
    "Shukla Chaturdashi",
    "Purnima",
    "Krishna Pratipada",
    "Krishna Dwitiya",
    "Krishna Tritiya",
    "Krishna Chaturthi",
    "Krishna Panchami",
    "Krishna Shashthi",
    "Krishna Saptami",
    "Krishna Ashtami",
    "Krishna Navami",
    "Krishna Dashami",
    "Krishna Ekadashi",
    "Krishna Dwadashi",
    "Krishna Trayodashi",
    "Krishna Chaturdashi",
    "Amavasya",
]

# Vaara (weekdays) - Starting with Sunday as per Vedic tradition
VAARA_NAMES = [
    "Sunday",
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
]

# Planetary tattvas (elements)
PLANETARY_TATTVA = {
    "Sun": "Fire",
    "Moon": "Water",
    "Mars": "Fire",
    "Mercury": "Air",
    "Jupiter": "Ether",
    "Venus": "Water",
    "Saturn": "Air",
    "Rahu": "Air",
    "Ketu": "Ether",
}

# Sign tattvas (in English: Fire, Earth, Air, Water)
SIGN_TATTVA = {
    "Aries": "Fire",
    "Leo": "Fire",
    "Sagittarius": "Fire",
    "Taurus": "Earth",
    "Virgo": "Earth",
    "Capricorn": "Earth",
    "Gemini": "Air",
    "Libra": "Air",
    "Aquarius": "Air",
    "Cancer": "Water",
    "Scorpio": "Water",
    "Pisces": "Water",
}

# Friendly tattvas (compatible elements)
TATTVA_RELATIONS = {
    "Fire": ["Air", "Fire"],
    "Water": ["Earth", "Water"],
    "Earth": ["Water", "Earth"],
    "Air": ["Fire", "Air"],
    "Ether": ["Air", "Fire", "Water", "Earth", "Ether"],
}

# Planetary dignity data
PLANETARY_DIGNITIES = {
    "Sun": {
        "element": "Fire",
        "exaltation": {"sign": "Aries", "degrees": 10},
        "debilitation": {"sign": "Libra", "degrees": 10},
        "own_signs": ["Leo"],
        "moolatrikona": {"sign": "Leo", "min_degrees": 0, "max_degrees": 20},
        "friend_planets": ["Moon", "Mars", "Jupiter"],
        "enemy_planets": ["Venus", "Saturn"],
        "neutral_planets": ["Mercury"],
    },
    "Moon": {
        "element": "Water",
        "exaltation": {"sign": "Taurus", "degrees": 3},
        "debilitation": {"sign": "Scorpio", "degrees": 3},
        "own_signs": ["Cancer"],
        "moolatrikona": {
            "sign": "Cancer",
            "min_degrees": 0,
            "max_degrees": 30,
        },  # Full sign for Moon
        "friend_planets": ["Sun", "Mercury"],
        "enemy_planets": [],
        "neutral_planets": ["Mars", "Jupiter", "Venus", "Saturn"],
    },
    "Mars": {
        "element": "Fire",
        "exaltation": {"sign": "Capricorn", "degrees": 28},
        "debilitation": {"sign": "Cancer", "degrees": 28},
        "own_signs": ["Aries", "Scorpio"],
        "moolatrikona": {"sign": "Aries", "min_degrees": 0, "max_degrees": 12},
        "friend_planets": ["Sun", "Moon", "Jupiter"],
        "enemy_planets": ["Mercury"],
        "neutral_planets": ["Venus", "Saturn"],
    },
    "Mercury": {
        "element": "Air",
        "exaltation": {"sign": "Virgo", "degrees": 15},
        "debilitation": {"sign": "Pisces", "degrees": 15},
        "own_signs": ["Gemini", "Virgo"],
        "moolatrikona": {"sign": "Virgo", "min_degrees": 15, "max_degrees": 20},
        "friend_planets": ["Saturn", "Venus"],
        "enemy_planets": ["Moon"],
        "neutral_planets": ["Sun", "Mars", "Jupiter"],
    },
    "Jupiter": {
        "element": "Ether",
        "exaltation": {"sign": "Cancer", "degrees": 5},
        "debilitation": {"sign": "Capricorn", "degrees": 5},
        "own_signs": ["Sagittarius", "Pisces"],
        "moolatrikona": {"sign": "Sagittarius", "min_degrees": 0, "max_degrees": 10},
        "friend_planets": ["Sun", "Moon", "Mars"],
        "enemy_planets": ["Mercury", "Venus"],
        "neutral_planets": ["Saturn"],
    },
    "Venus": {
        "element": "Water",
        "exaltation": {"sign": "Pisces", "degrees": 27},
        "debilitation": {"sign": "Virgo", "degrees": 27},
        "own_signs": ["Taurus", "Libra"],
        "moolatrikona": {"sign": "Taurus", "min_degrees": 0, "max_degrees": 10},
        "friend_planets": ["Mercury", "Saturn"],
        "enemy_planets": ["Sun", "Moon"],
        "neutral_planets": ["Mars", "Jupiter"],
    },
    "Saturn": {
        "element": "Air",
        "exaltation": {"sign": "Libra", "degrees": 20},
        "debilitation": {"sign": "Aries", "degrees": 20},
        "own_signs": ["Capricorn", "Aquarius"],
        "moolatrikona": {"sign": "Capricorn", "min_degrees": 0, "max_degrees": 20},
        "friend_planets": ["Mercury", "Venus"],
        "enemy_planets": ["Sun", "Moon", "Mars"],
        "neutral_planets": ["Jupiter"],
    },
    "Rahu": {
        "element": "Air",
        "exaltation": None,
        "debilitation": None,
        "own_signs": [],
        "moolatrikona": None,
        "friend_planets": [],
        "enemy_planets": [],
        "neutral_planets": [
            "Sun",
            "Moon",
            "Mars",
            "Mercury",
            "Jupiter",
            "Venus",
            "Saturn",
            "Ketu",
        ],
    },
    "Ketu": {
        "element": "Ether",
        "exaltation": None,
        "debilitation": None,
        "own_signs": [],
        "moolatrikona": None,
        "friend_planets": [],
        "enemy_planets": [],
        "neutral_planets": [
            "Sun",
            "Moon",
            "Mars",
            "Mercury",
            "Jupiter",
            "Venus",
            "Saturn",
            "Rahu",
        ],
    },
}

# Natural benefic/malefic classification
NATURAL_BENEFIC = ["Jupiter", "Venus", "Moon"]
NATURAL_MALEFIC = ["Sun", "Mars", "Saturn", "Rahu", "Ketu"]

# Sign lords
SIGN_LORDS = {
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
}

# Planetary relationships (friends, enemies, neutrals)
PLANETARY_RELATIONS = {
    "Sun": {
        "friends": ["Moon", "Mars", "Jupiter"],
        "enemies": ["Venus", "Saturn"],
        "neutrals": ["Mercury"],
    },
    "Moon": {
        "friends": ["Sun", "Mercury"],
        "enemies": [],
        "neutrals": ["Mars", "Jupiter", "Venus", "Saturn"],
    },
    "Mars": {
        "friends": ["Sun", "Moon", "Jupiter"],
        "enemies": ["Mercury"],
        "neutrals": ["Venus", "Saturn"],
    },
    "Mercury": {
        "friends": ["Sun", "Venus"],
        "enemies": ["Moon"],
        "neutrals": ["Mars", "Jupiter", "Saturn"],
    },
    "Jupiter": {
        "friends": ["Sun", "Moon", "Mars"],
        "enemies": ["Mercury", "Venus"],
        "neutrals": ["Saturn"],
    },
    "Venus": {
        "friends": ["Saturn", "Mercury"],
        "enemies": ["Sun", "Moon"],
        "neutrals": ["Mars", "Jupiter"],
    },
    "Saturn": {
        "friends": ["Mercury", "Venus"],
        "enemies": ["Sun", "Moon", "Mars"],
        "neutrals": ["Jupiter"],
    },
    # Nodes have no traditional friends/enemies, often neutral to all
    "Rahu": {
        "friends": [],
        "enemies": [],
        "neutrals": [
            "Sun",
            "Moon",
            "Mars",
            "Mercury",
            "Jupiter",
            "Venus",
            "Saturn",
            "Ketu",
        ],
    },
    "Ketu": {
        "friends": [],
        "enemies": [],
        "neutrals": [
            "Sun",
            "Moon",
            "Mars",
            "Mercury",
            "Jupiter",
            "Venus",
            "Saturn",
            "Rahu",
        ],
    },
}

# Divisional chart definitions (significances and divisions)
DIVISIONAL_CHARTS = {
    "D1": {
        "name": "Rashi",
        "significance": "Physical body and personality",
        "divisions": 12,
    },
    "D2": {"name": "Hora", "significance": "Wealth material prospects", "divisions": 2},
    "D3": {
        "name": "Drekkana",
        "significance": "Siblings and mental inclination",
        "divisions": 3,
    },
    "D4": {
        "name": "Chaturthamsa",
        "significance": "Property and assets",
        "divisions": 4,
    },
    "D7": {"name": "Saptamsa", "significance": "Children", "divisions": 7},
    "D9": {"name": "Navamsa", "significance": "Marriage and spouse", "divisions": 9},
    "D10": {
        "name": "Dashamsa",
        "significance": "Career and profession",
        "divisions": 10,
    },
    "D12": {"name": "Dwadashamsa", "significance": "Parents", "divisions": 12},
    "D16": {
        "name": "Shodashamsa",
        "significance": "Vehicles luxury and pleasures",
        "divisions": 16,
    },
    "D20": {
        "name": "Vimsamsa",
        "significance": "Spirituality worship",
        "divisions": 20,
    },
    "D24": {
        "name": "Chaturvimshamsa",
        "significance": "Education learning and knowledge",
        "divisions": 24,
    },
    "D27": {
        "name": "Bamsamsa",
        "significance": "Strengths and weaknesses",
        "divisions": 27,
    },
    "D30": {
        "name": "Trimsamsa",
        "significance": "Misfortunes and evils",
        "divisions": 30,
    },
    "D40": {
        "name": "Khavedamsa",
        "significance": "General auspiciousness",
        "divisions": 40,
    },
    "D45": {
        "name": "Aksharaviamdsansa",
        "significance": "Correspondence and letters",
        "divisions": 45,
    },
    "D60": {"name": "Shastyamsa", "significance": "All significances", "divisions": 60},
}

# --- STRENGTH CALCULATION CONSTANTS ---

# Bala Ratios for Vimshopaka and other calculations (JSM rel2vimshopakratio)
BALA_RELATION_RATIOS = {
    "MOOL": (20 / 20),
    "OWN": (20 / 20),
    "SWAYAM": (20 / 20),
    "ATHIMITRA": (18 / 20),
    "MITRA": (15 / 20),
    "SAMA": (10 / 20),
    "SHATRU": (7 / 20),
    "ATHISHATRU": (5 / 20),
}

# Vimshopaka divisional weights
VIMSHOPAKA_DIVISION_STRENGTHS = {
    "shadvarga": {"D1": 6, "D2": 2, "D3": 4, "D9": 5, "D12": 2, "D30": 1},
    "saptavarga": {"D1": 5, "D2": 2, "D3": 3, "D7": 2.5, "D9": 4.5, "D12": 2, "D30": 1},
    "dashavarga": {
        "D1": 3,
        "D2": 1.5,
        "D3": 1.5,
        "D7": 1.5,
        "D9": 1.5,
        "D10": 1.5,
        "D12": 1.5,
        "D16": 1.5,
        "D30": 1.5,
        "D60": 5,
    },
    "shodashavarga": {
        "D1": 3.5,
        "D2": 1,
        "D3": 1,
        "D4": 0.5,
        "D7": 0.5,
        "D9": 3,
        "D10": 0.5,
        "D12": 0.5,
        "D16": 2,
        "D20": 0.5,
        "D24": 0.5,
        "D27": 0.5,
        "D30": 1,
        "D40": 0.5,
        "D45": 0.5,
        "D60": 4,
    },
}

# Exaltation longitudes in decimal degrees
EXALTATION_DEGREES = {
    "Sun": 10.0,
    "Moon": 33.0,
    "Mars": 298.0,
    "Mercury": 165.0,
    "Jupiter": 95.0,
    "Venus": 357.0,
    "Saturn": 200.0,
}

# Saptavargaja Bala scores based on dignity
SAPTA_VARGAJA_SCORES = {
    "mool": 45,
    "own": 30,
    "ATHIMITRA": 22.5,
    "MITRA": 15,
    "SAMA": 7.5,
    "SHATRU": 3.75,
    "ATHISHATRU": 1.875,
}

# Planet genders for Ojha-Yugma Bala
PLANET_GENDERS = {
    "Sun": "male",
    "Moon": "female",
    "Mars": "male",
    "Mercury": "male",
    "Jupiter": "male",
    "Venus": "female",
    "Saturn": "male",
}

# Drekkana Bala: decanate index (0,1,2) for masculinity-based strength
# Masculine planets get strength in 1st decanate (0), Neutral in 2nd (1), Feminine in 3rd (2)
DEKANATE_STRENGTH = {
    "Sun": 0,
    "Mars": 0,
    "Jupiter": 0,  # Masculine
    "Mercury": 1,
    "Saturn": 1,  # Neutral
    "Moon": 2,
    "Venus": 2,  # Feminine
}

# Natural benefic/malefic classifications for Shadbala
NATURAL_BENEFIC_SHADBALA = ["Jupiter", "Venus", "Moon"]
NATURAL_MALEFIC_SHADBALA = ["Sun", "Mars", "Saturn"]

# Naisargika Bala (Natural Strength) in Virupas
NAISARGIKA_VALUES = {
    "Sun": 60.0,
    "Moon": 51.43,
    "Venus": 42.86,
    "Jupiter": 34.29,
    "Mercury": 25.71,
    "Mars": 17.14,
    "Saturn": 8.57,
}

# Minimum required Shadbala for planetary strength (in Rupas)
MIN_REQUIRED_SHADBALA = {
    "Sun": 6.5,  # Surya
    "Moon": 6.0,  # Chandra
    "Mars": 5.0,  # Mangal
    "Mercury": 7.0,  # Budha
    "Jupiter": 6.5,  # Guru
    "Venus": 5.5,  # Shukra
    "Saturn": 5.0,  # Shani
}

# Planets that receive shadbala calculations
PLANETS_WITH_SHADBALA = list(NAISARGIKA_VALUES.keys())

# Sputa Drishti (Planetary Aspect Strength) constants
SPUTA_DRISHTI_PLANETS = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]

# Special planetary aspect angles (in degrees)
MARS_SPECIAL_ASPECTS = [90, 210]  # 4th (90°) and 8th (210°) aspects
JUPITER_SPECIAL_ASPECTS = [120, 240]  # 5th (120°) and 9th (240°) aspects
SATURN_SPECIAL_ASPECTS = [60, 270]  # 3rd (60°) and 10th (270°) aspects

# Sputa Drishti aspect ranges (degrees)
SPUTA_ASPECT_RANGES = [
    (0, 30),
    (30, 60),
    (60, 90),
    (90, 120),
    (120, 150),
    (150, 180),
    (180, 210),
    (210, 240),
    (240, 270),
    (270, 300),
    (300, 330),
    (330, 360),
]

# Full aspect strength value
FULL_ASPECT_STRENGTH = 60.0

# Aspect orb for special aspects (± degrees)
SPECIAL_ASPECT_ORB = 15.0

# Kendra Bala (Angular Strength) scores
KENDRA_BALA_SCORES = {
    1: 60,
    4: 60,
    7: 60,
    10: 60,  # Kendras
    2: 30,
    5: 30,
    8: 30,
    11: 30,  # Panapharas
    3: 15,
    6: 15,
    9: 15,
    12: 15,  # Apoklimas
}

# Mean geocentric velocities (degrees/day) for Chesta Bala reference
MEAN_VELOCITIES = {
    "Mars": 0.524,
    "Mercury": 1.383,
    "Jupiter": 0.083,
    "Venus": 1.602,
    "Saturn": 0.034,
}

# Mean Daily Motion for Cheshta Bala calculation (degrees/day)
# As per classical astronomical texts (e.g., Surya Siddhanta)
PLANET_MEAN_MOTION = {
    "Mars": 0.5240,
    "Mercury": 4.0923,
    "Jupiter": 0.0831,
    "Venus": 1.6021,
    "Saturn": 0.0334,
}

# --- STRENGTH CALCULATION CONSTANTS ---
# Additional constants specific to strength calculations
RUPA_SCALING = 60.0  # Standard Rupas scale (0-60)
SIGN_DEGREES = 30.0  # Degrees per zodiac sign
HOUSES_COUNT = 12  # Number of houses/zodiac signs
WEEKDAYS_COUNT = 7  # Days in a week
VELC = 1.0  # Default velocity constant for unknown planets
PUCHC = 3.0  # Uchhabala division factor
DIGBAL_DIVISOR = 3.0  # Digbala angular division factor
AYANA_DECL_ADJUST = 24.0  # Ayana bala declination adjustment
AYANA_DECL_RANGE = 48.0  # Ayana bala declination range
AYANA_MULTIPLIER = 2.0  # Sun's Ayana bala multiplier
ASH_ANGULAR_BOUNDARY = 180.0  # Reference angle for angular difference calculations
DEFAULT_PRECISION = 3  # Default decimal places for rounding

# Planet Diameter Ratios (for Yuddha Bala)
PLANET_DIAMETERS = {
    "Mars": 1.5,
    "Mercury": 1.0,
    "Jupiter": 3.5,
    "Venus": 1.6,
    "Saturn": 3.0,
}

# --- STRENGTH CALCULATION CONSTANTS (SHADBALA) ---

# Ojha-Yugma Bala gender classifications
MALE_PLANETS_SHADBALA = ["Sun", "Mars", "Mercury", "Jupiter", "Saturn"]
FEMALE_PLANETS_SHADBALA = ["Moon", "Venus"]

# Drekkana Bala planet index map and decanate groups
PLANET_INDEX_MAP = {
    "Sun": 0,
    "Moon": 1,
    "Mars": 2,
    "Mercury": 3,
    "Jupiter": 4,
    "Venus": 5,
    "Saturn": 6,
}
DECANATE_RULER_GROUPS = {
    0: [0, 2, 4],  # First decanate: Sun, Mars, Jupiter (Masculine)
    1: [3, 6],  # Second decanate: Mercury, Saturn (Neutral)
    2: [1, 5],  # Third decanate: Moon, Venus (Feminine)
}

# Dig Bala strong houses mapping
DIGBALA_STRONG_HOUSES = {
    "Sun": 10,
    "Moon": 4,
    "Mars": 10,
    "Mercury": 1,
    "Jupiter": 1,
    "Venus": 4,
    "Saturn": 7,
}

# Tribhaga Bala day and night lords
TRIBHAGA_DAY_LORDS = ["Sun", "Mercury", "Saturn"]
TRIBHAGA_NIGHT_LORDS = ["Moon", "Venus", "Mars"]

# Varsha-Maasa-Dina-Hora Bala constants
WEEKDAY_LORDS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
# Planetary hour sequence (Sun->Venus->Mercury->Moon->Saturn->Jupiter->Mars)
# Indices correspond to daylord list: [Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn]
PLANETARY_HOUR_SEQUENCE = [0, 5, 3, 1, 6, 4, 2]

# Yuddha Bala planets that can engage in war
YUDDHABALA_PLANETS = ["Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

# Planetary Hour Sequence (Vedic: Sun->Venus->Mercury->Moon->Saturn->Jupiter->Mars)
# Indices correspond to daylord list: [Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn]
VEDIC_HORA_SEQUENCE = [0, 5, 3, 1, 6, 4, 2]

# --- BHAVA BALA CONSTANTS (REFACTORED) ---

# MODIFIED: Defines the nature of signs for Bhava Dig Bala.
# This serves as a base map; dual-nature signs are handled in the main logic.
SIGN_NATURE_MAP = {
    "Aries": "chatuspadha",
    "Taurus": "chatuspadha",
    "Gemini": "nara",
    "Cancer": "jalachara",
    "Leo": "chatuspadha",
    "Virgo": "nara",
    "Libra": "nara",
    "Scorpio": "keeta",
    "Sagittarius": "chatuspadha",
    "Capricorn": "chatuspadha",
    "Aquarius": "nara",
    "Pisces": "jalachara",
}

# MODIFIED: Renamed and confirmed patterns for Bhava Dig Bala calculation.
BHAVA_STRENGTH_FROM_SIGN_NATURE = {
    "nara": [60, 50, 40, 30, 20, 10, 0, 10, 20, 30, 40, 50],  # Humans
    "jalachara": [30, 40, 50, 60, 50, 40, 30, 20, 10, 0, 10, 20],  # Aquatic
    "chatuspadha": [30, 20, 10, 0, 10, 20, 30, 40, 50, 60, 50, 40],  # Quadrupeds
    "keeta": [0, 10, 20, 30, 40, 50, 60, 50, 40, 30, 20, 10],  # Insects
}

# Sign nature classification for Bhava Dig Bala, including half-sign variations
SIGN_NATURE_CLASSIFICATION = {
    "Aries": "chatuspadha",
    "Taurus": "chatuspadha",
    "Gemini": "nara",
    "Cancer": "jalachara",
    "Leo": "chatuspadha",
    "Virgo": "nara",
    "Libra": "nara",
    "Scorpio": "keeta",
    "Sagittarius_first_half": "nara",
    "Sagittarius_second_half": "chatuspadha",
    "Capricorn_first_half": "chatuspadha",
    "Capricorn_second_half": "jalachara",
    "Aquarius": "nara",
    "Pisces": "jalachara",
}

# --- VIMSHOTTARI DASHA CONSTANTS (CORRECTED) ---

# The full 120-year cycle duration for each of the 9 grahas
VIMSHOTTARI_DASHA_DURATIONS = {
    "Ketu": 7,
    "Venus": 20,
    "Sun": 6,
    "Moon": 10,
    "Mars": 7,
    "Rahu": 18,
    "Jupiter": 16,
    "Saturn": 19,
    "Mercury": 17,
}

# The correct, standard sequence of Vimshottari Dasha lords
VIMSHOTTARI_ADHIPATI_LIST = [
    "Ketu",
    "Venus",
    "Sun",
    "Moon",
    "Mars",
    "Rahu",
    "Jupiter",
    "Saturn",
    "Mercury",
]

# Total duration of the Vimshottari cycle in years
HUMAN_LIFE_SPAN_FOR_VIMSHOTTARI = 120.0

# Standard year duration in days for dasha calculations (sidereal year)
YEAR_DURATION_DAYS = 365.25636

# Dasha level names for output clarity
DASHA_LEVEL_NAMES = {
    1: "mahadasha",
    2: "antardasha",
    3: "pratyantardasha",
    4: "sukshmadasha",
    5: "pranadasha",
}
