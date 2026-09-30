from datetime import date, time

from custom_components.voltalis.lib.domain.devices_management.consumptions.device_consumption import (
    ConsumptionRecord,
    DeviceConsumption,
)
from custom_components.voltalis.lib.domain.shared.providers.voltalis_provider import VoltalisProvider


class GetDevicesDailyConsumptionHandler:
    """Handler to get the daily consumption for all devices."""

    def __init__(
        self,
        *,
        voltalis_provider: VoltalisProvider,
    ):
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
        consumption_records: list[ConsumptionRecord],
        target_time: time | None,
    ) -> DeviceConsumption:
        filtered_records = (
            self.get_consumptions_for_hour(records=consumption_records, target_time=target_time)
            if target_time is not None
            else consumption_records
        )
        return DeviceConsumption(daily_consumption_records=filtered_records)

    def get_consumptions_for_hour(
        self,
        *,
        records: list[ConsumptionRecord],
        target_time: time,
    ) -> list[ConsumptionRecord]:
        target_hour = target_time.replace(minute=0, second=0, microsecond=0)

        return [
            record
            for record in records
            if record.timestamp.replace(minute=0, second=0, microsecond=0).time() < target_hour
        ]
