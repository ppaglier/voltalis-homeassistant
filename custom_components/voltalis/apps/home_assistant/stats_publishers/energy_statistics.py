from __future__ import annotations

import asyncio
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from logging import Logger
from typing import Callable

from homeassistant.components.recorder.models import StatisticData, StatisticMeanType, StatisticMetaData
from homeassistant.components.recorder.statistics import (
    async_add_external_statistics,
    get_last_statistics,
    statistics_during_period,
)
from homeassistant.const import UnitOfEnergy
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import device_registry
from homeassistant.helpers.recorder import get_instance
from homeassistant.helpers.translation import async_get_translations
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util
from homeassistant.util.unit_conversion import EnergyConverter

from custom_components.voltalis.apps.home_assistant.coordinators.base import BaseVoltalisCoordinator
from custom_components.voltalis.const import DOMAIN
from custom_components.voltalis.lib.application.devices_management.handlers.devices.get_devices_daily_energy_handler import (  # noqa: E501
    GetDevicesDailyEnergyHandler,
)
from custom_components.voltalis.lib.domain.devices_management.energy.device_energy import DeviceEnergy, EnergyRecord
from custom_components.voltalis.lib.domain.energy_contracts.energy_contract import EnergyContract
from custom_components.voltalis.lib.domain.energy_contracts.energy_contract_enum import EnergyContractTypeEnum


