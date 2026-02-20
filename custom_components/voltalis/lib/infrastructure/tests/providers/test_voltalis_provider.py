from datetime import date, datetime
from typing import AsyncGenerator, TypeAlias

import pytest

from custom_components.voltalis.lib.domain.devices_management.climates.manual_setting import (
    ManualSetting,
    ManualSettingUpdate,
)
from custom_components.voltalis.lib.domain.devices_management.climates.manual_setting_builder import (
    ManualSettingBuilder,
)
from custom_components.voltalis.lib.domain.devices_management.devices.device import Device
from custom_components.voltalis.lib.domain.devices_management.devices.device_builder import DeviceBuilder
from custom_components.voltalis.lib.domain.devices_management.devices.device_enum import (
    DeviceModeEnum,
    DeviceModulatorTypeEnum,
    DeviceTypeEnum,
)
from custom_components.voltalis.lib.domain.devices_management.health.device_health import (
    DeviceHealth,
    DeviceHealthStatusEnum,
)
from custom_components.voltalis.lib.domain.devices_management.health.device_health_builder import DeviceHealthBuilder
from custom_components.voltalis.lib.domain.energy_contracts.energy_contract import EnergyContract
from custom_components.voltalis.lib.domain.energy_contracts.energy_contract_builder import EnergyContractBuilder
from custom_components.voltalis.lib.domain.energy_contracts.live_consumption import LiveConsumption
from custom_components.voltalis.lib.domain.programs_management.programs.program import Program
from custom_components.voltalis.lib.domain.programs_management.programs.program_builder import ProgramBuilder
from custom_components.voltalis.lib.domain.programs_management.programs.program_enum import ProgramTypeEnum
from custom_components.voltalis.lib.infrastructure.providers.voltalis_provider_stub import (
    VoltalisProviderStub,
)
from custom_components.voltalis.lib.infrastructure.providers.voltalis_provider_voltalis_api import (
    VoltalisProviderVoltalisApi,
)
from custom_components.voltalis.tests.utils.base_fixture import BaseFixture
from custom_components.voltalis.tests.utils.mock_voltalis_server import MockVoltalisServer


@pytest.mark.integration
async def test_get_devices(fixture: "VoltalisProviderFixture") -> None:
    """Test get_devices method."""

    devices = {
        1: DeviceBuilder()
        .with_id(1)
        .with_name("Device 1")
        .with_type(DeviceTypeEnum.HEATER)
        .with_modulator_type(DeviceModulatorTypeEnum.VX_WIRE)
        .with_available_modes([DeviceModeEnum.COMFORT, DeviceModeEnum.ECO])
        .with_has_ecov(True)
        .build(),
        2: DeviceBuilder()
        .with_id(2)
        .with_name("Device 2")
        .with_type(DeviceTypeEnum.WATER_HEATER)
        .with_modulator_type(DeviceModulatorTypeEnum.VX_RELAY)
        .with_available_modes([DeviceModeEnum.COMFORT, DeviceModeEnum.ECO])
        .with_has_ecov(False)
        .build(),
    }

    # Arrange
    fixture.given_devices(devices)

    # Act
    result = await fixture.provider.get_devices()

    # Assert
    expected_result = devices
    fixture.compare_data(result, expected_result)


@pytest.mark.integration
async def test_get_devices_empty(fixture: "VoltalisProviderFixture") -> None:
    """Test get_devices method with no devices."""

    # Arrange
    fixture.given_devices({})

    # Act
    result = await fixture.provider.get_devices()

    # Assert
    assert result == {}


@pytest.mark.integration
async def test_get_devices_health(fixture: "VoltalisProviderFixture") -> None:
    """Test get_devices_health method."""

    devices_health = {
        1: DeviceHealthBuilder().with_status(DeviceHealthStatusEnum.OK).build(),
        2: DeviceHealthBuilder().with_status(DeviceHealthStatusEnum.NOT_OK).build(),
    }

    # Arrange
    fixture.given_devices_health(devices_health)

    # Act
    result = await fixture.provider.get_devices_health()

    # Assert
    expected_result = devices_health
    fixture.compare_data(result, expected_result)


@pytest.mark.integration
async def test_get_devices_health_empty(fixture: "VoltalisProviderFixture") -> None:
    """Test get_devices_health method with no health data."""

    # Arrange
    fixture.given_devices_health({})

    # Act
    result = await fixture.provider.get_devices_health()

    # Assert
    assert result == {}


@pytest.mark.integration
async def test_get_live_consumption(fixture: "VoltalisProviderFixture") -> None:
    """Test get_live_consumption method."""

    live_consumption = LiveConsumption(consumption=123.45)

    # Arrange
    fixture.given_live_consumption(live_consumption)

    # Act
    result = await fixture.provider.get_live_consumption()

    # Assert
    expected_result = live_consumption
    fixture.compare_data(result, expected_result)


