"""Top-level test configuration for Voltalis integration."""

import logging
from collections.abc import Generator
from typing import Any

import pytest
import pytest_socket

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


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_fixture_setup(
    fixturedef: pytest.FixtureDef[Any], request: pytest.FixtureRequest
) -> Generator[None, None, None]:
    """Enable sockets before setting up fixtures for tests marked with enable_socket."""
    # Check if any test using this fixture has the enable_socket marker
    # Traverse up the test node hierarchy to find markers
    node = request.node
    while node is not None:
        if hasattr(node, "get_closest_marker") and node.get_closest_marker("enable_socket"):
            pytest_socket.enable_socket()
            break
        node = node.parent if hasattr(node, "parent") else None

    yield
