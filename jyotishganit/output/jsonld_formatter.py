"""
JSON-LD formatting for jyotishganit.

Provides structured JSON-LD output based on custom vocabulary.
The models handle the to_dict conversion, this module is for extensions.
"""

from typing import Any

try:
    from ..core.models import VedicBirthChart
except ImportError:
    from jyotishganit.core.models import VedicBirthChart


def format_chart(chart: VedicBirthChart) -> dict[str, Any]:
    """Format birth chart as JSON-LD."""
    return chart.to_dict()


# For future use, e.g., custom contexts or validations
