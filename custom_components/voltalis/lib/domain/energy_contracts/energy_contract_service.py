from datetime import time

from custom_components.voltalis.lib.domain.energy_contracts.energy_contract_current_mode_enum import (
    EnergyContractCurrentModeEnum,
)
from custom_components.voltalis.lib.domain.energy_contracts.energy_contract_enum import EnergyContractTypeEnum
from custom_components.voltalis.lib.domain.helpers.is_in_time_range import is_in_time_range
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
        contract_type: EnergyContractTypeEnum,
        offpeak_hours: list[RangeModel[time]],
    ) -> EnergyContractCurrentModeEnum:
        """Get the current mode of the energy contract."""

        if contract_type == EnergyContractTypeEnum.BASE:
            return EnergyContractCurrentModeEnum.BASE

        now = self.__date_provider.get_now().time()
        in_off_peak = any(is_in_time_range(time_range, now) for time_range in offpeak_hours)

        if in_off_peak:
            return EnergyContractCurrentModeEnum.OFFPEAK

        return EnergyContractCurrentModeEnum.PEAK