@pytest.mark.integration
async def test_get_devices_consumptions(fixture: "VoltalisProviderFixture") -> None:
    """Test get_devices_consumptions method."""

    target_date = date(2024, 11, 24)
    target_datetime = datetime(target_date.year, target_date.month, target_date.day, 12, 0, 0)
    devices_consumptions = {
        1: [
            (datetime(2024, 11, 24, 11, 0, 0), 100.5),
            (target_datetime, 150.75),
            (datetime(2024, 11, 25, 13, 0, 0), 200.0),
        ],
        2: [
            (datetime(2024, 11, 24, 11, 0, 0), 50.25),
            (target_datetime, 75.5),
        ],
    }

    # Arrange
    fixture.given_devices_consumptions(devices_consumptions)

    # Act
    result = await fixture.provider.get_devices_daily_consumptions(target_date)

    # Assert
    expected_result = {
        1: [
            (datetime(2024, 11, 24, 11, 0, 0), 100.5),
            (target_datetime, 150.75),
        ],
        2: [(datetime(2024, 11, 24, 11, 0, 0), 50.25), (target_datetime, 75.5)],
    }
    fixture.compare_data(result, expected_result)


@pytest.mark.integration
async def test_get_devices_consumptions_no_match(fixture: "VoltalisProviderFixture") -> None:
    """Test get_devices_consumptions method with no matching datetime."""

    target_date = date(2024, 11, 25)
    devices_consumptions = {
        1: [(datetime(2024, 11, 24, 13, 0, 0), 100.5), (datetime(2024, 11, 24, 14, 0, 0), 200.0)],
    }

    # Arrange
    fixture.given_devices_consumptions(devices_consumptions)

    # Act
    result = await fixture.provider.get_devices_daily_consumptions(target_date)

    # Assert
    assert result == {1: []}


@pytest.mark.integration
async def test_get_manual_settings(fixture: "VoltalisProviderFixture") -> None:
    """Test get_manual_settings method."""

    manual_settings = [
        ManualSettingBuilder()
        .with_id(1)
        .with_enabled(True)
        .with_id_appliance(10)
        .with_until_further_notice(True)
        .with_is_on(True)
        .with_mode(DeviceModeEnum.COMFORT)
        .with_temperature_target(21.5)
        .build(),
        ManualSettingBuilder()
        .with_id(2)
        .with_enabled(False)
        .with_id_appliance(20)
        .with_until_further_notice(False)
        .with_is_on(False)
        .with_mode(DeviceModeEnum.ECO)
        .with_end_date(datetime(2024, 12, 31))
        .with_temperature_target(19.0)
        .build(),
    ]

    # Arrange
    fixture.given_manual_settings(manual_settings)

    # Act
    result = await fixture.provider.get_manual_settings()

    # Assert
    expected_result = {manual_setting.id_appliance: manual_setting for manual_setting in manual_settings}
    fixture.compare_data(result, expected_result)


@pytest.mark.integration
async def test_get_manual_settings_empty(fixture: "VoltalisProviderFixture") -> None:
    """Test get_manual_settings method with no manual settings."""

    # Arrange
    fixture.given_manual_settings([])

    # Act
    result = await fixture.provider.get_manual_settings()

    # Assert
    assert result == {}


@pytest.mark.integration
async def test_set_manual_setting(fixture: "VoltalisProviderFixture") -> None:
    """Test set_manual_setting method."""

    manual_setting_builder = (
        ManualSettingBuilder()
        .with_id(1)
        .with_enabled(True)
        .with_id_appliance(10)
        .with_until_further_notice(True)
        .with_is_on(True)
        .with_mode(DeviceModeEnum.COMFORT)
        .with_temperature_target(21.5)
    )
    manual_settings = [manual_setting_builder.build()]

    update = ManualSettingUpdate(
        enabled=True,
        id_appliance=10,
        until_further_notice=False,
        is_on=True,
        has_ecov=False,
        mode=DeviceModeEnum.ECO,
        end_date=datetime(2024, 12, 31),
        temperature_target=19.0,
    )

    # Arrange
    fixture.given_manual_settings(manual_settings)

    # Act
    await fixture.provider.set_manual_setting(1, update)

    # Assert
    result = await fixture.provider.get_manual_settings()
    expected = (
        manual_setting_builder.with_until_further_notice(update.until_further_notice)
        .with_mode(update.mode)
        .with_end_date(update.end_date)
        .with_temperature_target(update.temperature_target)
        .build()
    )
    fixture.compare_data(result[10], expected)


