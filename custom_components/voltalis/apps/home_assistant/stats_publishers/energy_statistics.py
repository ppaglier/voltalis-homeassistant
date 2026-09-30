from __future__ import annotations

import asyncio
from collections import defaultdict
from datetime import date, datetime, timedelta
from typing import Callable

from homeassistant.components.recorder.models import StatisticData, StatisticMeanType, StatisticMetaData
from homeassistant.components.recorder.statistics import (
    async_add_external_statistics,
    get_last_statistics,
    statistics_during_period,
)
from homeassistant.const import UnitOfEnergy
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.recorder import get_instance
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util
from homeassistant.util.unit_conversion import EnergyConverter

from custom_components.voltalis.apps.home_assistant.coordinators.base import BaseVoltalisCoordinator
from custom_components.voltalis.const import DOMAIN
from custom_components.voltalis.lib.application.devices_management.dtos.device_dto import DeviceDto
from custom_components.voltalis.lib.application.devices_management.handlers.devices.get_devices_daily_consumption_handler import (  # noqa: E501
    GetDevicesDailyConsumptionHandler,
)
from custom_components.voltalis.lib.domain.devices_management.consumptions.device_consumption import DeviceConsumption
from custom_components.voltalis.lib.domain.energy_contracts.energy_contract import EnergyContract
from custom_components.voltalis.lib.domain.energy_contracts.energy_contract_enum import EnergyContractTypeEnum


