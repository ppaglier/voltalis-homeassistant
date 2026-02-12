from custom_components.voltalis.const import CLIMATE_COMFORT_TEMP, CLIMATE_DEFAULT_TEMP
from custom_components.voltalis.lib.application.devices_management.dtos.device_dto import DeviceDto
from custom_components.voltalis.lib.domain.devices_management.device.device_enum import DeviceModeEnum


def get_appropriate_temperature(
    device: DeviceDto,
    mode: DeviceModeEnum,
    specified_temperature: float | None = None,
) -> float:
    """Determine the appropriate temperature based on mode and device programming."""

    if specified_temperature is not None:
        return specified_temperature

    # Use device programming temperature if available
    if device.programming.temperature_target:
        return device.programming.temperature_target

    # Use default temperature from device programming
    if device.programming.default_temperature:
        return device.programming.default_temperature

    # Fallbacks based on mode
    if mode == DeviceModeEnum.CONFORT:
        return CLIMATE_COMFORT_TEMP

    # Fallback to constant
    return CLIMATE_DEFAULT_TEMP
