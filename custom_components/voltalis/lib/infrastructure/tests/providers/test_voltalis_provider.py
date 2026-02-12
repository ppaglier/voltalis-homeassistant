from collections.abc import Generator
from datetime import datetime
from typing import TypeAlias

import pytest

from custom_components.voltalis.lib.domain.devices_management.climates.manual_setting import (
    ManualSetting,
    ManualSettingUpdate,
)
from custom_components.voltalis.lib.domain.devices_management.consumptions.device_consumption import (
    DeviceConsumption,
)
from custom_components.voltalis.lib.domain.devices_management.devices.device import (
    Device,
    DeviceProgramming,
)
from custom_components.voltalis.lib.domain.devices_management.devices.device_enum import (
    DeviceModeEnum,
    DeviceModulatorTypeEnum,
    DeviceTypeEnum,
)
from custom_components.voltalis.lib.domain.devices_management.health.device_health import (
    DeviceHealth,
    DeviceHealthStatusEnum,
)
from custom_components.voltalis.lib.domain.voltalis_programs_management.programs.program_enum import ProgramTypeEnum
from custom_components.voltalis.lib.infrastructure.providers.voltalis_provider_stub import (
    VoltalisProviderStub,
)
from custom_components.voltalis.lib.infrastructure.providers.voltalis_provider_voltalis_api import (
    VoltalisProviderVoltalisApi,
)
from custom_components.voltalis.tests.base_fixture import BaseFixture


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_devices(fixture: "VoltalisProviderFixture") -> None:
    """Test get_devices method."""

    devices = {
        1: Device(
            id=1,
            name="Device 1",
            type=DeviceTypeEnum.HEATER,
            modulator_type=DeviceModulatorTypeEnum.VX_WIRE,
            available_modes=[],
            programming=DeviceProgramming(
                prog_type=ProgramTypeEnum.DEFAULT,
            ),
        ),
        2: Device(
            id=2,
            name="Device 2",
            type=DeviceTypeEnum.WATER_HEATER,
            modulator_type=DeviceModulatorTypeEnum.VX_RELAY,
            available_modes=[],
            programming=DeviceProgramming(
                prog_type=ProgramTypeEnum.DEFAULT,
            ),
        ),
    }

    # Arrange
    fixture.given_devices(devices)

    # Act
    result = await fixture.provider.get_devices()

    # Assert
    expected_result = devices
    fixture.compare_data(result, expected_result)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_devices_empty(fixture: "VoltalisProviderFixture") -> None:
    """Test get_devices method with no devices."""

    # Arrange
    fixture.given_devices({})

    # Act
    result = await fixture.provider.get_devices()

    # Assert
    assert result == {}


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_devices_health(fixture: "VoltalisProviderFixture") -> None:
    """Test get_devices_health method."""

    devices_health = {
        1: DeviceHealth(status=DeviceHealthStatusEnum.OK),
        2: DeviceHealth(status=DeviceHealthStatusEnum.NOT_OK),
    }

    # Arrange
    fixture.given_devices_health(devices_health)

    # Act
    result = await fixture.provider.get_devices_health()

    # Assert
    expected_result = devices_health
    fixture.compare_data(result, expected_result)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_devices_health_empty(fixture: "VoltalisProviderFixture") -> None:
    """Test get_devices_health method with no health data."""

    # Arrange
    fixture.given_devices_health({})

    # Act
    result = await fixture.provider.get_devices_health()

    # Assert
    assert result == {}


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_devices_consumptions(fixture: "VoltalisProviderFixture") -> None:
    """Test get_devices_consumptions method."""

    target_datetime = datetime(2024, 11, 24, 12, 0, 0)
    devices_consumptions = {
        1: [
            (datetime(2024, 11, 24, 11, 0, 0), 100.5),
            (target_datetime, 150.75),
            (datetime(2024, 11, 24, 13, 0, 0), 200.0),
        ],
        2: [(datetime(2024, 11, 24, 11, 0, 0), 50.25), (target_datetime, 75.5)],
    }

    # Arrange
    fixture.given_devices_consumptions(devices_consumptions)

    # Act
    result = await fixture.provider.get_devices_daily_consumptions(target_datetime)

    # Assert
    expected_result = {
        1: DeviceConsumption(daily_consumption=100.5 + 150.75),
        2: DeviceConsumption(daily_consumption=50.25 + 75.5),
    }
    fixture.compare_data(result, expected_result)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_devices_consumptions_no_match(fixture: "VoltalisProviderFixture") -> None:
    """Test get_devices_consumptions method with no matching datetime."""

    target_datetime = datetime(2024, 11, 24, 12, 0, 0)
    devices_consumptions = {
        1: [(datetime(2024, 11, 24, 13, 0, 0), 100.5), (datetime(2024, 11, 24, 14, 0, 0), 200.0)],
    }

    # Arrange
    fixture.given_devices_consumptions(devices_consumptions)

    # Act
    result = await fixture.provider.get_devices_daily_consumptions(target_datetime)

    # Assert
    assert result == {1: DeviceConsumption(daily_consumption=0.0)}


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_manual_settings(fixture: "VoltalisProviderFixture") -> None:
    """Test get_manual_settings method."""

    manual_settings = {
        1: ManualSetting(
            id=1,
            enabled=True,
            id_appliance=10,
            until_further_notice=True,
            is_on=True,
            mode=DeviceModeEnum.CONFORT,
            temperature_target=21.5,
        ),
        2: ManualSetting(
            id=2,
            enabled=False,
            id_appliance=20,
            until_further_notice=False,
            is_on=False,
            mode=DeviceModeEnum.ECO,
            end_date="2024-12-31",
            temperature_target=19.0,
        ),
    }

    # Arrange
    fixture.given_manual_settings(manual_settings)

    # Act
    result = await fixture.provider.get_manual_settings()

    # Assert
    expected_result = manual_settings
    fixture.compare_data(result, expected_result)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_manual_settings_empty(fixture: "VoltalisProviderFixture") -> None:
    """Test get_manual_settings method with no manual settings."""

    # Arrange
    fixture.given_manual_settings({})

    # Act
    result = await fixture.provider.get_manual_settings()

    # Assert
    assert result == {}


