import pytest
from homeassistant.core import HomeAssistant

from custom_components.voltalis.config_flow import VoltalisConfigFlow
from custom_components.voltalis.const import CONF_PASSWORD, CONF_USERNAME


@pytest.mark.asyncio
async def test_config_flow_creates_entry(hass: HomeAssistant) -> None:
    """Teste que le config flow crée bien une entry."""

    flow = VoltalisConfigFlow()
    flow.hass = hass

    user_input = {
        CONF_USERNAME: "test@example.com",
        CONF_PASSWORD: "secret",
    }

    result = await flow.async_step_user(user_input)

    assert result["type"] == "create_entry"
    assert result["title"] == "test@example.com"
    assert result["data"][CONF_USERNAME] == "test@example.com"
    assert result["data"][CONF_PASSWORD] == "secret"
