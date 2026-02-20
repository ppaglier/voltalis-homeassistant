"""Base fixture class for Home Assistant E2E tests."""

from datetime import datetime

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest import MonkeyPatch

from custom_components.voltalis.apps.home_assistant.entities.config_entry_data import VoltalisConfigEntry
from custom_components.voltalis.const import DOMAIN
from custom_components.voltalis.lib.domain.devices_management.climates.manual_setting_builder import (
    ManualSettingBuilder,
)
from custom_components.voltalis.lib.domain.devices_management.devices.device_builder import DeviceBuilder
from custom_components.voltalis.lib.domain.devices_management.devices.device_enum import DeviceModeEnum, DeviceTypeEnum
from custom_components.voltalis.lib.domain.devices_management.health.device_health import DeviceHealthStatusEnum
from custom_components.voltalis.lib.domain.devices_management.health.device_health_builder import DeviceHealthBuilder
from custom_components.voltalis.lib.domain.energy_contracts.energy_contract_builder import EnergyContractBuilder
from custom_components.voltalis.lib.domain.energy_contracts.energy_contract_enum import EnergyContractTypeEnum
from custom_components.voltalis.lib.domain.energy_contracts.live_consumption import LiveConsumption
from custom_components.voltalis.lib.domain.programs_management.programs.program_builder import ProgramBuilder
from custom_components.voltalis.tests.utils.base_fixture import BaseFixture
from custom_components.voltalis.tests.utils.mock_voltalis_server import MockVoltalisServer


