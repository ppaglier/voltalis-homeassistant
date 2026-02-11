from datetime import timedelta

from custom_components.voltalis.lib.domain.devices_management.consumption.device_consumption import (
    VoltalisDeviceConsumption,
)
from custom_components.voltalis.lib.domain.shared.providers.date_provider import DateProvider
from custom_components.voltalis.lib.domain.shared.providers.voltalis_provider import VoltalisProvider


class GetDevicesDailyConsumptionHandler:
    """Handler to get the daily consumption for all devices."""

    def __init__(
        self,
        *,
        date_provider: DateProvider,
        voltalis_provider: VoltalisProvider,
    ):
        self.__date_provider = date_provider
        self._voltalis_provider = voltalis_provider

    async def handle(self) -> dict[int, VoltalisDeviceConsumption]:
        """Handle the request to get the daily consumption for all devices."""

        # We remove 1 hour because we can't fetch data from the current hour
        target_datetime = self.__date_provider.get_now() - timedelta(hours=1)

        result = await self._voltalis_provider.get_devices_daily_consumptions(target_datetime)
        return result
