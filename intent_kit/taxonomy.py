from typing import Any, Dict, Optional, Type, get_type_hints
from dataclasses import dataclass
import inspect


@dataclass
class Intent:
    """Base class for all intent types."""

    def __post_init__(self):
        """Validate parameters after initialization."""
        type_hints = get_type_hints(self.__class__)
        for field_name, field_value in self.__dict__.items():
            if field_name in type_hints:
                expected_type = type_hints[field_name]
                if not isinstance(field_value, expected_type):
                    raise TypeError(
                        f"Parameter '{field_name}' must be of type {expected_type}, "
                        f"got {type(field_value)}"
                    )


class IntentTaxonomy:
    """Base class for intent taxonomies."""

    def __init__(self):
        """Initialize the taxonomy."""
        self._intents: Dict[str, Type[Intent]] = {}
        self._discover_intents()

    def _discover_intents(self):
        """Discover all Intent subclasses defined in this taxonomy."""
        for name, value in inspect.getmembers(self.__class__):
            if (
                isinstance(value, type)
                and issubclass(value, Intent)
                and value is not Intent
            ):
                self._intents[name] = value

    def get_intents(self) -> Dict[str, Type[Intent]]:
        """Get all discovered intents."""
        return self._intents.copy()

# Example taxonomy for testing
