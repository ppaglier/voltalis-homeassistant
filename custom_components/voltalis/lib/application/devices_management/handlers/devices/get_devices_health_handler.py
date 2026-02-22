from custom_components.voltalis.lib.domain.devices_management.health.device_health import DeviceHealth
from custom_components.voltalis.lib.domain.shared.providers.voltalis_provider import VoltalisProvider


class GetDevicesHealthHandler:
    """Handler to get the health of the devices."""

    def __init__(
        self,
        *,
        voltalis_provider: VoltalisProvider,
    ):
        self.__voltalis_provider = voltalis_provider

    async def handle(self) -> dict[int, DeviceHealth]:
        """Handle the request to get the health of the devices."""

        result = await self.__voltalis_provider.get_devices_health()
        return result
