"""Configuration for Voltalis integration tests."""

from collections.abc import Generator
from typing import Any

import pytest


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations: Any) -> Generator[None, None, None]:
    """Enable custom integrations for all tests."""
    yield
