import time
from datetime import datetime

import pytest

from custom_components.voltalis.lib.infrastructure.date_provider_stub import DateProviderStub


@pytest.mark.integration
def test_get_now() -> None:
    """Test get now."""

    # Arrange
    date_provider = DateProviderStub()
    date_provider.now = datetime(2021, 1, 1)

    # Act
    result = date_provider.get_now()

    # Assert
    result_should_be = datetime(2021, 1, 1)
    assert type(result) is type(result_should_be)
    assert (result_should_be - result).total_seconds() < 1


@pytest.mark.integration
def test_get_now_multiple() -> None:
    """Test get now multiple times."""

    # Arrange
    date_provider = DateProviderStub()
    date_provider.now = datetime(2021, 1, 1)

    # Act
    result1 = date_provider.get_now()
    time.sleep(1)  # Wait 1 second to be sure that the time has changed
    result2 = date_provider.get_now()

    # Assert
    assert result1 == result2


@pytest.mark.integration
def test_get_now_utc() -> None:
    """Test get now on UTC."""

    # Arrange
    date_provider = DateProviderStub()
    date_provider.now_utc = datetime(2021, 1, 1)

    # Act
    result_should_be = datetime(2021, 1, 1)
    result = date_provider.get_now_utc()

    # Assert
    assert type(result) is type(result_should_be)
    assert (result_should_be - result).total_seconds() < 1


@pytest.mark.integration
def test_get_now_utc_multiple() -> None:
    """Test get now on UTC multiple times."""

    # Arrange
    date_provider = DateProviderStub()
    date_provider.now_utc = datetime(2021, 1, 1)

    # Act
    result1 = date_provider.get_now_utc()
    time.sleep(1)  # Wait 1 second to be sure that the time has changed
    result2 = date_provider.get_now_utc()

    # Assert
    assert result1 == result2