class VoltalisEnergyStatisticsPublisher:
    """Publish Voltalis hourly consumption as Home Assistant external statistics."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry_id: str,
        device_consumption_coordinator: BaseVoltalisCoordinator[dict[int, DeviceConsumption]],
        device_coordinator: BaseVoltalisCoordinator[dict[int, DeviceDto]],
        energy_contract_coordinator: DataUpdateCoordinator[dict[int, EnergyContract]],
        daily_consumption_handler: GetDevicesDailyConsumptionHandler,
    ) -> None:
        self.__hass = hass
        self.__entry_id = entry_id.lower()
        self.__device_consumption_coordinator = device_consumption_coordinator
        self.__device_coordinator = device_coordinator
        self.__energy_contract_coordinator = energy_contract_coordinator
        self.__daily_consumption_handler = daily_consumption_handler
        self.__lock = asyncio.Lock()
        self.__remove_listener: Callable[[], None] | None = None
        self.__statistic_listeners: list[Callable[[str, float], None]] = []
        self.__latest_daily_values: dict[str, float] = {}

    def add_statistic_listener(self, listener: Callable[[str, float], None]) -> Callable[[], None]:
        """Subscribe to updated external statistic values."""
        self.__statistic_listeners.append(listener)

        def remove_listener() -> None:
            if listener in self.__statistic_listeners:
                self.__statistic_listeners.remove(listener)

        return remove_listener

    def get_latest_value(self, statistic_id: str) -> float | None:
        """Return the latest cumulative value known for a statistic."""
        return self.__latest_daily_values.get(statistic_id)

    def start_time_tracking(self) -> None:
        """Start publishing statistics after each consumption update."""
        if self.__remove_listener is None:
            self.__remove_listener = self.__device_consumption_coordinator.async_add_listener(self.__schedule_update)

    def stop_time_tracking(self) -> None:
        """Stop publishing statistics."""
        if self.__remove_listener is not None:
            self.__remove_listener()
            self.__remove_listener = None

    @callback
    def __schedule_update(self) -> None:
        self.__hass.async_create_task(self.async_publish())

    async def async_publish(self) -> None:
        """Publish all newly available hourly consumption records."""
        async with self.__lock:
            await self.__publish_devices_data(self.__device_consumption_coordinator.data)

    async def async_backfill(self, target_dates: list[date]) -> None:
        """Load complete consumption records for dates requested during setup."""
        async with self.__lock:
            for target_date in target_dates:
                devices_data = await self.__daily_consumption_handler.handle(
                    target_date=target_date,
                    target_time=None,
                )
                await self.__publish_devices_data(devices_data)

    async def __publish_devices_data(self, devices_data: dict[int, DeviceConsumption]) -> None:
        published_series = 0
        for contract in self.__energy_contract_coordinator.data.values():
            sensor_types: tuple[str | None, ...] = (None,)
            if contract.type == EnergyContractTypeEnum.PEAK_OFFPEAK:
                sensor_types = (None, "peak", "offpeak")

            for sensor_type in sensor_types:
                contract_records = self.__get_records(
                    devices_data,
                    sensor_type,
                )
                await self.__publish_records(contract, sensor_type, contract_records)
                published_series += 1

                for device_id, device_data in devices_data.items():
                    device_records = self.__get_records({device_id: device_data}, sensor_type)
                    await self.__publish_records(
                        contract,
                        sensor_type,
                        device_records,
                        device_id=device_id,
                    )
                    published_series += 1

        self.__device_consumption_coordinator.logger.info(
            "Voltalis external energy statistics update completed: %s series considered",
            published_series,
        )

    def __get_records(
        self,
        devices_data: dict[int, DeviceConsumption],
        sensor_type: str | None,
    ) -> list[tuple[datetime, float]]:
        totals: defaultdict[datetime, float] = defaultdict(float)

        for device_data in devices_data.values():
            for record in device_data.daily_consumption_records:
                start = record.timestamp.replace(minute=0, second=0, microsecond=0)
                if sensor_type == "peak":
                    totals[start] += record.peak_consumption_in_wh or 0.0
                elif sensor_type == "offpeak":
                    totals[start] += record.offpeak_consumption_in_wh or 0.0
                else:
                    totals[start] += record.total_consumption_in_wh

        return sorted(totals.items())

    async def __publish_records(
        self,
        contract: EnergyContract,
        sensor_type: str | None,
        records: list[tuple[datetime, float]],
        device_id: int | None = None,
    ) -> None:
        statistic_id = self.__get_statistic_id(contract, sensor_type, device_id)
        metadata = self.__get_metadata(contract, sensor_type, statistic_id, device_id)
        last_statistics = await get_instance(self.__hass).async_add_executor_job(
            get_last_statistics, self.__hass, 1, statistic_id, False, {"sum"}
        )
        last_record = last_statistics.get(statistic_id, [])
        last_start = last_record[0].get("start") if last_record else None
        cumulative_sum = float(last_record[0].get("sum") or 0.0) if last_record else 0.0
        statistics: list[StatisticData] = []

        for start, consumption in records:
            start = self.__as_local(start)
            if last_start is not None and start.timestamp() <= last_start:
                continue
            cumulative_sum += consumption
            statistics.append(StatisticData(start=start, state=consumption, sum=cumulative_sum))

        if statistics:
            async_add_external_statistics(self.__hass, metadata, statistics)
            self.__device_consumption_coordinator.logger.info(
                "Published %s Voltalis statistics for %s",
                len(statistics),
                statistic_id,
            )

        await self.__update_daily_value(statistic_id, statistics)

    async def __update_daily_value(self, statistic_id: str, new_statistics: list[StatisticData]) -> None:
        """Expose today's consumption while keeping Recorder's sum cumulative."""
        start_of_day = dt_util.start_of_local_day()
        rows = await get_instance(self.__hass).async_add_executor_job(
            statistics_during_period,
            self.__hass,
            start_of_day - timedelta(hours=1),
            None,
            {statistic_id},
            "hour",
            None,
            {"sum"},
        )
        daily_rows = rows.get(statistic_id, [])
        baseline = 0.0
        latest_sum = 0.0
        latest_start = 0.0
        start_timestamp = start_of_day.timestamp()
        for row in daily_rows:
            row_start = float(row.get("start") or 0.0)
            row_sum = float(row.get("sum") or 0.0)
            if row_start < start_timestamp:
                baseline = row_sum
            else:
                latest_sum = row_sum
            latest_start = max(latest_start, row_start)

        daily_value = max(0.0, latest_sum - baseline)
        for statistic in new_statistics:
            statistic_start = self.__as_local(statistic["start"])
            if statistic_start.timestamp() >= start_timestamp and statistic_start.timestamp() > latest_start:
                daily_value += float(statistic.get("state") or 0.0)

        self.__latest_daily_values[statistic_id] = daily_value
        for listener in tuple(self.__statistic_listeners):
            listener(statistic_id, daily_value)

    @staticmethod
    def __as_local(value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=dt_util.get_default_time_zone())
        return dt_util.as_local(value)

    def __get_statistic_id(self, contract: EnergyContract, sensor_type: str | None, device_id: int | None) -> str:
        if device_id is not None:
            suffix = f"_{sensor_type}" if sensor_type else ""
            return f"{DOMAIN}:device_{self.__entry_id}_{device_id}_energy{suffix}"
        suffix = f"_{sensor_type}" if sensor_type else ""
        return f"{DOMAIN}:contract_{self.__entry_id}_{contract.id}_energy{suffix}"

    def __get_metadata(
        self,
        contract: EnergyContract,
        sensor_type: str | None,
        statistic_id: str,
        device_id: int | None,
    ) -> StatisticMetaData:
        if device_id is None:
            name = contract.name
        else:
            device = self.__device_coordinator.data.get(device_id)
            name = device.name if device else f"Device {device_id}"
        suffix = f" {sensor_type}" if sensor_type else ""
        return StatisticMetaData(
            mean_type=StatisticMeanType.NONE,
            has_sum=True,
            name=f"{name}{suffix} consumption",
            source=DOMAIN,
            statistic_id=statistic_id,
            unit_class=EnergyConverter.UNIT_CLASS,
            unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        )
