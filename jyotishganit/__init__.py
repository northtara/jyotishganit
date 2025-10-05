"""
jyotishganit: High precision Vedic astrology calculations in Python.

A comprehensive library for generating complete Vedic horoscopes with
traditional Indian astrological elements including planetary positions,
ayanamsa calculations, divisional charts, and strength analyses.
"""

from .main import calculate_birth_chart, get_birth_chart_json, get_birth_chart_json_string
from .core.models import Person, VedicBirthChart

__version__ = "0.1.0"
__all__ = ['calculate_birth_chart', 'get_birth_chart_json', 'get_birth_chart_json_string', 'Person', 'VedicBirthChart']
