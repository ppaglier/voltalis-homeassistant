"""E2E tests for the Voltalis climate platform."""

from collections.abc import AsyncGenerator

import pytest
from homeassistant.components.climate import (
    ATTR_HVAC_MODE,
    ATTR_PRESET_MODE,
    SERVICE_SET_HVAC_MODE,
    SERVICE_SET_PRESET_MODE,
)
from homeassistant.components.climate import DOMAIN as CLIMATE_DOMAIN
from homeassistant.components.climate.const import HVACMode
from homeassistant.const import SERVICE_TURN_OFF, SERVICE_TURN_ON
from homeassistant.core import HomeAssistant

from custom_components.voltalis.apps.home_assistant.tests.home_assistant_fixture import HomeAssistantFixture
from custom_components.voltalis.lib.domain.devices_management.presets.preset_enum import DeviceCurrentPresetEnum


@pytest.mark.e2e
@pytest.mark.parametrize(
    "entity_id,expected_hvac_mode",
    [
        ("climate.heater_1", HVACMode.HEAT),
        ("climate.heater_2", HVACMode.OFF),
    ],
)
async def test_climate_entity_setup(
    fixture: HomeAssistantFixture,
    entity_id: str,
    expected_hvac_mode: HVACMode,
) -> None:
    """Test that climate entities are created for heater devices."""

    climate_entity = fixture.get_entity_state(entity_id)
    fixture.compare_data(climate_entity.state, expected_hvac_mode.value)


@pytest.mark.e2e
@pytest.mark.parametrize(
    "entity_id",
    [
        "climate.heater_1",
        "climate.heater_2",
    ],
)
async def test_climate_entity_has_hvac_modes(
    fixture: HomeAssistantFixture,
    entity_id: str,
) -> None:
    """Test that climate entities have HVAC modes."""

    climate_entity = fixture.get_entity_state(entity_id)
    assert "hvac_modes" in climate_entity.attributes
    hvac_modes = climate_entity.attributes["hvac_modes"]
    assert HVACMode.OFF in hvac_modes
    assert HVACMode.HEAT in hvac_modes
    assert HVACMode.AUTO in hvac_modes


@pytest.mark.e2e
@pytest.mark.parametrize(
    "entity_id",
    [
        "climate.heater_1",
        "climate.heater_2",
    ],
)
async def test_climate_entity_has_preset_modes(
    fixture: HomeAssistantFixture,
    entity_id: str,
) -> None:
    """Test that climate entities have preset modes."""

    climate_entity = fixture.get_entity_state(entity_id)
    assert "preset_modes" in climate_entity.attributes
    preset_modes = climate_entity.attributes["preset_modes"]
    assert len(preset_modes) > 0


@pytest.mark.e2e
@pytest.mark.parametrize(
    "entity_id,hvac_mode,expected_state",
    [
        ("climate.heater_1", HVACMode.OFF, HVACMode.OFF),
        ("climate.heater_1", HVACMode.HEAT, HVACMode.HEAT),
        ("climate.heater_2", HVACMode.HEAT, HVACMode.HEAT),
        ("climate.heater_2", HVACMode.OFF, HVACMode.OFF),
    ],
)
async def test_climate_set_hvac_mode(
    fixture: HomeAssistantFixture,
    entity_id: str,
    hvac_mode: HVACMode,
    expected_state: HVACMode,
) -> None:
    """Test setting HVAC mode for climate entities."""

    # Set HVAC mode
    await fixture.async_call_service(CLIMATE_DOMAIN, SERVICE_SET_HVAC_MODE, entity_id, {ATTR_HVAC_MODE: hvac_mode})

    # Trigger coordinator refresh to update HA state
    await fixture.async_refresh_coordinator(fixture.get_home_assistant_voltalis_module().device_coordinator)

    # Verify state changed
    state = fixture.get_entity_state(entity_id)
    fixture.compare_data(state.state, expected_state.value)


@pytest.mark.e2e
@pytest.mark.parametrize(
    "entity_id,service,expected_state",
    [
        ("climate.heater_1", SERVICE_TURN_OFF, HVACMode.OFF),
        ("climate.heater_2", SERVICE_TURN_ON, HVACMode.HEAT),
    ],
)
async def test_climate_turn_on_off(
    fixture: HomeAssistantFixture,
    entity_id: str,
    service: str,
    expected_state: HVACMode,
) -> None:
    """Test turning on/off climate entities."""

    # Turn on/off the climate entity
    await fixture.async_call_service(CLIMATE_DOMAIN, service, entity_id)

    # Trigger coordinator refresh to update HA state
    await fixture.async_refresh_coordinator(fixture.get_home_assistant_voltalis_module().device_coordinator)

    # Verify state changed
    state = fixture.get_entity_state(entity_id)
    fixture.compare_data(state.state, expected_state.value)


