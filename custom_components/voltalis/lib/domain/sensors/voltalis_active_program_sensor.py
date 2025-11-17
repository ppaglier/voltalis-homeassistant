"""Voltalis active program sensor."""

from homeassistant.components.sensor import SensorEntity

from custom_components.voltalis.lib.domain.voltalis_entity import VoltalisEntity


class VoltalisActiveProgramSensor(VoltalisEntity, SensorEntity):
    """Representation of a Voltalis active program sensor."""

    _attr_icon = "mdi:calendar-check"
    _attr_translation_key = "active_program"

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        data = self.coordinator.data.get(self.device_id)
        if data is None or not data.programs:
            return None

        # Find the first enabled program
        enabled_programs = [p for p in data.programs if p.enabled]
        if not enabled_programs:
            return "None"

        return enabled_programs[0].name

    @property
    def extra_state_attributes(self) -> dict[str, any]:
        """Return additional state attributes."""
        data = self.coordinator.data.get(self.device_id)
        if data is None or not data.programs:
            return {}

        enabled_programs = [p for p in data.programs if p.enabled]
        if not enabled_programs:
            return {}

        active_program = enabled_programs[0]
        return {
            "program_type": active_program.program_type,
            "program_name": active_program.program_name,
            "until_further_notice": active_program.until_further_notice,
            "end_date": active_program.end_date,
            "geoloc_currently_on": active_program.geoloc_currently_on,
            "all_programs": [p.name for p in data.programs],
        }