@pytest.mark.integration
async def test_set_manual_setting_with_ecov(fixture: "VoltalisProviderFixture") -> None:
    """Test set_manual_setting method."""

    manual_setting_builder = (
        ManualSettingBuilder()
        .with_id(1)
        .with_enabled(True)
        .with_id_appliance(10)
        .with_until_further_notice(True)
        .with_is_on(True)
        .with_mode(DeviceModeEnum.COMFORT)
        .with_temperature_target(21.5)
    )
    manual_settings = [manual_setting_builder.build()]

    update = ManualSettingUpdate(
        enabled=True,
        id_appliance=10,
        until_further_notice=False,
        is_on=True,
        has_ecov=True,
        mode=DeviceModeEnum.ECO,
        end_date=datetime(2024, 12, 31),
        temperature_target=19.0,
    )

    # Arrange
    fixture.given_manual_settings(manual_settings)

    # Act
    await fixture.provider.set_manual_setting(1, update)

    # Assert
    result = await fixture.provider.get_manual_settings()
    expected = (
        manual_setting_builder.with_until_further_notice(update.until_further_notice)
        .with_mode(update.mode)
        .with_end_date(update.end_date)
        .with_temperature_target(update.temperature_target)
        .build()
    )
    fixture.compare_data(result[10], expected)


@pytest.mark.integration
async def test_get_energy_contracts(fixture: "VoltalisProviderFixture") -> None:
    """Test get_energy_contracts method."""

    energy_contracts = {
        1: EnergyContractBuilder().with_id(1).build(),
        2: EnergyContractBuilder().with_id(2).build(),
    }
    fixture.given_energy_contracts(energy_contracts)

    # Act
    result = await fixture.provider.get_energy_contracts()

    # Assert
    expected_result = energy_contracts
    fixture.compare_data(result, expected_result)


@pytest.mark.integration
async def test_get_energy_contracts_empty(fixture: "VoltalisProviderFixture") -> None:
    """Test get_energy_contracts method with no energy contracts."""

    fixture.given_energy_contracts({})

    # Act
    result = await fixture.provider.get_energy_contracts()

    # Assert
    assert result == {}


@pytest.mark.integration
async def test_get_programs(fixture: "VoltalisProviderFixture") -> None:
    """Test get_programs method."""

    programs = {
        1: ProgramBuilder().with_id(1).with_type(ProgramTypeEnum.MANUAL).build(),
        2: ProgramBuilder().with_id(2).with_name("quicksettings-longleave").with_type(ProgramTypeEnum.QUICK).build(),
        3: ProgramBuilder().with_id(3).with_type(ProgramTypeEnum.USER).build(),
    }
    fixture.given_programs(programs)

    # Act
    result = await fixture.provider.get_programs()

    # Assert
    expected_result = {
        2: programs[2],
        3: programs[3],
    }
    fixture.compare_data(result, expected_result)


@pytest.mark.integration
async def test_toggle_program_user(fixture: "VoltalisProviderFixture") -> None:
    """Test toggle_program method."""

    program_builder = ProgramBuilder().with_id(1).with_type(ProgramTypeEnum.USER).with_enabled(False)
    program = program_builder.build()
    fixture.given_programs({1: program})

    # Act
    updated_program = program_builder.with_enabled(True).build()
    await fixture.provider.toggle_program(updated_program)

    # Assert
    result = await fixture.provider.get_programs()
    expected_result = {1: updated_program}
    fixture.compare_dicts(result, expected_result)


@pytest.mark.integration
async def test_toggle_program_quick(fixture: "VoltalisProviderFixture") -> None:
    """Test toggle_program method with a quick setting program."""

    program_builder = ProgramBuilder().with_id(1).with_type(ProgramTypeEnum.QUICK).with_enabled(False)
    program = program_builder.build()
    fixture.given_programs({1: program})

    # Act
    updated_program = program_builder.with_enabled(True).build()
    await fixture.provider.toggle_program(updated_program)

    # Assert
    result = await fixture.provider.get_programs()
    expected_result = {1: updated_program}
    fixture.compare_dicts(result, expected_result)


