from datetime import datetime, timedelta

from custom_components.voltalis.lib.domain.devices_management.consumptions.device_consumption import (
    DeviceConsumption,
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
        self.__voltalis_provider = voltalis_provider

    async def handle(self) -> dict[int, DeviceConsumption]:
        """Handle the request to get the daily consumption for all devices."""

        # We remove 1 hour because we can't fetch data from the current hour
        target_datetime = self.__date_provider.get_now() - timedelta(hours=1)

        devices_daily_consumptions = await self.__voltalis_provider.get_devices_daily_consumptions(
            target_datetime.date()
        )
        devices_consumptions = {
            device_id: DeviceConsumption(
                daily_consumption=self.get_consumption_for_hour(
                    consumptions=consumption_records,
                    target_datetime=target_datetime,
                )
            )
            for device_id, consumption_records in devices_daily_consumptions.items()
        }
        return devices_consumptions

    def get_consumption_for_hour(
        self,
        *,
        consumptions: list[tuple[datetime, float]],
        target_datetime: datetime,
    ) -> float:
        target_hour = target_datetime.replace(minute=0, second=0, microsecond=0)

        return sum(
            [
                consumption
                for (date, consumption) in consumptions
                if date.replace(minute=0, second=0, microsecond=0) <= target_hour
            ],
            0.0,
        )
