import logging
from datetime import datetime

from custom_components.voltalis.const import (
    DEFAULT_AWAY_TEMP,
    DEFAULT_COMFORT_TEMP,
    DEFAULT_ECO_TEMP,
    DEFAULT_TEMP,
    DEFAULT_WATER_HEATER_TEMP,
)
from custom_components.voltalis.lib.application.devices_management.handlers.climates.disable_manual_mode_handler import (  # noqa: E501
    DisableManualModeHandler,
)
from custom_components.voltalis.lib.application.devices_management.handlers.climates.get_climate_action_handler import (
    GetClimateActionHandler,
)
from custom_components.voltalis.lib.application.devices_management.handlers.climates.get_climate_mode_handler import (
    GetClimateModeHandler,
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
from custom_components.voltalis.lib.application.devices_management.handlers.devices.get_device_mode_handler import (
    GetDeviceModeHandler,
)
from custom_components.voltalis.lib.application.devices_management.handlers.devices.get_devices import GetDevicesHandler
from custom_components.voltalis.lib.application.devices_management.handlers.devices.get_devices_daily_consumption_handler import (  # noqa: E501
    GetDevicesDailyConsumptionHandler,
)
from custom_components.voltalis.lib.application.devices_management.handlers.devices.get_devices_health_handler import (
    GetDevicesHealthHandler,
)
from custom_components.voltalis.lib.application.devices_management.handlers.presets.get_device_preset_handler import (
    GetDevicePresetHandler,
)
from custom_components.voltalis.lib.application.devices_management.handlers.presets.get_device_presets_handler import (
    GetDevicePresetsHandler,
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
from custom_components.voltalis.lib.domain.devices_management.climates.manual_setting import ManualSetting
from custom_components.voltalis.lib.domain.devices_management.devices.device import Device
from custom_components.voltalis.lib.domain.devices_management.health.device_health import DeviceHealth
from custom_components.voltalis.lib.infrastructure.providers.date_provider_stub import DateProviderStub
from custom_components.voltalis.lib.infrastructure.providers.voltalis_provider_stub import VoltalisProviderStub
from custom_components.voltalis.tests.base_fixture import BaseFixture


class DeviceManagementFixture(BaseFixture):
    """Fixture for device management tests."""

    def __init__(self) -> None:
        self.logger = logging.getLogger("voltalis-home_assistant-tests device-management-fixture")

        # Providers
        self.date_provider = DateProviderStub()
        self.voltalis_provider = VoltalisProviderStub()

        # Config
        self.default_temperature = DEFAULT_TEMP
        self.default_away_temp = DEFAULT_AWAY_TEMP
        self.default_eco_temp = DEFAULT_ECO_TEMP
        self.default_comfort_temp = DEFAULT_COMFORT_TEMP
        self.default_water_heater_temp = DEFAULT_WATER_HEATER_TEMP

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
        self.get_device_mode_handler = GetDeviceModeHandler()

        # Device presets

        self.get_device_presets_handler = GetDevicePresetsHandler()
        self.get_device_preset_handler = GetDevicePresetHandler()
        self.set_device_preset_handler = SetDevicePresetHandler(
            logger=self.logger,
            date_provider=self.date_provider,
            voltalis_provider=self.voltalis_provider,
            default_temperature=self.default_temperature,
            default_away_temperature=self.default_away_temp,
            default_eco_temperature=self.default_eco_temp,
            default_comfort_temperature=self.default_comfort_temp,
        )

        # Device water heater operations

        self.get_water_heater_current_operation_handler = GetWaterHeaterCurrentOperationHandler()
        self.set_water_heater_operation_handler = SetWaterHeaterOperationHandler(
            logger=self.logger,
            date_provider=self.date_provider,
            voltalis_provider=self.voltalis_provider,
            default_water_heater_temp=self.default_water_heater_temp,
        )

        # Device climate management

        self.get_climate_mode_handler = GetClimateModeHandler()

        self.get_climate_action_handler = GetClimateActionHandler()
        self.set_climate_action_handler = SetClimateActionHandler(
            logger=self.logger,
            date_provider=self.date_provider,
            voltalis_provider=self.voltalis_provider,
            default_temperature=self.default_temperature,
            default_away_temperature=self.default_away_temp,
            default_eco_temperature=self.default_eco_temp,
            default_comfort_temperature=self.default_comfort_temp,
        )

        self.turn_off_device_handler = TurnOffDeviceHandler(
            logger=self.logger,
            date_provider=self.date_provider,
            voltalis_provider=self.voltalis_provider,
            default_temperature=self.default_temperature,
            default_away_temperature=self.default_away_temp,
            default_eco_temperature=self.default_eco_temp,
            default_comfort_temperature=self.default_comfort_temp,
        )

        self.set_device_temperature_handler = SetDeviceTemperatureHandler(
            logger=self.logger,
            date_provider=self.date_provider,
            voltalis_provider=self.voltalis_provider,
            default_temperature=self.default_temperature,
            default_away_temperature=self.default_away_temp,
            default_eco_temperature=self.default_eco_temp,
            default_comfort_temperature=self.default_comfort_temp,
        )
        self.disable_manual_mode_handler = DisableManualModeHandler(
            logger=self.logger,
            date_provider=self.date_provider,
            voltalis_provider=self.voltalis_provider,
            default_temperature=self.default_temperature,
            default_away_temp=self.default_away_temp,
            default_eco_temp=self.default_eco_temp,
            default_comfort_temp=self.default_comfort_temp,
        )

    # ------------------------------------------------------------
    # Given
    # ------------------------------------------------------------

    def given_now(self, now: datetime) -> None:
        """Set the current date and time."""

        self.date_provider.now = now

    def given_devices(self, devices: dict[int, Device]) -> None:
        """Set the devices to be returned by the provider."""

        self.voltalis_provider.set_devices(devices)

    def given_devices_health(self, devices_health: dict[int, DeviceHealth]) -> None:
        """Set the devices health to be returned by the provider."""

        self.voltalis_provider.set_devices_health(devices_health)

    def given_devices_consumptions(self, devices_consumptions: dict[int, list[tuple[datetime, float]]]) -> None:
        """Set the devices consumptions to be returned by the provider."""

        self.voltalis_provider.set_devices_consumptions(devices_consumptions)

    def given_manual_settings(self, manual_settings: list[ManualSetting]) -> None:
        """Set the devices manual settings to be returned by the provider."""

        self.voltalis_provider.set_manual_settings(manual_settings)

    # ------------------------------------------------------------
    # Assertions
    # ------------------------------------------------------------

    def then_devices_should_be(self, expected_devices: dict[int, Device]) -> None:
        """Assert the devices returned by the provider are as expected."""

        self.compare_dicts(self.voltalis_provider._devices, expected_devices)

    def then_manual_settings_should_be(self, expected_manual_settings: dict[int, ManualSetting]) -> None:
        """Assert the manual settings returned by the provider are as expected."""

        self.compare_dicts(self.voltalis_provider._manual_settings, expected_manual_settings)
