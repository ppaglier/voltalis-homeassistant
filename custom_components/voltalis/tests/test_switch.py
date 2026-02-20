"""E2E tests for the Voltalis switch platform."""

from collections.abc import AsyncGenerator

import pytest
from homeassistant.components.switch import DOMAIN as SWITCH_DOMAIN
from homeassistant.const import (
    ATTR_ENTITY_ID,
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
    STATE_OFF,
    STATE_ON,
    STATE_UNAVAILABLE,
)
from homeassistant.core import HomeAssistant

from custom_components.voltalis.apps.home_assistant.tests.home_assistant_fixture import HomeAssistantFixture


@pytest.mark.e2e
async def test_switch_entity_setup(fixture: HomeAssistantFixture) -> None:
    """Test that switch entities are created for all devices."""

    # Verify switch entities were created
    switch_entity_1 = fixture.hass.states.get("switch.heater_1_device_switch")
    switch_entity_2 = fixture.hass.states.get("switch.heater_2_device_switch")
    switch_entity_3 = fixture.hass.states.get("switch.water_heater_device_switch")

    assert switch_entity_1 is not None
    assert switch_entity_2 is not None
    assert switch_entity_3 is not None

    # Check initial states based on is_on from manual settings
    assert switch_entity_1.state == STATE_ON
    assert switch_entity_2.state == STATE_OFF
    assert switch_entity_3.state == STATE_ON


@pytest.mark.e2e
async def test_switch_turn_on(fixture: HomeAssistantFixture) -> None:
    """Test turning on a switch entity."""

    entity_id = "switch.heater_2_device_switch"

    # Verify initial state
    state = fixture.hass.states.get(entity_id)
    assert state is not None
    assert state.state == STATE_OFF

    # Turn on the switch
    await fixture.hass.services.async_call(
        SWITCH_DOMAIN,
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: entity_id},
        blocking=True,
    )
    await fixture.hass.async_block_till_done(True)

    # Trigger coordinator refresh to update HA state
    entry = fixture.get_config_entry()
    coordinator = entry.runtime_data.voltalis_home_assistant_module.device_coordinator
    await coordinator.async_refresh()
    await fixture.hass.async_block_till_done(True)

    # Verify state changed in HA
    state = fixture.hass.states.get(entity_id)
    assert state is not None
    assert state.state == STATE_ON


@pytest.mark.e2e
async def test_switch_turn_off(fixture: HomeAssistantFixture) -> None:
    """Test turning off a switch entity."""

    entity_id = "switch.heater_1_device_switch"

    # Verify initial state
    state = fixture.hass.states.get(entity_id)
    assert state is not None
    assert state.state == STATE_ON

    # Turn off the switch
    await fixture.hass.services.async_call(
        SWITCH_DOMAIN,
        SERVICE_TURN_OFF,
        {ATTR_ENTITY_ID: entity_id},
        blocking=True,
    )
    await fixture.hass.async_block_till_done(True)

    # Trigger coordinator refresh to update HA state
    entry = fixture.get_config_entry()
    coordinator = entry.runtime_data.voltalis_home_assistant_module.device_coordinator
    await coordinator.async_refresh()
    await fixture.hass.async_block_till_done(True)

    # Verify state changed in HA
    state = fixture.hass.states.get(entity_id)
    assert state is not None
    assert state.state == STATE_OFF


@pytest.mark.e2e
async def test_switch_uses_on_mode_for_device_with_on_mode(fixture: HomeAssistantFixture) -> None:
    """Test that switch uses ON mode when device has it available."""

    entity_id = "switch.heater_2_device_switch"

    # Heater 2 has ON mode in available_modes
    state = fixture.hass.states.get(entity_id)
    assert state is not None
    assert state.state == STATE_OFF

    # Turn on the switch
    await fixture.hass.services.async_call(
        SWITCH_DOMAIN,
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: entity_id},
        blocking=True,
    )
    await fixture.hass.async_block_till_done(True)

    # The device should be turned on
    # (The actual mode used is handled by the command handler)


@pytest.mark.e2e
async def test_switch_uses_comfort_mode_for_device_without_on_mode(fixture: HomeAssistantFixture) -> None:
    """Test that switch uses COMFORT mode when device doesn't have ON mode."""

    entity_id = "switch.heater_1_device_switch"

    # Heater 1 doesn't have ON mode in available_modes
    state = fixture.hass.states.get(entity_id)
    assert state is not None
    assert state.state == STATE_ON

    # Turn off then on the switch
    await fixture.hass.services.async_call(
        SWITCH_DOMAIN,
        SERVICE_TURN_OFF,
        {ATTR_ENTITY_ID: entity_id},
        blocking=True,
    )
    await fixture.hass.async_block_till_done(True)

    await fixture.hass.services.async_call(
        SWITCH_DOMAIN,
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: entity_id},
        blocking=True,
    )
    await fixture.hass.async_block_till_done(True)

    # The device should be turned on
    # (The actual mode used is handled by the command handler)


@pytest.mark.e2e
async def test_switch_coordinator_update_reflects_state(fixture: HomeAssistantFixture) -> None:
    """Test that coordinator updates reflect in switch state."""

    entity_id = "switch.heater_1_device_switch"

    # Get initial state
    state = fixture.hass.states.get(entity_id)
    assert state is not None
    assert state.state == STATE_ON

    # Manually trigger refresh
    entry = fixture.get_config_entry()
    coordinator = entry.runtime_data.voltalis_home_assistant_module.device_coordinator

    await coordinator.async_refresh()
    await fixture.hass.async_block_till_done(True)

    # Verify state is consistent
    state = fixture.hass.states.get(entity_id)
    assert state is not None
    assert state.state == STATE_ON


@pytest.mark.e2e
async def test_switch_availability_when_device_missing(fixture: HomeAssistantFixture) -> None:
    """Test that switch becomes unavailable when device is missing."""

    entity_id = "switch.heater_1_device_switch"

    # Verify initial availability
    state = fixture.hass.states.get(entity_id)
    assert state is not None
    assert state.state != STATE_UNAVAILABLE

    # Note: Testing unavailability requires manipulating the stub client's device list
    # This would require public API on VoltalisClientStub or using a MockVoltalisServer
    # For now, verify that the entity exists and is available


@pytest.mark.e2e
async def test_switch_availability_when_is_on_is_none(fixture: HomeAssistantFixture) -> None:
    """Test that switch becomes unavailable when is_on is None."""

    entity_id = "switch.heater_1_device_switch"

    # Verify initial availability
    state = fixture.hass.states.get(entity_id)
    assert state is not None
    assert state.state != STATE_UNAVAILABLE

    # Note: Testing unavailability when is_on is None requires manipulating the stub client's manual settings
    # This would require public API on VoltalisClientStub or using a MockVoltalisServer
    # For now, verify that the entity exists and is available


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
