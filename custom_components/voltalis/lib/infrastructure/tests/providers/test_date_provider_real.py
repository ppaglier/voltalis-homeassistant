import time
from datetime import UTC, datetime

import pytest

from custom_components.voltalis.lib.infrastructure.providers.date_provider_real import DateProviderReal


@pytest.mark.integration
def test_get_now() -> None:
    """Test get now."""

    # Arrange
    date_provider = DateProviderReal()

    # Act
    result = date_provider.get_now()

    # Assert
    result_should_be = datetime.now().replace(microsecond=0)
    assert type(result) is type(result_should_be)
    assert (result_should_be - result).total_seconds() < 1


@pytest.mark.integration
def test_get_now_multiple() -> None:
    """Test get now multiple times."""

    # Arrange
    date_provider = DateProviderReal()

    # Act
    result1 = date_provider.get_now()
    time.sleep(1)  # Wait 1 second to be sure that the time has changed
    result2 = date_provider.get_now()

    # Assert
    assert result1 != result2


@pytest.mark.integration
def test_get_now_utc() -> None:
    """Test get now on UTC."""

    # Arrange
    date_provider = DateProviderReal()

    # Act
    result = date_provider.get_now_utc()
    result_should_be = datetime.now(UTC)

    # Assert
    assert type(result) is type(result_should_be)
    assert (result_should_be - result).total_seconds() < 1


@pytest.mark.integration
def test_get_now_utc_multiple() -> None:
    """Test get now on UTC multiple times."""

    # Arrange
    date_provider = DateProviderReal()

    # Act
    result1 = date_provider.get_now_utc()
    time.sleep(1)  # Wait 1 second to be sure that the time has changed
    result2 = date_provider.get_now_utc()

    # Assert
    assert result1 != result2
