from logging import Logger

from custom_components.voltalis.lib.application.devices_management.dtos.device_dto import DeviceDto
from custom_components.voltalis.lib.domain.devices_management.device.device_enum import DeviceTypeEnum
from custom_components.voltalis.lib.domain.shared.providers.voltalis_provider import VoltalisProvider


class GetDevicesHandler:
    """Handler to get the devices."""

    def __init__(
        self,
        *,
        logger: Logger,
        voltalis_provider: VoltalisProvider,
    ):
        self.__logger = logger
        self.__voltalis_provider = voltalis_provider

    async def handle(self) -> dict[int, DeviceDto]:
        """Handle the request to get the devices."""

        # Fetch devices and manual settings
        devices = await self.__voltalis_provider.get_devices()
        devices_manual_settings = await self.__voltalis_provider.get_manual_settings()

        result: dict[int, DeviceDto] = {}
        for device_id, device in devices.items():
            if device.type not in [DeviceTypeEnum.HEATER, DeviceTypeEnum.WATER_HEATER]:
                self.__logger.debug(f"Skipping unsupported device type: {device.type}")
                continue

            result[device_id] = DeviceDto(
                **device.model_dump(),
                manual_setting=devices_manual_settings.get(device_id),
            )

        return result
