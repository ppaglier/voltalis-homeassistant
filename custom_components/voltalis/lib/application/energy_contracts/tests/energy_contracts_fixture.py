import logging
from datetime import datetime

from custom_components.voltalis.lib.application.energy_contracts.handlers.get_current_energy_contract_handler import (
    GetCurrentEnergyContractHandler,
)
from custom_components.voltalis.lib.application.energy_contracts.handlers.get_energy_contract_current_tariff_handler import (  # noqa: E501
    GetEnergyContractCurrentTariffHandler,
)
from custom_components.voltalis.lib.application.energy_contracts.handlers.get_energy_contract_kwh_current_price_handler import (  # noqa: E501
    GetEnergyContractKwhCurrentPriceHandler,
)
from custom_components.voltalis.lib.application.energy_contracts.handlers.get_live_power_handler import (
    GetLivePowerHandler,
)
from custom_components.voltalis.lib.domain.energy_contracts.energy_contract import EnergyContract
from custom_components.voltalis.lib.domain.energy_contracts.live_power import LivePower
from custom_components.voltalis.lib.infrastructure.providers.date_provider_stub import DateProviderStub
from custom_components.voltalis.lib.infrastructure.providers.voltalis_provider_stub import VoltalisProviderStub
from custom_components.voltalis.tests.utils.base_fixture import BaseFixture


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
        self.get_energy_contract_current_tariff_handler = GetEnergyContractCurrentTariffHandler(
            date_provider=self.date_provider,
        )
        self.get_energy_contract_kwh_current_price_handler = GetEnergyContractKwhCurrentPriceHandler()
        self.get_live_power_handler = GetLivePowerHandler(
            voltalis_provider=self.voltalis_provider,
        )

    # ------------------------------------------------------------
    # Given
    # ------------------------------------------------------------

    def given_now(self, now: datetime) -> None:
        """Set the current date and time."""

        self.date_provider.now = now

    def given_energy_contracts(self, energy_contracts: list[EnergyContract]) -> None:
        """Set energy contracts returned by the provider."""

        self.voltalis_provider.set_energy_contracts(energy_contracts)

    def given_live_power(self, live_power: LivePower) -> None:
        """Set live consumption returned by the provider."""

        self.voltalis_provider.set_live_power(live_power)

    # ------------------------------------------------------------
    # Assertions
    # ------------------------------------------------------------

    def then_energy_contracts_should_be(self, expected_contracts: dict[int, EnergyContract]) -> None:
        """Assert energy contracts returned by the provider are as expected."""

        self.compare_dicts(self.voltalis_provider._energy_contracts, expected_contracts)

    def then_live_power_should_be(self, expected: LivePower) -> None:
        """Assert live consumption returned by the provider is as expected."""

        self.compare_data(self.voltalis_provider._live_power, expected)
