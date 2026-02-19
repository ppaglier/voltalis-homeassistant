import logging
from datetime import datetime

from custom_components.voltalis.lib.application.energy_contracts.handlers.get_current_energy_contract_handler import (
    GetCurrentEnergyContractHandler,
)
from custom_components.voltalis.lib.application.energy_contracts.handlers.get_energy_contract_current_kwh_cost_handler import (  # noqa: E501
    GetEnergyContractCurrentKwhCostHandler,
)
from custom_components.voltalis.lib.application.energy_contracts.handlers.get_energy_contract_current_mode_handler import (  # noqa: E501
    GetEnergyContractCurrentModeHandler,
)
from custom_components.voltalis.lib.application.energy_contracts.handlers.get_live_consumption_handler import (
    GetLiveConsumptionHandler,
)
from custom_components.voltalis.lib.domain.energy_contracts.energy_contract import EnergyContract
from custom_components.voltalis.lib.domain.energy_contracts.live_consumption import LiveConsumption
from custom_components.voltalis.lib.infrastructure.providers.date_provider_stub import DateProviderStub
from custom_components.voltalis.lib.infrastructure.providers.voltalis_provider_stub import VoltalisProviderStub
from custom_components.voltalis.tests.base_fixture import BaseFixture


class EnergyContractsFixture(BaseFixture):
    """Fixture for energy contracts tests."""

    def __init__(self) -> None:
        self.logger = logging.getLogger("voltalis-home_assistant-tests energy-contracts-fixture")

        self.date_provider = DateProviderStub()
        self.voltalis_provider = VoltalisProviderStub()

        self.get_current_energy_contract_handler = GetCurrentEnergyContractHandler(
            date_provider=self.date_provider,
            voltalis_provider=self.voltalis_provider,
        )
        self.get_energy_contract_current_mode_handler = GetEnergyContractCurrentModeHandler(
            date_provider=self.date_provider,
        )
        self.get_energy_contract_current_kwh_cost_handler = GetEnergyContractCurrentKwhCostHandler()
        self.get_live_consumption_handler = GetLiveConsumptionHandler(
            voltalis_provider=self.voltalis_provider,
        )

    # ------------------------------------------------------------
    # Given
    # ------------------------------------------------------------

    def given_now(self, now: datetime) -> None:
        """Set the current date and time."""

        self.date_provider.now = now

    def given_energy_contracts(self, energy_contracts: dict[int, EnergyContract]) -> None:
        """Set energy contracts returned by the provider."""

        self.voltalis_provider.set_energy_contracts(energy_contracts)

    def given_live_consumption(self, live_consumption: LiveConsumption) -> None:
        """Set live consumption returned by the provider."""

        self.voltalis_provider.set_live_consumption(live_consumption)

    # ------------------------------------------------------------
    # Assertions
    # ------------------------------------------------------------

    def then_energy_contracts_should_be(self, expected_contracts: dict[int, EnergyContract]) -> None:
        """Assert energy contracts returned by the provider are as expected."""

        self.compare_dicts(self.voltalis_provider._energy_contracts, expected_contracts)

    def then_live_consumption_should_be(self, expected: LiveConsumption) -> None:
        """Assert live consumption returned by the provider is as expected."""

        self.compare_data(self.voltalis_provider._live_consumption, expected)
