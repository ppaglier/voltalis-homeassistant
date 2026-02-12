from custom_components.voltalis.lib.application.devices_management.dtos.device_dto import DeviceDto
from custom_components.voltalis.lib.domain.devices_management.water_heaters.water_heater_current_operations_enum import (  # noqa: E501
    WaterHeaterCurrentOperationEnum,
)
from custom_components.voltalis.lib.domain.shared.custom_model import CustomModel


class SetWaterHeaterOperationCommand(CustomModel):
    """Command to set the operation mode for a water heater device.

    Attributes:
        device: The device to update
        operation_mode: The operation mode to set (ON, OFF, AUTO)
    """

    device: DeviceDto
    manual_setting_id: int
    operation_mode: WaterHeaterCurrentOperationEnum