class VoltalisEnergyStatisticsPublisher:
    """Publish Voltalis hourly consumption as Home Assistant external statistics."""

    def __init__(
        self,
        *,
        hass: HomeAssistant,
        entry_id: str,
        site_id: str,
        logger: Logger,
        device_consumption_coordinator: BaseVoltalisCoordinator[dict[int, DeviceEnergy]],
        energy_contract_coordinator: DataUpdateCoordinator[dict[int, EnergyContract]],
        daily_consumption_handler: GetDevicesDailyEnergyHandler,
    ) -> None:
        self.__hass = hass
        self.__entry_id = entry_id
        self.__site_id = site_id
        self.__device_registry = device_registry.async_get(hass)
        self.__translations: dict[str, str] | None = None
        self.__translation_language: str | None = None
        self.__logger = logger
        self.__device_consumption_coordinator = device_consumption_coordinator
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
            devices_data: dict[int, list[EnergyRecord]] = defaultdict(list)
            for target_date in target_dates:
                daily_devices_data = await self.__daily_consumption_handler.handle(
                    target_date=target_date,
                    target_time=None,
                )
                for device_id, device_data in daily_devices_data.items():
                    devices_data[device_id].extend(device_data.daily_energy_records)

            await self.__publish_devices_data(
                {device_id: DeviceEnergy(daily_energy_records=records) for device_id, records in devices_data.items()},
                replace_existing=True,
            )

    async def __publish_devices_data(
        self,
        devices_data: dict[int, DeviceEnergy],
        *,
        replace_existing: bool = False,
    ) -> None:
        published_series = 0
        for energy_contract in self.__energy_contract_coordinator.data.values():
            sensor_types: tuple[str | None, ...] = (None,)
            if energy_contract.type == EnergyContractTypeEnum.PEAK_OFF_PEAK:
                sensor_types = (None, "peak", "off-peak")

            for sensor_type in sensor_types:
                contract_entity_id = self.__get_statistic_id(
                    stat_suffix=f"system_energy_daily{f'_{sensor_type}' if sensor_type else ''}",
                )
                contract_statistic_name = await self.__get_statistic_name(
                    stat_suffix=f"system_energy_daily{f'_{sensor_type}' if sensor_type else ''}",
                )
                records = self.__get_records(
                    devices_data,
                    sensor_type,
                )
                await self.__publish_records(
                    statistic_id=contract_entity_id,
                    statistic_name=contract_statistic_name,
                    records=records,
                    replace_existing=replace_existing,
                )
                published_series += 1

                cost_statistic_id = self.__get_statistic_id(
                    stat_suffix=f"system_energy_cost{f'_{sensor_type}' if sensor_type else ''}",
                )
                cost_statistic_name = await self.__get_statistic_name(
                    stat_suffix=f"system_energy_cost{f'_{sensor_type}' if sensor_type else ''}",
                )
                await self.__publish_records(
                    statistic_id=cost_statistic_id,
                    statistic_name=cost_statistic_name,
                    records=self.__get_cost_records(devices_data, sensor_type, energy_contract),
                    replace_existing=replace_existing,
                    unit_of_measurement="EUR",
                    unit_class=None,
                    update_daily_value=False,
                )
                published_series += 1

                for device_id, device_data in devices_data.items():
                    device_records = self.__get_records({device_id: device_data}, sensor_type)
                    device_entity_id = self.__get_statistic_id(
                        stat_suffix=f"device_energy_daily{f'_{sensor_type}' if sensor_type else ''}",
                        device_id=device_id,
                    )
                    device_statistic_name = await self.__get_statistic_name(
                        stat_suffix=f"device_energy_daily{f'_{sensor_type}' if sensor_type else ''}",
                        device_id=device_id,
                    )
                    await self.__publish_records(
                        statistic_id=device_entity_id,
                        statistic_name=device_statistic_name,
                        records=device_records,
                        replace_existing=replace_existing,
                    )
                    published_series += 1

        self.__logger.info(
            "Voltalis external energy statistics update completed: %s series considered",
            published_series,
        )

    def __get_records(
        self,
        devices_data: dict[int, DeviceEnergy],
        sensor_type: str | None,
    ) -> list[tuple[datetime, float]]:
        totals: defaultdict[datetime, float] = defaultdict(float)

        for device_data in devices_data.values():
            for record in device_data.daily_energy_records:
                start = record.timestamp.replace(minute=0, second=0, microsecond=0)
                if sensor_type == "peak":
                    totals[start] += record.peak or 0.0
                elif sensor_type == "off-peak":
                    totals[start] += record.off_peak or 0.0
                else:
                    totals[start] += record.total

        return sorted(totals.items())

    def __get_cost_records(
        self,
        devices_data: dict[int, DeviceEnergy],
        sensor_type: str | None,
        energy_contract: EnergyContract,
    ) -> list[tuple[datetime, float]]:
        """Calculate hourly system cost in EUR for the selected tariff."""
        totals: defaultdict[datetime, float] = defaultdict(float)
        prices = energy_contract.prices

        for device_data in devices_data.values():
            for record in device_data.daily_energy_records:
                start = record.timestamp.replace(minute=0, second=0, microsecond=0)
                if sensor_type == "peak":
                    consumption = record.peak or 0.0
                    price = prices.kwh_peak or 0.0
                elif sensor_type == "off-peak":
                    consumption = record.off_peak or 0.0
                    price = prices.kwh_off_peak or 0.0
                elif energy_contract.type == EnergyContractTypeEnum.PEAK_OFF_PEAK:
                    consumption = (record.peak or 0.0) * (prices.kwh_peak or 0.0)
                    consumption += (record.off_peak or 0.0) * (prices.kwh_off_peak or 0.0)
                    totals[start] += consumption / 1000
                    continue
                else:
                    consumption = record.total
                    price = prices.kwh_base or 0.0

                totals[start] += consumption * price / 1000

        return sorted(totals.items())

    async def __publish_records(
        self,
        *,
        statistic_id: str,
        statistic_name: str,
        records: list[tuple[datetime, float]],
        replace_existing: bool = False,
        unit_of_measurement: str = UnitOfEnergy.WATT_HOUR,
        unit_class: str | None = EnergyConverter.UNIT_CLASS,
        update_daily_value: bool = True,
    ) -> None:
        if replace_existing:
            statistics = await self.__build_replacement_statistics(statistic_id=statistic_id, records=records)
        else:
            last_statistics = await get_instance(self.__hass).async_add_executor_job(
                get_last_statistics, self.__hass, 1, statistic_id, False, {"sum"}
            )
            last_record = last_statistics.get(statistic_id, [])
            last_start = last_record[0].get("start") if last_record else None
            cumulative_sum = float(last_record[0].get("sum") or 0.0) if last_record else 0.0

            statistics = []
            for start, consumption in records:
                start = self.__as_local(start)
                if last_start is not None and start.timestamp() <= last_start:
                    continue
                cumulative_sum += consumption
                statistics.append(StatisticData(start=start, state=consumption, sum=cumulative_sum))

        if statistics:
            async_add_external_statistics(
                self.__hass,
                StatisticMetaData(
                    mean_type=StatisticMeanType.NONE,
                    has_sum=True,
                    name=statistic_name,
                    source=DOMAIN,
                    statistic_id=statistic_id,
                    unit_class=unit_class,
                    unit_of_measurement=unit_of_measurement,
                ),
                statistics,
            )
            self.__logger.info(
                "Published %s Voltalis statistics for %s",
                len(statistics),
                statistic_id,
            )

        if update_daily_value:
            await self.__update_daily_value(statistic_id, statistics)

    async def __build_replacement_statistics(
        self,
        *,
        statistic_id: str,
        records: list[tuple[datetime, float]],
    ) -> list[StatisticData]:
        """Merge API records with Recorder rows before recalculating cumulative sums."""
        if not records:
            return []

        api_values = {self.__as_local(start).timestamp(): consumption for start, consumption in records}
        start = datetime.fromtimestamp(min(api_values), tz=timezone.utc) - timedelta(hours=1)
        end = datetime.fromtimestamp(max(api_values), tz=timezone.utc) + timedelta(hours=1)
        rows = await get_instance(self.__hass).async_add_executor_job(
            statistics_during_period,
            self.__hass,
            start,
            end,
            {statistic_id},
            "hour",
            None,
            {"state", "sum"},
        )

        values: dict[float, float] = {}
        baseline = 0.0
        first_api_timestamp = min(api_values)
        for row in rows.get(statistic_id, []):
            row_start = float(row.get("start") or 0.0)
            row_state = row.get("state")
            row_sum = row.get("sum")
            if row_state is not None:
                values[row_start] = float(row_state)
            if row_start < first_api_timestamp and row_sum is not None:
                baseline = float(row_sum) - float(row_state or 0.0)

        values.update(api_values)
        cumulative_sum = baseline
        statistics: list[StatisticData] = []
        for timestamp in sorted(values):
            consumption = values[timestamp]
            cumulative_sum += consumption
            statistics.append(
                StatisticData(
                    start=datetime.fromtimestamp(timestamp, tz=timezone.utc),
                    state=consumption,
                    sum=cumulative_sum,
                )
            )
        return statistics

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

    def __get_statistic_id(self, *, stat_suffix: str, device_id: int | None = None) -> str:
        """Build a readable and stable Recorder statistic ID."""
        normalized_suffix = stat_suffix.replace("-", "_")
        if device_id is None:
            return f"{DOMAIN}:{self.__site_id}_{normalized_suffix}"

        return f"{DOMAIN}:{self.__site_id}_{device_id}_{normalized_suffix}"

    async def __get_statistic_name(self, *, stat_suffix: str, device_id: int | None = None) -> str:
        """Build the display name stored with an external statistic."""

        # Get translation for the current language
        translations = await async_get_translations(
            self.__hass,
            self.__hass.config.language,
            "entity",
            integrations=[DOMAIN],
        )

        # Get Statistic name
        translation_key = f"component.{DOMAIN}.entity.sensor.{stat_suffix}.name"
        label = translations.get(translation_key)
        if label is None:
            label = stat_suffix.removeprefix("system_").removeprefix("device_").replace("_", " ")

        # Get Device name
        device = self.__device_registry.async_get_device_by_identifier(
            identifier=(DOMAIN, f"{self.__site_id}_{device_id or 'system'}"),
            config_entry_id=self.__entry_id,
        )
        device_name = "Voltalis"
        if device is not None:
            device_name = device.name_by_user or device.name or device_name

        return f"{device_name} {label}".capitalize()
