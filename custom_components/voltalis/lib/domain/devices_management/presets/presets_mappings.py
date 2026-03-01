from custom_components.voltalis.lib.domain.devices_management.devices.device_enum import DeviceModeEnum
from custom_components.voltalis.lib.domain.devices_management.presets.preset_enum import DeviceCurrentPresetEnum

PRESET_MODE_MAPPING = {
    DeviceCurrentPresetEnum.ON: DeviceModeEnum.ON,
    DeviceCurrentPresetEnum.COMFORT: DeviceModeEnum.COMFORT,
    DeviceCurrentPresetEnum.ECO: DeviceModeEnum.ECO,
    DeviceCurrentPresetEnum.AWAY: DeviceModeEnum.AWAY,
    DeviceCurrentPresetEnum.TEMPERATURE: DeviceModeEnum.TEMPERATURE,
}

MODE_PRESET_MAPPING = {v: k for k, v in PRESET_MODE_MAPPING.items()}
