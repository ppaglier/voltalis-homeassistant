from custom_components.voltalis.lib.domain.devices_management.climates.manual_setting import ManualSetting
from custom_components.voltalis.lib.domain.devices_management.devices.device import Device


class DeviceDto(Device):
    """Data class to hold device information."""

    manual_setting: ManualSetting | None = None
