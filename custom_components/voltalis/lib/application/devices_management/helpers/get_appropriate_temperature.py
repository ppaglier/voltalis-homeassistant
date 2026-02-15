from custom_components.voltalis.lib.application.devices_management.dtos.device_dto import DeviceDto
from custom_components.voltalis.lib.domain.devices_management.devices.device_enum import DeviceModeEnum


def get_appropriate_temperature(
    device: DeviceDto,
    mode: DeviceModeEnum,
    *,
    default_temperature: float,
    default_away_temperature: float,
    default_eco_temperature: float,
    default_comfort_temperature: float,
    use_device_programming: bool = True,
    temperature: float | None = None,
) -> float:
    """Determine the appropriate temperature based on mode and device programming."""

    if temperature is not None:
        return temperature

    if use_device_programming:
        # Use device programming temperature if available
        if device.programming.temperature_target:
            return device.programming.temperature_target

        # Use default temperature from device programming
        if device.programming.default_temperature:
            return device.programming.default_temperature

    mode_mapping = {
        DeviceModeEnum.HORS_GEL: default_away_temperature,
        DeviceModeEnum.ECO: default_eco_temperature,
        DeviceModeEnum.ECOV: default_eco_temperature,
        DeviceModeEnum.CONFORT: default_comfort_temperature,
    }

    return mode_mapping.get(mode, default_temperature)
