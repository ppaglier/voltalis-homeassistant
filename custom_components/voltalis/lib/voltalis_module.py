from logging import Logger

from custom_components.voltalis.lib.application.devices_management.handlers.climates.disable_manual_mode_handler import (  # noqa: E501
    DisableManualModeHandler,
)
from custom_components.voltalis.lib.application.devices_management.handlers.climates.get_climate_current_action_handler import (  # noqa: E501
    GetClimateCurrentActionHandler,
)
from custom_components.voltalis.lib.application.devices_management.handlers.climates.set_climate_action_handler import (
    SetClimateActionHandler,
)
from custom_components.voltalis.lib.application.devices_management.handlers.climates.set_device_temperature_handler import (  # noqa: E501
    SetDeviceTemperatureHandler,
)
from custom_components.voltalis.lib.application.devices_management.handlers.climates.turn_off_device_handler import (
    TurnOffDeviceHandler,
)
from custom_components.voltalis.lib.application.devices_management.handlers.devices.get_device_current_mode_handler import (  # noqa: E501
    GetDeviceCurrentModeHandler,
)
from custom_components.voltalis.lib.application.devices_management.handlers.devices.get_devices import GetDevicesHandler
from custom_components.voltalis.lib.application.devices_management.handlers.devices.get_devices_daily_consumption_handler import (  # noqa: E501
    GetDevicesDailyConsumptionHandler,
)  # noqa: E501
from custom_components.voltalis.lib.application.devices_management.handlers.devices.get_devices_health_handler import (
    GetDevicesHealthHandler,
)  # noqa: E501
from custom_components.voltalis.lib.application.devices_management.handlers.presets.get_device_current_preset_handler import (  # noqa: E501
    GetDeviceCurrentPresetHandler,
)
from custom_components.voltalis.lib.application.devices_management.handlers.presets.set_device_preset_handler import (
    SetDevicePresetHandler,
)
from custom_components.voltalis.lib.application.devices_management.handlers.water_heaters.get_water_heater_current_operation_handler import (  # noqa: E501
    GetWaterHeaterCurrentOperationHandler,
)
from custom_components.voltalis.lib.application.devices_management.handlers.water_heaters.set_water_heater_operation_handler import (  # noqa: E501
    SetWaterHeaterOperationHandler,
)
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
        self.get_devices_handler = GetDevicesHandler(
            logger=self.logger,
            voltalis_provider=self.voltalis_provider,
        )
        self.get_devices_health_handler = GetDevicesHealthHandler(
            voltalis_provider=self.voltalis_provider,
        )
        self.get_devices_daily_consumption_handler = GetDevicesDailyConsumptionHandler(
            date_provider=self.date_provider,
            voltalis_provider=self.voltalis_provider,
        )

        # Device presets

        self.get_device_current_preset_handler = GetDeviceCurrentPresetHandler()
        self.set_device_preset_handler = SetDevicePresetHandler(
            logger=self.logger,
            date_provider=self.date_provider,
            voltalis_provider=self.voltalis_provider,
        )

        # Device water heater operations

        self.get_water_heater_current_operation_handler = GetWaterHeaterCurrentOperationHandler()
        self.set_water_heater_operation_handler = SetWaterHeaterOperationHandler(
            logger=self.logger,
            date_provider=self.date_provider,
            voltalis_provider=self.voltalis_provider,
        )

        # Device climate management

        self.get_device_current_mode_handler = GetDeviceCurrentModeHandler()

        self.get_climate_current_action_handler = GetClimateCurrentActionHandler()
        self.set_climate_action_handler = SetClimateActionHandler(
            logger=self.logger,
            date_provider=self.date_provider,
            voltalis_provider=self.voltalis_provider,
        )

        self.turn_off_device_handler = TurnOffDeviceHandler(
            logger=self.logger,
            date_provider=self.date_provider,
            voltalis_provider=self.voltalis_provider,
        )

        self.set_device_temperature_handler = SetDeviceTemperatureHandler(
            logger=self.logger,
            date_provider=self.date_provider,
            voltalis_provider=self.voltalis_provider,
        )
        self.disable_manual_mode_handler = DisableManualModeHandler(
            logger=self.logger,
            date_provider=self.date_provider,
            voltalis_provider=self.voltalis_provider,
        )

        # energy contracts
        self.get_current_energy_contract_handler = GetCurrentEnergyContractHandler(
            date_provider=self.date_provider,
            voltalis_provider=self.voltalis_provider,
        )
        self.get_energy_contract_current_mode_handler = GetEnergyContractCurrentModeHandler(
            date_provider=self.date_provider,
        )
        self.get_energy_contract_current_kwh_cost_handler = GetEnergyContractCurrentKwhCostHandler(
            logger=self.logger,
        )
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