@pytest.mark.asyncio
@pytest.mark.integration
async def test_set_manual_setting(fixture: "VoltalisProviderFixture") -> None:
    """Test set_manual_setting method."""

    manual_settings = {
        1: ManualSetting(
            id=1,
            enabled=True,
            id_appliance=10,
            until_further_notice=True,
            is_on=True,
            mode=DeviceModeEnum.CONFORT,
            temperature_target=21.5,
        ),
    }

    update = ManualSettingUpdate(
        enabled=True,
        id_appliance=10,
        until_further_notice=False,
        is_on=True,
        mode=DeviceModeEnum.ECO,
        end_date="2024-12-31",
        temperature_target=19.0,
    )

    # Arrange
    fixture.given_manual_settings(manual_settings)

    # Act
    await fixture.provider.set_manual_setting(1, update)

    # Assert
    result = await fixture.provider.get_manual_settings()
    expected = ManualSetting(
        id=1,
        enabled=True,
        id_appliance=10,
        until_further_notice=False,
        is_on=True,
        mode=DeviceModeEnum.ECO,
        end_date="2024-12-31",
        temperature_target=19.0,
    )
    fixture.compare_data(result[1], expected)


class VoltalisProviderFixture(BaseFixture):
    """VoltalisProvider fixture."""

    # Define the type of the providers to test
    TestedProvidersType: TypeAlias = VoltalisProviderStub | VoltalisProviderVoltalisApi

    # Define the tested providers
    TESTED_PROVIDERS = [
        VoltalisProviderStub,
        # VoltalisProviderVoltalisApi,
    ]

    def __init__(
        self,
        *,
        provider_type: type[TestedProvidersType],
    ) -> None:
        self.provider_type = provider_type
        # self.voltalis_server = MockVoltalisServer()

        self.provider = self.__get_provider(provider_type=provider_type)

    def after_all(self) -> None:
        # if self.provider_type == VoltalisProviderVoltalisApi:
        #     self.voltalis_server.stop_server()
        pass

    def before_each(self) -> None:
        if isinstance(self.provider, VoltalisProviderStub):
            self.provider.set_devices({})
            self.provider.set_devices_health({})
            self.provider.set_devices_consumptions({})
            self.provider.set_manual_settings({})

        # if isinstance(self.provider, VoltalisProviderVoltalisApi):
        #     self.voltalis_server.reset_storage()

    def __get_provider(self, *, provider_type: type[TestedProvidersType]) -> TestedProvidersType:
        """Get the provider depends on the provider type."""

        # Initialize the in-memory provider
        if provider_type == VoltalisProviderStub:
            return VoltalisProviderStub()

        # Initialize the voltalis-api provider
        # if provider_type == VoltalisProviderVoltalisApi:
        #     self.voltalis_server.start_server()
        #     return VoltalisProviderVoltalisApi(http_client=self.voltalis_server.get_client())

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
            # self.voltalis_server.set_devices(devices)
            return

        raise ValueError("Unknown provider type")

    def given_devices_health(self, devices_health: dict[int, DeviceHealth]) -> None:
        """Set existing devices health in the provider."""
        if isinstance(self.provider, VoltalisProviderStub):
            self.provider.set_devices_health(devices_health)
            return

        if isinstance(self.provider, VoltalisProviderVoltalisApi):
            # self.voltalis_server.set_devices_health(devices_health)
            return

        raise ValueError("Unknown provider type")

    def given_devices_consumptions(self, devices_consumptions: dict[int, list[tuple[datetime, float]]]) -> None:
        """Set existing devices consumptions in the provider."""
        if isinstance(self.provider, VoltalisProviderStub):
            self.provider.set_devices_consumptions(devices_consumptions)
            return

        if isinstance(self.provider, VoltalisProviderVoltalisApi):
            # self.voltalis_server.set_devices_consumptions(devices_consumptions)
            return

        raise ValueError("Unknown provider type")

    def given_manual_settings(self, manual_settings: dict[int, ManualSetting]) -> None:
        """Set existing manual settings in the provider."""
        if isinstance(self.provider, VoltalisProviderStub):
            self.provider.set_manual_settings(manual_settings)
            return

        if isinstance(self.provider, VoltalisProviderVoltalisApi):
            # self.voltalis_server.set_manual_settings(manual_settings)
            return

        raise ValueError("Unknown provider type")


@pytest.fixture(scope="module", params=VoltalisProviderFixture.TESTED_PROVIDERS)
def fixture_all(request: pytest.FixtureRequest) -> Generator[VoltalisProviderFixture, None, None]:
    """
    Before all tests, start the server.
    Then after all tests, stop the server.
    """
    fixture = VoltalisProviderFixture(provider_type=request.param)
    yield fixture
    fixture.after_all()


@pytest.fixture
def fixture(
    fixture_all: VoltalisProviderFixture,
) -> Generator[VoltalisProviderFixture, None, None]:
    """Before each test, initialize the collection."""
    fixture_all.before_each()
    yield fixture_all