class VoltalisProviderFixture(BaseFixture):
    """VoltalisProvider fixture."""

    # Define the type of the providers to test
    TestedProvidersType: TypeAlias = VoltalisProviderStub | VoltalisProviderVoltalisApi

    # Define the tested providers
    # NOTE: VoltalisProviderVoltalisApi is disabled until MockVoltalisServer HTTP routes are fully implemented
    TESTED_PROVIDERS = [
        VoltalisProviderStub,
        VoltalisProviderVoltalisApi,
    ]

    def __init__(
        self,
        *,
        provider_type: type[TestedProvidersType],
    ) -> None:
        self.provider_type = provider_type
        self.voltalis_server = MockVoltalisServer()

    async def async_before_all(self) -> None:
        self.provider = await self.__get_provider(provider_type=self.provider_type)

    async def async_after_all(self) -> None:
        if self.provider_type == VoltalisProviderVoltalisApi:
            await self.voltalis_server.stop_server()

    def before_each(self) -> None:
        if isinstance(self.provider, VoltalisProviderStub):
            self.provider.set_devices({})
            self.provider.set_devices_health({})
            self.provider.set_devices_consumptions({})
            self.provider.set_manual_settings([])

        if isinstance(self.provider, VoltalisProviderVoltalisApi):
            self.voltalis_server.reset_storage()
            self.voltalis_server.given_login_ok()

    async def __get_provider(self, *, provider_type: type[TestedProvidersType]) -> TestedProvidersType:
        """Get the provider depends on the provider type."""

        # Initialize the in-memory provider
        if provider_type == VoltalisProviderStub:
            return VoltalisProviderStub()

        # Initialize the voltalis-api provider
        if provider_type == VoltalisProviderVoltalisApi:
            await self.voltalis_server.start_server()
            return VoltalisProviderVoltalisApi(http_client=self.voltalis_server.get_client())

        raise ValueError("Unknown provider type")

    # --------------------------------------
    # Arrange
    # --------------------------------------
    def given_devices(self, devices: dict[int, Device]) -> None:
        """Set existing devices in the provider."""
        if isinstance(self.provider, VoltalisProviderStub):
            self.provider.set_devices(devices)
            return

        if isinstance(self.provider, VoltalisProviderVoltalisApi):
            self.voltalis_server.given_devices(devices)
            return

        raise ValueError("Unknown provider type")

    def given_devices_health(self, devices_health: dict[int, DeviceHealth]) -> None:
        """Set existing devices health in the provider."""
        if isinstance(self.provider, VoltalisProviderStub):
            self.provider.set_devices_health(devices_health)
            return

        if isinstance(self.provider, VoltalisProviderVoltalisApi):
            self.voltalis_server.given_devices_health(devices_health)
            return

        raise ValueError("Unknown provider type")

    def given_live_consumption(self, live_consumption: LiveConsumption) -> None:
        """Set existing live consumption in the provider."""
        if isinstance(self.provider, VoltalisProviderStub):
            self.provider.set_live_consumption(live_consumption)
            return

        if isinstance(self.provider, VoltalisProviderVoltalisApi):
            self.voltalis_server.given_live_consumption(live_consumption)
            return

        raise ValueError("Unknown provider type")

    def given_devices_consumptions(self, devices_consumptions: dict[int, list[tuple[datetime, float]]]) -> None:
        """Set existing devices consumptions in the provider."""
        if isinstance(self.provider, VoltalisProviderStub):
            self.provider.set_devices_consumptions(devices_consumptions)
            return

        if isinstance(self.provider, VoltalisProviderVoltalisApi):
            self.voltalis_server.given_devices_consumptions(devices_consumptions)
            return

        raise ValueError("Unknown provider type")

    def given_manual_settings(self, manual_settings: list[ManualSetting]) -> None:
        """Set existing manual settings in the provider."""
        if isinstance(self.provider, VoltalisProviderStub):
            self.provider.set_manual_settings(manual_settings)
            return

        if isinstance(self.provider, VoltalisProviderVoltalisApi):
            self.voltalis_server.given_manual_settings(manual_settings)
            return

        raise ValueError("Unknown provider type")

    def given_energy_contracts(self, energy_contracts: dict[int, EnergyContract]) -> None:
        """Set existing energy contracts in the provider."""
        if isinstance(self.provider, VoltalisProviderStub):
            self.provider.set_energy_contracts(energy_contracts)
            return

        if isinstance(self.provider, VoltalisProviderVoltalisApi):
            self.voltalis_server.given_energy_contracts(energy_contracts)
            return

        raise ValueError("Unknown provider type")

    def given_programs(self, programs: dict[int, Program]) -> None:
        """Set existing programs in the provider."""
        if isinstance(self.provider, VoltalisProviderStub):
            self.provider.set_programs(programs)
            return

        if isinstance(self.provider, VoltalisProviderVoltalisApi):
            self.voltalis_server.given_programs(programs)
            return

        raise ValueError("Unknown provider type")


pytestmark = [pytest.mark.asyncio(loop_scope="module"), pytest.mark.enable_socket]


@pytest.fixture(scope="module", params=VoltalisProviderFixture.TESTED_PROVIDERS)
async def fixture_all(request: pytest.FixtureRequest) -> AsyncGenerator[VoltalisProviderFixture, None]:
    """
    Before all tests, start the server.
    Then after all tests, stop the server.
    """
    fixture = VoltalisProviderFixture(provider_type=request.param)
    await fixture.async_before_all()
    yield fixture
    await fixture.async_after_all()


@pytest.fixture(scope="function")
async def fixture(fixture_all: VoltalisProviderFixture) -> AsyncGenerator[VoltalisProviderFixture, None]:
    """Before each test, initialize the collection."""
    fixture_all.before_each()
    yield fixture_all
