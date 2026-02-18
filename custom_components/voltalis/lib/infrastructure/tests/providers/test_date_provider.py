import time
from collections.abc import Generator
from datetime import UTC, datetime
from typing import TypeAlias

import pytest

from custom_components.voltalis.lib.infrastructure.providers.date_provider_real import DateProviderReal
from custom_components.voltalis.lib.infrastructure.providers.date_provider_stub import DateProviderStub
from custom_components.voltalis.tests.base_fixture import BaseFixture


@pytest.mark.integration
def test_get_now(fixture: "DateProviderFixture") -> None:
    """Test get now."""

    # Arrange
    now = datetime(2021, 1, 1) if fixture.provider_type == DateProviderStub else datetime.now().replace(microsecond=0)
    fixture.given_now(now)

    # Act
    result = fixture.provider.get_now()

    # Assert
    assert type(result) is type(now)
    assert (now - result).total_seconds() < 1


@pytest.mark.integration
def test_get_now_multiple(fixture: "DateProviderFixture") -> None:
    """Test get now multiple times."""

    # Arrange
    now = datetime(2021, 1, 1) if fixture.provider_type == DateProviderStub else datetime.now().replace(microsecond=0)
    fixture.given_now(now)

    # Act
    result1 = fixture.provider.get_now()
    time.sleep(1)  # Wait 1 second to be sure that the time has changed
    result2 = fixture.provider.get_now()

    # Assert
    if fixture.provider_type == DateProviderStub:
        assert result1 == result2
    else:
        assert result1 != result2


@pytest.mark.integration
def test_get_now_with_timezone(fixture: "DateProviderFixture") -> None:
    """Test get now with timezone."""

    # Arrange
    now = datetime(2021, 1, 1) if fixture.provider_type == DateProviderStub else datetime.now().replace(microsecond=0)
    fixture.given_now(now)

    # Act
    result = fixture.provider.get_now(tz=UTC)

    # Assert
    expected_result = now.astimezone(UTC)
    assert type(result) is type(expected_result)
    assert (expected_result - result).total_seconds() < 1


class DateProviderFixture(BaseFixture):
    """DateProvider fixture."""

    # Define the type of the providers to test
    TestedProvidersType: TypeAlias = DateProviderStub | DateProviderReal

    # Define the tested providers
    TESTED_PROVIDERS = [
        DateProviderStub,
        DateProviderReal,
    ]

    def __init__(
        self,
        *,
        provider_type: type[TestedProvidersType],
    ) -> None:
        self.provider_type = provider_type
        self.provider = self.__get_provider(provider_type=self.provider_type)

    def before_each(self) -> None:
        if isinstance(self.provider, DateProviderStub):
            self.provider.now = DateProviderStub.DEFAULT_NOW

        if isinstance(self.provider, DateProviderReal):
            pass

    def __get_provider(self, *, provider_type: type[TestedProvidersType]) -> TestedProvidersType:
        """Get the provider depends on the provider type."""

        # Initialize the in-memory provider
        if provider_type == DateProviderStub:
            return DateProviderStub()

        # Initialize the voltalis-api provider
        if provider_type == DateProviderReal:
            return DateProviderReal()

        raise ValueError("Unknown provider type")

    # --------------------------------------
    # Arrange
    # --------------------------------------
    def given_now(self, now: datetime) -> None:
        """Set existing devices in the provider."""
        if isinstance(self.provider, DateProviderStub):
            self.provider.now = now
            return

        if isinstance(self.provider, DateProviderReal):
            return

        raise ValueError("Unknown provider type")


@pytest.fixture(scope="module", params=DateProviderFixture.TESTED_PROVIDERS)
def fixture_all(request: pytest.FixtureRequest) -> Generator[DateProviderFixture, None]:
    """
    Before all tests, start the server.
    Then after all tests, stop the server.
    """
    fixture = DateProviderFixture(provider_type=request.param)
    yield fixture


@pytest.fixture(scope="function")
def fixture(fixture_all: DateProviderFixture) -> Generator[DateProviderFixture, None]:
    """Before each test, initialize the collection."""
    fixture_all.before_each()
    yield fixture_all
