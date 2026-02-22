"""Top-level test configuration for Voltalis integration."""

import logging
from collections.abc import Generator
from typing import Any

import pytest

pytest_plugins = ["pytest_homeassistant_custom_component"]


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations: Any) -> Generator[None, None, None]:
    """Enable custom integrations for all tests."""
    yield


@pytest.fixture(autouse=True)
def configure_logging(caplog: pytest.LogCaptureFixture) -> Generator[None, None, None]:
    """Configure logging for home assistant to display only warnings and above."""
    # Configure Home Assistant logging
    logging.getLogger("homeassistant").setLevel(logging.WARNING)

    # Configure the caplog fixture to capture warnings and above
    caplog.set_level(logging.WARNING)

    yield
