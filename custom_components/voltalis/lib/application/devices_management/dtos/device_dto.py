from custom_components.voltalis.lib.domain.devices_management.climate.manual_setting import ManualSetting
from custom_components.voltalis.lib.domain.devices_management.device.device import Device


class VoltalisDeviceDto(Device):
    """Data class to hold device information."""

    manual_setting: ManualSetting | None = None
