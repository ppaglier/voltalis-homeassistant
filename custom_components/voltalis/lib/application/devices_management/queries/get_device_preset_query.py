from custom_components.voltalis.lib.domain.devices_management.devices.device_enum import DeviceModeEnum
from custom_components.voltalis.lib.domain.programs_management.programs.program_enum import ProgramTypeEnum
from custom_components.voltalis.lib.domain.shared.custom_model import CustomModel


class GetDevicePresetQuery(CustomModel):
    """Query to get the current preset of devices."""

    is_on: bool
    prog_type: ProgramTypeEnum
    mode: DeviceModeEnum | None = None
    climate_mode: bool = False
