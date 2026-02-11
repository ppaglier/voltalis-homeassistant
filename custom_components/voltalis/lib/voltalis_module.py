from logging import Logger

from custom_components.voltalis.lib.application.devices_management.handlers.get_devices_daily_consumption_handler import (  # noqa: E501
    GetDevicesDailyConsumptionHandler,
)
from custom_components.voltalis.lib.application.energy_contracts.handlers.get_live_consumption_handler import (
    GetLiveConsumptionHandler,
)
from custom_components.voltalis.lib.application.voltalis_programs_management.handlers.get_programs_handler import (
    GetProgramsHandler,
)
from custom_components.voltalis.lib.application.voltalis_programs_management.handlers.set_current_program_handler import (  # noqa: E501
    SetCurrentProgramHandler,
)
from custom_components.voltalis.lib.domain.shared.providers.date_provider import DateProvider
from custom_components.voltalis.lib.domain.shared.providers.voltalis_provider import VoltalisProvider


class VoltalisModule:
    """Module to initialize the voltalis lib."""

    def __init__(
        self,
        *,
        # Providers
        date_provider: DateProvider,
        logger: Logger,
        voltalis_provider: VoltalisProvider,
    ) -> None:
        """Initialize the the voltalis module."""

        # Providers
        self.date_provider = date_provider
        self.logger = logger
        self.voltalis_provider = voltalis_provider

    def setup_handlers(self) -> None:
        """Setup the handlers."""

        # Devices management
        self.get_devices_daily_consumption_handler = GetDevicesDailyConsumptionHandler(
            date_provider=self.date_provider,
            voltalis_provider=self.voltalis_provider,
        )

        # energy contracts
        self.get_live_consumption_handler = GetLiveConsumptionHandler(
            voltalis_provider=self.voltalis_provider,
        )

        # programs management
        self.get_programs_handler = GetProgramsHandler(
            voltalis_provider=self.voltalis_provider,
        )
        self.set_current_program_handler = SetCurrentProgramHandler(
            voltalis_provider=self.voltalis_provider,
        )
