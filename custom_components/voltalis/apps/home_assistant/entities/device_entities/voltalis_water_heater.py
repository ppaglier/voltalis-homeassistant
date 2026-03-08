from typing import Any

from homeassistant.components.water_heater import WaterHeaterEntity, WaterHeaterEntityFeature

from custom_components.voltalis.apps.home_assistant.coordinators.device import DeviceDto
from custom_components.voltalis.apps.home_assistant.entities.base_entities.voltalis_device_entity import (
    VoltalisDeviceEntity,
)
from custom_components.voltalis.apps.home_assistant.entities.config_entry_data import VoltalisConfigEntry
from custom_components.voltalis.const import CLIMATE_UNIT
from custom_components.voltalis.lib.application.devices_management.commands.set_water_heater_operation_command import (
    SetWaterHeaterOperationCommand,
)
from custom_components.voltalis.lib.application.devices_management.queries.get_water_heater_current_operation_query import (  # noqa: E501
    GetWaterHeaterCurrentOperationQuery,
)
from custom_components.voltalis.lib.domain.devices_management.devices.device import Device
from custom_components.voltalis.lib.domain.devices_management.water_heaters.water_heater_current_operations_enum import (  # noqa: E501
    WaterHeaterCurrentOperationEnum,
)


class VoltalisWaterHeater(VoltalisDeviceEntity, WaterHeaterEntity):
    """Water heater entity for Voltalis water heater devices.

    This is a relay controller with 3 states:
    - ON: Manually forced on
    - OFF: Manually forced off (cut off regardless of HP/HC contactor)
    - AUTO: Voltalis controls the device according to its programming

    Note: When ON, it doesn't mean actively heating - depends on HP/HC contactors.
    """

    _attr_temperature_unit = CLIMATE_UNIT
    _attr_translation_key = "water_heater"
    _unique_id_suffix = "water_heater"

    def __init__(self, entry: VoltalisConfigEntry, device: DeviceDto) -> None:
        """Initialize the water heater entity."""
        super().__init__(entry, device, entry.runtime_data.voltalis_home_assistant_module.device_coordinator)
        # We don't set name there because this is only one entity per device
        # and the device name is already used for the main entity.
        self._attr_name = None

        # Water heater supports ON/OFF and operation modes (ON, OFF, AUTO)
        self._attr_supported_features = (
            WaterHeaterEntityFeature.ON_OFF
            | WaterHeaterEntityFeature.OPERATION_MODE
            | WaterHeaterEntityFeature.AWAY_MODE
        )
        self._attr_operation_list = [operation for operation in WaterHeaterCurrentOperationEnum]
        self._attr_is_away_mode_on = False
        self.__before_away_mode_operation: WaterHeaterCurrentOperationEnum | None = None

    @property
    def _current_device(self) -> DeviceDto:
        """Get the current device data from coordinator."""
        device = self._voltalis_module.device_coordinator.data.get(self._device.id)
        return device if device else self._device

    @property
    def icon(self) -> str:
        """Return the icon to use for this entity."""
        current = self.current_operation
        if current is not None:
            if current == WaterHeaterCurrentOperationEnum.ON:
                return "mdi:water-boiler"
            if current == WaterHeaterCurrentOperationEnum.OFF:
                return "mdi:water-boiler-off"
            if current == WaterHeaterCurrentOperationEnum.AUTO:
                return "mdi:water-boiler-auto"
        return "mdi:water-boiler-alert"

    # ------------------------------------------------------------------
    # Operation mode handling
    # ------------------------------------------------------------------

    @property
    def current_operation(self) -> WaterHeaterCurrentOperationEnum | None:
        """Return current operation mode: on, off, or auto."""
        device = self._current_device

        return self._voltalis_module.get_water_heater_current_operation_handler.handle(
            GetWaterHeaterCurrentOperationQuery(
                is_on=device.programming.is_on,
                prog_type=device.programming.prog_type,
            )
        )

    async def async_set_operation_mode(self, operation_mode: str) -> None:
        """Set new operation mode: on, off, or auto."""

        self._attr_is_away_mode_on = False

        await self._voltalis_module.set_water_heater_operation_handler.handle(
            SetWaterHeaterOperationCommand(
                device=self._current_device,
                operation_mode=WaterHeaterCurrentOperationEnum(operation_mode),
            )
        )

        await self.coordinator.async_request_refresh()

    # ------------------------------------------------------------------
    # Away mode handling
    # ------------------------------------------------------------------

    async def async_turn_away_mode_on(self) -> None:
        """Enable away mode by turning off the water heater."""
        self.__before_away_mode_operation = self.current_operation
        await self.async_set_operation_mode(WaterHeaterCurrentOperationEnum.OFF)
        self._attr_is_away_mode_on = True

    async def async_turn_away_mode_off(self) -> None:
        """Disable away mode by returning to automatic operation."""
        await self.async_set_operation_mode(self.__before_away_mode_operation or WaterHeaterCurrentOperationEnum.AUTO)
        self._attr_is_away_mode_on = False

    # ------------------------------------------------------------------
    # On/Off handling
    # ------------------------------------------------------------------

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the water heater on."""
        await self.async_set_operation_mode(WaterHeaterCurrentOperationEnum.ON)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the water heater off."""
        await self.async_set_operation_mode(WaterHeaterCurrentOperationEnum.OFF)

    # ------------------------------------------------------------------
    # Availability handling override
    # ------------------------------------------------------------------
    def _is_available_from_data(self, data: Device) -> bool:
        return data.programming.is_on is not None and data.programming.mode is not None
