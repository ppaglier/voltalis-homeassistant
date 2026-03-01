from typing import TYPE_CHECKING

from homeassistant import config_entries

# Prevent circular import for type checking
if TYPE_CHECKING:
    from custom_components.voltalis.apps.home_assistant.home_assistant_module import VoltalisHomeAssistantModule


class VoltalisConfigEntryData:
    """Config entry for the Voltalis data"""

    def __init__(self, *, voltalis_home_assistant_module: "VoltalisHomeAssistantModule") -> None:
        self.voltalis_home_assistant_module = voltalis_home_assistant_module


VoltalisConfigEntry = config_entries.ConfigEntry[VoltalisConfigEntryData]
