import pytest
from homeassistant.core import HomeAssistant

from custom_components.voltalis.config_flow import VoltalisConfigFlow


@pytest.mark.asyncio
async def test_config_flow_creates_entry(hass: HomeAssistant) -> None:
    """Teste que le config flow crée bien une entry."""

    flow = VoltalisConfigFlow()
    flow.hass = hass

    user_input = {
        "username": "test@example.com",
        "password": "secret",
    }

    result = await flow.async_step_user(user_input)

    assert result["type"] == "create_entry"
    assert result["title"] == "test@example.com"
    assert result["data"]["username"] == "test@example.com"
    assert result["data"]["password"] == "secret"
