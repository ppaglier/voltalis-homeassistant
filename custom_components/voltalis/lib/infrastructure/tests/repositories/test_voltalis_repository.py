from collections.abc import Generator
from datetime import datetime
from typing import TypeAlias

import pytest

from custom_components.voltalis.lib.domain.models.device import (
    VoltalisDevice,
    VoltalisDeviceModeEnum,
    VoltalisDeviceModulatorTypeEnum,
    VoltalisDeviceProgrammingStatus,
    VoltalisDeviceProgTypeEnum,
    VoltalisDeviceTypeEnum,
)
from custom_components.voltalis.lib.domain.models.device_health import (
    VoltalisDeviceHealth,
    VoltalisHealthStatusEnum,
)
from custom_components.voltalis.lib.domain.models.manual_setting import (
    VoltalisManualSetting,
    VoltalisManualSettingUpdate,
)
from custom_components.voltalis.lib.infrastructure.repositories.voltalis_repository_in_memory import (
    VoltalisRepositoryInMemory,
)
from custom_components.voltalis.lib.infrastructure.repositories.voltalis_repository_voltalis_api import (
    VoltalisRepositoryVoltalisApi,
)
from custom_components.voltalis.tests.base_fixture import BaseFixture


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_devices(fixture: "VoltalisRepositoryFixture") -> None:
    """Test get_devices method."""

    devices = {
        1: VoltalisDevice(
            id=1,
            name="Device 1",
            type=VoltalisDeviceTypeEnum.HEATER,
            modulator_type=VoltalisDeviceModulatorTypeEnum.VX_WIRE,
            available_modes=[],
            programming=VoltalisDeviceProgrammingStatus(
                prog_type=VoltalisDeviceProgTypeEnum.DEFAULT,
            ),
        ),
        2: VoltalisDevice(
            id=2,
            name="Device 2",
            type=VoltalisDeviceTypeEnum.WATER_HEATER,
            modulator_type=VoltalisDeviceModulatorTypeEnum.VX_RELAY,
            available_modes=[],
            programming=VoltalisDeviceProgrammingStatus(
                prog_type=VoltalisDeviceProgTypeEnum.DEFAULT,
            ),
        ),
    }

    # Arrange
    fixture.given_devices(devices)

    # Act
    result = await fixture.repository.get_devices()

    # Assert
    expected_result = devices
    fixture.compare_data(result, expected_result)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_devices_empty(fixture: "VoltalisRepositoryFixture") -> None:
    """Test get_devices method with no devices."""

    # Arrange
    fixture.given_devices({})

    # Act
    result = await fixture.repository.get_devices()

    # Assert
    assert result == {}


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_devices_health(fixture: "VoltalisRepositoryFixture") -> None:
    """Test get_devices_health method."""

    devices_health = {
        1: VoltalisDeviceHealth(status=VoltalisHealthStatusEnum.OK),
        2: VoltalisDeviceHealth(status=VoltalisHealthStatusEnum.NOT_OK),
    }

    # Arrange
    fixture.given_devices_health(devices_health)

    # Act
    result = await fixture.repository.get_devices_health()

    # Assert
    expected_result = devices_health
    fixture.compare_data(result, expected_result)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_devices_health_empty(fixture: "VoltalisRepositoryFixture") -> None:
    """Test get_devices_health method with no health data."""

    # Arrange
    fixture.given_devices_health({})

    # Act
    result = await fixture.repository.get_devices_health()

    # Assert
    assert result == {}


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_devices_consumptions(fixture: "VoltalisRepositoryFixture") -> None:
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
    result = await fixture.repository.get_devices_consumptions(target_datetime)

    # Assert
    expected_result = {1: 150.75, 2: 75.5}
    fixture.compare_data(result, expected_result)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_devices_consumptions_no_match(fixture: "VoltalisRepositoryFixture") -> None:
    """Test get_devices_consumptions method with no matching datetime."""

    target_datetime = datetime(2024, 11, 24, 12, 0, 0)
    devices_consumptions = {
        1: [(datetime(2024, 11, 24, 11, 0, 0), 100.5), (datetime(2024, 11, 24, 13, 0, 0), 200.0)],
    }

    # Arrange
    fixture.given_devices_consumptions(devices_consumptions)

    # Act
    result = await fixture.repository.get_devices_consumptions(target_datetime)

    # Assert
    assert result == {}


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_manual_settings(fixture: "VoltalisRepositoryFixture") -> None:
    """Test get_manual_settings method."""

    manual_settings = {
        1: VoltalisManualSetting(
            id=1,
            enabled=True,
            id_appliance=10,
            until_further_notice=True,
            is_on=True,
            mode=VoltalisDeviceModeEnum.CONFORT,
            temperature_target=21.5,
        ),
        2: VoltalisManualSetting(
            id=2,
            enabled=False,
            id_appliance=20,
            until_further_notice=False,
            is_on=False,
            mode=VoltalisDeviceModeEnum.ECO,
            end_date="2024-12-31",
            temperature_target=19.0,
        ),
    }

    # Arrange
    fixture.given_manual_settings(manual_settings)

    # Act
    result = await fixture.repository.get_manual_settings()

    # Assert
    expected_result = manual_settings
    fixture.compare_data(result, expected_result)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_manual_settings_empty(fixture: "VoltalisRepositoryFixture") -> None:
    """Test get_manual_settings method with no manual settings."""

    # Arrange
    fixture.given_manual_settings({})

    # Act
    result = await fixture.repository.get_manual_settings()

    # Assert
    assert result == {}