class HomeAssistantFixture(BaseFixture[None]):
    """Base fixture class for Home Assistant E2E tests."""

    def __init__(self) -> None:
        """Initialize the fixture.

        Args:
            hass: Home Assistant instance
            monkeypatch: pytest MonkeyPatch instance
        """
        super().__init__()
        self.voltalis_server = MockVoltalisServer()

    async def async_before_all(self) -> None:
        """Set up before all tests - called once at the start."""
        await self.voltalis_server.start_server()

    async def async_after_all(self) -> None:
        """Clean up after all tests - called once at the end."""
        await self.voltalis_server.stop_server()

    async def async_before_each(self) -> None:
        """Set up before each test - called before each test function.

        Resets the server and initializes default devices/settings.
        """
        await super().async_before_each()

        # Reset and configure the mock server
        self.voltalis_server.reset_storage()

    def setup_before_test(
        self,
        *,
        hass: HomeAssistant,
        monkeypatch: MonkeyPatch,
    ) -> None:
        """Set up the Home Assistant fixture.

        Args:
            hass: Home Assistant instance
            monkeypatch: pytest MonkeyPatch instance
        """
        self.hass = hass

        monkeypatch.setattr(
            "custom_components.voltalis.config_flow.VoltalisClientAiohttp",
            lambda session, **kwargs: self.voltalis_server.get_client(),
        )

        monkeypatch.setattr(
            "custom_components.voltalis.apps.home_assistant.home_assistant_module.VoltalisClientAiohttp",
            lambda session, **kwargs: self.voltalis_server.get_client(),
        )

    def get_config_entry(self) -> VoltalisConfigEntry:
        return self.hass.config_entries.async_entries(DOMAIN)[0]

    async def configure_entry(
        self,
        username: str = "test@example.com",
        password: str = "secret",
    ) -> None:
        """Configure the integration entry via config flow.

        Args:
            username: Username for the config flow
            password: Password for the config flow
        """
        # Start the flow
        init_result = await self.hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        assert init_result["type"] == FlowResultType.FORM

        # Submit credentials
        result = await self.hass.config_entries.flow.async_configure(
            init_result["flow_id"],
            user_input={
                "username": username,
                "password": password,
            },
        )
        assert result["type"] == FlowResultType.CREATE_ENTRY

        # Wait for setup to complete
        await self.hass.async_block_till_done(True)

    def init_provider_with_data(self) -> None:
        """Set up devices in the mock server.

        Args:
            devices: List of device dictionaries to set up in the server
        """
        self.voltalis_server.given_login_ok()
        self.init_devices()
        self.init_devices_health()
        self.init_live_consumption()
        self.init_devices_consumptions()
        self.init_manual_settings()
        self.init_energy_contracts()
        self.init_programs()

    def init_devices(self) -> None:
        """Set up devices in the mock server."""

        # Create test devices
        device1 = (
            DeviceBuilder()
            .with_id(1)
            .with_name("Heater 1")
            .with_type(DeviceTypeEnum.HEATER)
            .with_programming_is_on(True)
            .build()
        )

        device2 = (
            DeviceBuilder()
            .with_id(2)
            .with_name("Heater 2")
            .with_type(DeviceTypeEnum.HEATER)
            .with_available_modes([DeviceModeEnum.ON, DeviceModeEnum.ECO])
            .with_programming_is_on(False)
            .build()
        )

        device3 = (
            DeviceBuilder()
            .with_id(3)
            .with_name("Water Heater")
            .with_type(DeviceTypeEnum.WATER_HEATER)
            .with_programming_is_on(True)
            .build()
        )

        self.voltalis_server.given_devices({device1.id: device1, device2.id: device2, device3.id: device3})

    def init_devices_health(self) -> None:
        """Set up devices health in the mock server."""
        devices_health = {
            1: DeviceHealthBuilder().with_status(DeviceHealthStatusEnum.OK).build(),
            2: DeviceHealthBuilder().with_status(DeviceHealthStatusEnum.NOT_OK).build(),
            3: DeviceHealthBuilder().with_status(DeviceHealthStatusEnum.COMM_ERROR).build(),
        }
        self.voltalis_server.given_devices_health(devices_health)

    def init_live_consumption(self) -> None:
        """Set up live consumption data in the mock server."""

        self.voltalis_server.given_live_consumption(LiveConsumption(consumption=0))

    def init_devices_consumptions(self) -> None:
        """Set up devices consumption data in the mock server."""

        devices_consumptions = {
            1: [
                (datetime(2024, 1, 1, 8, 15, 0), 1.2),
                (datetime(2024, 1, 1, 9, 45, 0), 2.3),
                (datetime(2024, 1, 1, 10, 15, 0), 3.0),
            ],
            2: [
                (datetime(2024, 1, 1, 8, 15, 0), 1.2),
                (datetime(2024, 1, 1, 9, 45, 0), 2.3),
                (datetime(2024, 1, 1, 10, 15, 0), 3.0),
            ],
            3: [
                (datetime(2024, 1, 1, 8, 15, 0), 1.2),
                (datetime(2024, 1, 1, 9, 45, 0), 2.3),
                (datetime(2024, 1, 1, 10, 15, 0), 3.0),
            ],
        }

        self.voltalis_server.given_devices_consumptions(devices_consumptions)

    def init_manual_settings(self) -> None:
        """Set up manual settings in the mock server."""

        # Create and set manual settings
        manual_setting1 = ManualSettingBuilder().with_id(1).with_id_appliance(1).with_is_on(True).build()
        manual_setting2 = ManualSettingBuilder().with_id(2).with_id_appliance(2).with_is_on(False).build()
        manual_setting3 = ManualSettingBuilder().with_id(3).with_id_appliance(3).with_is_on(True).build()

        self.voltalis_server.given_manual_settings([manual_setting1, manual_setting2, manual_setting3])

    def init_energy_contracts(self) -> None:
        """Set up energy contracts in the mock server."""
        # For simplicity, we can assume a single energy contract with fixed data
        energy_contract = (
            EnergyContractBuilder()
            .with_id(1)
            .with_contract_id(1)
            .with_type(EnergyContractTypeEnum.PEAK_OFFPEAK)
            .build()
        )
        self.voltalis_server.given_energy_contracts({energy_contract.contract_id: energy_contract})

    def init_programs(self) -> None:
        """Set up programs in the mock server."""
        program1 = ProgramBuilder().with_id(1).with_name("Morning Program").build()
        self.voltalis_server.given_programs({program1.id: program1})
