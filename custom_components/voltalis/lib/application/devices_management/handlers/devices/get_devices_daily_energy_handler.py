from datetime import date, time

from custom_components.voltalis.lib.domain.devices_management.energy.device_energy import DeviceEnergy, EnergyRecord
from custom_components.voltalis.lib.domain.shared.providers.voltalis_provider import VoltalisProvider


class GetDevicesDailyEnergyHandler:
    """Handler to get the daily energy for all devices."""

    def __init__(
        self,
        *,
        voltalis_provider: VoltalisProvider,
    ):
        self.__voltalis_provider = voltalis_provider

    async def handle(self, target_date: date, target_time: time | None = None) -> dict[int, DeviceEnergy]:
        """Get energy for a date, optionally limited to completed hours."""

        devices_daily_energy = await self.__voltalis_provider.get_devices_daily_energy(target_date)
        devices_energy = {
            device_id: self._get_device_energy(
                records=records,
                target_time=target_time,
            )
            for device_id, records in devices_daily_energy.items()
        }
        return devices_energy

    def _get_device_energy(
        self,
        *,
        records: list[EnergyRecord],
        target_time: time | None,
    ) -> DeviceEnergy:
        filtered_records = (
            self._get_energy_for_hour(records=records, target_time=target_time) if target_time is not None else records
        )
        return DeviceEnergy(daily_energy_records=filtered_records)

    def _get_energy_for_hour(
        self,
        *,
        records: list[EnergyRecord],
        target_time: time,
    ) -> list[EnergyRecord]:
        target_hour = target_time.replace(minute=0, second=0, microsecond=0)

        return [
            record
            for record in records
            if record.timestamp.replace(minute=0, second=0, microsecond=0).time() < target_hour
        ]
