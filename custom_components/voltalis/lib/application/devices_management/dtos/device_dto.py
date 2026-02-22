from custom_components.voltalis.lib.domain.devices_management.climates.manual_setting import ManualSetting
from custom_components.voltalis.lib.domain.devices_management.devices.device import Device


class DeviceDto(Device):
    """Data class to hold device information."""

    manual_setting: ManualSetting | None = None

    @staticmethod
    def from_device(device: Device, manual_setting: ManualSetting | None = None) -> "DeviceDto":
        """Create a DeviceDto from a Device and an optional ManualSetting."""
        return DeviceDto(
            **device.model_dump(),
            manual_setting=manual_setting,
        )
