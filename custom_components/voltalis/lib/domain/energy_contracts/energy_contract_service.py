from datetime import time

from custom_components.voltalis.lib.domain.energy_contracts.energy_contract_current_mode_enum import (
    EnergyContractCurrentModeEnum,
)
from custom_components.voltalis.lib.domain.energy_contracts.energy_contract_enum import EnergyContractTypeEnum
from custom_components.voltalis.lib.domain.shared.providers.date_provider import DateProvider
from custom_components.voltalis.lib.domain.shared.range_model import RangeModel


class EnergyContractService:
    """Service for energy contracts management."""

    def __init__(
        self,
        *,
        date_provider: DateProvider,
    ):
        self.__date_provider = date_provider

    def get_current_mode(
        self,
        *,
        type: EnergyContractTypeEnum,
        offpeak_hours: list[RangeModel[time]],
    ) -> EnergyContractCurrentModeEnum:
        """Get the current mode of the energy contract."""

        if type == EnergyContractTypeEnum.BASE:
            return EnergyContractCurrentModeEnum.BASE

        now = self.__date_provider.get_now().time()
        in_off_peak = any(self.__is_in_time_range(time_range, now) for time_range in offpeak_hours)

        if in_off_peak:
            return EnergyContractCurrentModeEnum.OFFPEAK

        return EnergyContractCurrentModeEnum.PEAK

    def __is_in_time_range(self, time_range: RangeModel[time], now: time) -> bool:
        """Return True if now is within the given time range, handling overnight spans."""
        start = time_range.start
        end = time_range.end
        if start <= end:
            # Normal range within the same day, e.g. 08:00-12:00
            return start <= now <= end
        # Overnight range crossing midnight, e.g. 22:00-06:00
        return now >= start or now <= end
