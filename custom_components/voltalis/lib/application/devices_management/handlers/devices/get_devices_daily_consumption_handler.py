from datetime import date, datetime, time

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

    async def handle(self, target_date: date, target_time: time | None = None) -> dict[int, DeviceConsumption]:
        """Get consumption for a date, optionally limited to completed hours."""

        devices_daily_consumptions = await self.__voltalis_provider.get_devices_daily_consumptions(target_date)
        devices_consumptions = {
            device_id: self.get_device_consumption(
                consumption_records=consumption_records,
                target_time=target_time,
            )
            for device_id, consumption_records in devices_daily_consumptions.items()
        }
        return devices_consumptions

    def get_device_consumption(
        self,
        *,
        consumption_records: list[tuple[datetime, float]],
        target_time: time | None,
    ) -> DeviceConsumption:
        filtered_consumptions = (
            self.get_consumptions_for_hour(consumptions=consumption_records, target_time=target_time)
            if target_time is not None
            else consumption_records
        )
        return DeviceConsumption(
            daily_consumption=sum([consumption for (_, consumption) in filtered_consumptions], 0.0),
            daily_consumption_records=filtered_consumptions,
        )

    def get_consumptions_for_hour(
        self,
        *,
        consumptions: list[tuple[datetime, float]],
        target_time: time,
    ) -> list[tuple[datetime, float]]:
        target_hour = target_time.replace(minute=0, second=0, microsecond=0)

        return [
            (date, consumption)
            for (date, consumption) in consumptions
            if date.replace(minute=0, second=0, microsecond=0).time() < target_hour
        ]
