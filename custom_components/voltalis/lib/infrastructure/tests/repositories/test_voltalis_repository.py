from collections.abc import Generator
from typing import TypeAlias

import pytest

from custom_components.voltalis.lib.domain.models.device import (
    VoltalisDevice,
    VoltalisDeviceProgrammingStatus,
    VoltalisDeviceProgTypeEnum,
)
from custom_components.voltalis.lib.infrastructure.repositories.voltalis_repository_in_memory import (
    VoltalisRepositoryInMemory,
)
from custom_components.voltalis.lib.infrastructure.repositories.voltalis_repository_voltalis_api import (
    VoltalisRepositoryVoltalisApi,
)
from custom_components.voltalis.tests.base_fixture import BaseFixture
from custom_components.voltalis.tests.utils.mock_voltalis_server import MockVoltalisServer


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get(fixture: "VoltalisRepositoryFixture") -> None:
    """Test get method with filters."""

    devices = {
        1: VoltalisDevice(
            id=1,
            name="Device 1",
            type="type1",
            modulator_type="mod1",
            available_modes=[],
            programming=VoltalisDeviceProgrammingStatus(
                prog_type=VoltalisDeviceProgTypeEnum.DEFAULT,
            ),
        ),
        2: VoltalisDevice(
            id=2,
            name="Device 2",
            type="type2",
            modulator_type="mod2",
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
        self.voltalis_server = MockVoltalisServer()

        self.repository = self.__get_repository(repository_type=repository_type)

    def after_all(self) -> None:
        if self.repository_type == VoltalisRepositoryVoltalisApi:
            self.voltalis_server.stop_server()

    def before_each(self) -> None:
        if isinstance(self.repository, VoltalisRepositoryInMemory):
            self.repository.set_devices({})
            self.repository.set_devices_health({})
            self.repository.set_devices_consumptions({})
            self.repository.set_manual_settings({})

        if isinstance(self.repository, VoltalisRepositoryVoltalisApi):
            self.voltalis_server.reset_storage()

    def __get_repository(self, *, repository_type: type[TestedRepositoriesType]) -> TestedRepositoriesType:
        """Get the repository depends on the repository type."""

        # Initialize the in-memory repository
        if repository_type == VoltalisRepositoryInMemory:
            return VoltalisRepositoryInMemory()

        # Initialize the mongo repository
        if repository_type == VoltalisRepositoryVoltalisApi:
            self.voltalis_server.start_server()
            return VoltalisRepositoryVoltalisApi(http_client=self.voltalis_server.get_client())

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
            self.voltalis_server.set_devices(devices)
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