@pytest.mark.asyncio
@pytest.mark.integration
async def test_set_manual_setting(fixture: "VoltalisRepositoryFixture") -> None:
    """Test set_manual_setting method."""

    manual_settings = {
        1: VoltalisManualSetting(
            id=1,
            enabled=True,
            id_appliance=10,
            until_further_notice=True,
            is_on=True,
            mode=VoltalisDeviceModeEnum.CONFORT,
            temperature_target=21.5,
        ),
    }

    update = VoltalisManualSettingUpdate(
        enabled=True,
        id_appliance=10,
        until_further_notice=False,
        is_on=True,
        mode=VoltalisDeviceModeEnum.ECO,
        end_date="2024-12-31",
        temperature_target=19.0,
    )

    # Arrange
    fixture.given_manual_settings(manual_settings)

    # Act
    await fixture.repository.set_manual_setting(1, update)

    # Assert
    result = await fixture.repository.get_manual_settings()
    expected = VoltalisManualSetting(
        id=1,
        enabled=True,
        id_appliance=10,
        until_further_notice=False,
        is_on=True,
        mode=VoltalisDeviceModeEnum.ECO,
        end_date="2024-12-31",
        temperature_target=19.0,
    )
    fixture.compare_data(result[1], expected)


class VoltalisRepositoryFixture(BaseFixture):
    """VoltalisRepository fixture."""

    # Define the type of the repositories to test
    TestedRepositoriesType: TypeAlias = VoltalisRepositoryInMemory | VoltalisRepositoryVoltalisApi

    # Define the tested repositories
    TESTED_REPOSITORIES = [
        VoltalisRepositoryInMemory,
        # VoltalisRepositoryVoltalisApi,
    ]

    def __init__(
        self,
        *,
        repository_type: type[TestedRepositoriesType],
    ) -> None:
        self.repository_type = repository_type
        # self.voltalis_server = MockVoltalisServer()

        self.repository = self.__get_repository(repository_type=repository_type)

    def after_all(self) -> None:
        # if self.repository_type == VoltalisRepositoryVoltalisApi:
        #     self.voltalis_server.stop_server()
        pass

    def before_each(self) -> None:
        if isinstance(self.repository, VoltalisRepositoryInMemory):
            self.repository.set_devices({})
            self.repository.set_devices_health({})
            self.repository.set_devices_consumptions({})
            self.repository.set_manual_settings({})

        # if isinstance(self.repository, VoltalisRepositoryVoltalisApi):
        #     self.voltalis_server.reset_storage()

    def __get_repository(self, *, repository_type: type[TestedRepositoriesType]) -> TestedRepositoriesType:
        """Get the repository depends on the repository type."""

        # Initialize the in-memory repository
        if repository_type == VoltalisRepositoryInMemory:
            return VoltalisRepositoryInMemory()

        # Initialize the mongo repository
        # if repository_type == VoltalisRepositoryVoltalisApi:
        #     self.voltalis_server.start_server()
        #     return VoltalisRepositoryVoltalisApi(http_client=self.voltalis_server.get_client())

        raise ValueError("Unknown repository type")

    # --------------------------------------
    # Arrange
    # --------------------------------------
    def given_devices(self, devices: dict[int, VoltalisDevice]) -> None:
        """Set existing devices in the repository."""
        if isinstance(self.repository, VoltalisRepositoryInMemory):
            self.repository.set_devices(devices)
            return

        if isinstance(self.repository, VoltalisRepositoryVoltalisApi):
            # self.voltalis_server.set_devices(devices)
            return

        raise ValueError("Unknown repository type")

    def given_devices_health(self, devices_health: dict[int, VoltalisDeviceHealth]) -> None:
        """Set existing devices health in the repository."""
        if isinstance(self.repository, VoltalisRepositoryInMemory):
            self.repository.set_devices_health(devices_health)
            return

        if isinstance(self.repository, VoltalisRepositoryVoltalisApi):
            # self.voltalis_server.set_devices_health(devices_health)
            return

        raise ValueError("Unknown repository type")

    def given_devices_consumptions(self, devices_consumptions: dict[int, list[tuple[datetime, float]]]) -> None:
        """Set existing devices consumptions in the repository."""
        if isinstance(self.repository, VoltalisRepositoryInMemory):
            self.repository.set_devices_consumptions(devices_consumptions)
            return

        if isinstance(self.repository, VoltalisRepositoryVoltalisApi):
            # self.voltalis_server.set_devices_consumptions(devices_consumptions)
            return

        raise ValueError("Unknown repository type")

    def given_manual_settings(self, manual_settings: dict[int, VoltalisManualSetting]) -> None:
        """Set existing manual settings in the repository."""
        if isinstance(self.repository, VoltalisRepositoryInMemory):
            self.repository.set_manual_settings(manual_settings)
            return

        if isinstance(self.repository, VoltalisRepositoryVoltalisApi):
            # self.voltalis_server.set_manual_settings(manual_settings)
            return

        raise ValueError("Unknown repository type")


@pytest.fixture(scope="module", params=VoltalisRepositoryFixture.TESTED_REPOSITORIES)
def fixture_all(request: pytest.FixtureRequest) -> Generator[VoltalisRepositoryFixture, None, None]:
    """
    Before all tests, start the server.
    Then after all tests, stop the server.
    """
    fixture = VoltalisRepositoryFixture(repository_type=request.param)
    yield fixture
    fixture.after_all()


@pytest.fixture
def fixture(
    fixture_all: VoltalisRepositoryFixture,
) -> Generator[VoltalisRepositoryFixture, None, None]:
    """Before each test, initialize the collection."""
    fixture_all.before_each()
    yield fixture_all
