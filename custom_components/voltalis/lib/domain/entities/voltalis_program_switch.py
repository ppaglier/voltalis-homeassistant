from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from custom_components.voltalis.const import DOMAIN
from custom_components.voltalis.lib.domain.config_entry_data import VoltalisConfigEntry
from custom_components.voltalis.lib.domain.coordinators.program import VoltalisProgramCoordinator
from custom_components.voltalis.lib.domain.models.program import VoltalisProgram, VoltalisProgramTypeEnum


class VoltalisProgramSwitch(CoordinatorEntity[VoltalisProgramCoordinator], SwitchEntity):
    """Switch entity representing a Voltalis program."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:calendar-clock"

    def __init__(
        self,
        entry: VoltalisConfigEntry,
        program: VoltalisProgram,
        coordinator: VoltalisProgramCoordinator,
    ) -> None:
        """Initialize the program switch entity."""
        super().__init__(coordinator)
        self._entry = entry
        self._program_id = program.id

        # Unique id for Home Assistant
        self._attr_unique_id = f"program_{program.id}"
        self._attr_name = None  # Use device name

        # Device info - each program is its own device
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"program_{program.id}")},
            name=program.name.capitalize(),
            manufacturer="Voltalis",
            model=self._get_program_model(program),
            entry_type="service",
        )

    @property
    def unique_internal_name(self) -> str:
        """Return a unique internal name for the entity."""
        program = self._get_program()
        if program:
            return f"{program.name.lower()}_program_{self._program_id}"
        return f"program_{self._program_id}"

    def _get_program(self) -> VoltalisProgram | None:
        """Get the current program data from coordinator."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get(self._program_id)

    def _get_program_model(self, program: VoltalisProgram) -> str:
        """Return the model string based on program type."""
        if program.program_type == VoltalisProgramTypeEnum.USER:
            return "User Program"
        return "Default Program"

    @property
    def is_on(self) -> bool | None:
        """Return True if the program is enabled."""
        program = self._get_program()
        if program is None:
            return None
        return program.enabled

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.last_update_success and self._get_program() is not None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        program = self._get_program()
        if program is None:
            return {}
        return {
            "program_type": program.program_type.value,
            "program_id": program.id,
        }

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on (enable) the program."""
        program = self._get_program()
        if program is None:
            return

        await self.coordinator.set_program_state(program, enabled=True)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off (disable) the program."""
        program = self._get_program()
        if program is None:
            return

        await self.coordinator.set_program_state(program, enabled=False)
        await self.coordinator.async_request_refresh()