@pytest.mark.e2e
@pytest.mark.parametrize(
    "entity_id,preset_mode",
    [
        ("climate.heater_1", DeviceCurrentPresetEnum.ECO.value),
        ("climate.heater_1", DeviceCurrentPresetEnum.COMFORT.value),
    ],
)
async def test_climate_set_preset_mode(
    fixture: HomeAssistantFixture,
    entity_id: str,
    preset_mode: str,
) -> None:
    """Test setting preset mode for climate entities."""

    # Set preset mode
    await fixture.async_call_service(
        CLIMATE_DOMAIN, SERVICE_SET_PRESET_MODE, entity_id, {ATTR_PRESET_MODE: preset_mode}
    )

    # Trigger coordinator refresh to update HA state
    await fixture.async_refresh_coordinator(fixture.get_home_assistant_voltalis_module().device_coordinator)

    # Verify preset mode changed
    state = fixture.get_entity_state(entity_id)
    assert "preset_mode" in state.attributes
    fixture.compare_data(state.attributes["preset_mode"], preset_mode)


@pytest.mark.e2e
async def test_climate_temperature_attributes(fixture: HomeAssistantFixture) -> None:
    """Test that climate entities have temperature attributes."""

    entity_id = "climate.heater_1"
    climate_entity = fixture.get_entity_state(entity_id)

    # Check for temperature-related attributes
    assert "current_temperature" in climate_entity.attributes
    assert "min_temp" in climate_entity.attributes
    assert "max_temp" in climate_entity.attributes
    assert "target_temp_step" in climate_entity.attributes

    # Verify min/max are reasonable
    min_temp = climate_entity.attributes["min_temp"]
    max_temp = climate_entity.attributes["max_temp"]
    assert min_temp < max_temp


@pytest.mark.e2e
async def test_climate_coordinator_update_reflects_state(fixture: HomeAssistantFixture) -> None:
    """Test that coordinator updates reflect in climate state."""

    entity_id = "climate.heater_1"

    # Get initial state
    initial_state = fixture.get_entity_state(entity_id)
    initial_hvac_mode = initial_state.state

    # Trigger coordinator refresh
    await fixture.async_refresh_coordinator(fixture.get_home_assistant_voltalis_module().device_coordinator)

    # Verify state is still consistent
    state = fixture.get_entity_state(entity_id)
    fixture.compare_data(state.state, initial_hvac_mode)


@pytest.mark.e2e
async def test_climate_has_hvac_action(fixture: HomeAssistantFixture) -> None:
    """Test that climate entities have hvac_action attribute."""

    entity_id = "climate.heater_1"
    climate_entity = fixture.get_entity_state(entity_id)

    # Check for hvac_action attribute
    assert "hvac_action" in climate_entity.attributes
    # The action should be one of the valid HVAC actions
    hvac_action = climate_entity.attributes["hvac_action"]
    assert hvac_action in ["off", "heating", "idle"]


@pytest.mark.e2e
async def test_climate_supported_features(fixture: HomeAssistantFixture) -> None:
    """Test that climate entities have supported features."""

    entity_id = "climate.heater_1"
    climate_entity = fixture.get_entity_state(entity_id)

    # Check for supported_features attribute
    assert "supported_features" in climate_entity.attributes
    supported_features = climate_entity.attributes["supported_features"]
    assert supported_features > 0  # Should have at least some features


@pytest.mark.e2e
@pytest.mark.parametrize(
    "entity_id,hvac_mode_sequence",
    [
        ("climate.heater_1", [HVACMode.OFF, HVACMode.HEAT, HVACMode.AUTO]),
        ("climate.heater_2", [HVACMode.HEAT, HVACMode.OFF, HVACMode.AUTO]),
    ],
)
async def test_climate_hvac_mode_transitions(
    fixture: HomeAssistantFixture,
    entity_id: str,
    hvac_mode_sequence: list[HVACMode],
) -> None:
    """Test transitioning between different HVAC modes."""

    for hvac_mode in hvac_mode_sequence:
        # Set HVAC mode
        await fixture.async_call_service(CLIMATE_DOMAIN, SERVICE_SET_HVAC_MODE, entity_id, {ATTR_HVAC_MODE: hvac_mode})

        # Trigger coordinator refresh
        await fixture.async_refresh_coordinator(fixture.get_home_assistant_voltalis_module().device_coordinator)

        # Verify state changed
        state = fixture.get_entity_state(entity_id)
        fixture.compare_data(state.state, hvac_mode.value)


# We can't use the module-level because of the hass fixture scope
pytestmark = [pytest.mark.asyncio(loop_scope="function"), pytest.mark.enable_socket]


# We can't use the module-level because of the hass fixture scope
@pytest.fixture(scope="function")
async def fixture_all() -> AsyncGenerator[HomeAssistantFixture, None]:
    """
    Before all tests, start the server.
    Then after all tests, stop the server.
    """
    fixture = HomeAssistantFixture()
    await fixture.async_before_all()
    yield fixture
    await fixture.async_after_all()


@pytest.fixture(scope="function")
async def fixture(
    fixture_all: HomeAssistantFixture,
    hass: HomeAssistant,
    monkeypatch: pytest.MonkeyPatch,
) -> AsyncGenerator[HomeAssistantFixture, None]:
    """Before each test, initialize the collection."""
    await fixture_all.async_before_each()
    fixture_all.setup_before_test(hass=hass, monkeypatch=monkeypatch)
    fixture_all.init_provider_with_data()
    await fixture_all.configure_entry()
    yield fixture_all
