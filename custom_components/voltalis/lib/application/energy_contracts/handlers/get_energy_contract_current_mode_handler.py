from custom_components.voltalis.apps.home_assistant.entities.energy_contract.current_mode_sensor import (
    EnergyContractCurrentModeEnum,
)
from custom_components.voltalis.lib.application.energy_contracts.queries.get_energy_contract_current_mode_query import (
    GetEnergyContractCurrentModeQuery,
)
from custom_components.voltalis.lib.domain.energy_contracts.energy_contract_enum import EnergyContractTypeEnum
from custom_components.voltalis.lib.domain.energy_contracts.helpers.is_in_time_range import is_in_time_range
from custom_components.voltalis.lib.domain.shared.providers.date_provider import DateProvider


class GetEnergyContractCurrentModeHandler:
    """Handler to get the current mode of the energy contract."""

    def __init__(
        self,
        *,
        date_provider: DateProvider,
    ):
        self.__date_provider = date_provider

    async def handle(self, query: GetEnergyContractCurrentModeQuery) -> EnergyContractCurrentModeEnum:
        """Handle the request to get the current mode of the energy contract."""

        if query.type == EnergyContractTypeEnum.BASE:
            return EnergyContractCurrentModeEnum.BASE

        now = self.__date_provider.get_now().time()
        in_off_peak = any(is_in_time_range(time_range, now) for time_range in query.offpeak_hours)

        if in_off_peak:
            return EnergyContractCurrentModeEnum.OFFPEAK

        return EnergyContractCurrentModeEnum.PEAK
