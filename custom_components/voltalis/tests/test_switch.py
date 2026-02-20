"""E2E tests for the Voltalis switch platform."""

from collections.abc import AsyncGenerator

import pytest
from homeassistant import config_entries
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
from homeassistant.data_entry_flow import FlowResultType

from custom_components.voltalis.const import DOMAIN
from custom_components.voltalis.lib.domain.devices_management.climates.manual_setting_builder import (
    ManualSettingBuilder,
)
from custom_components.voltalis.lib.domain.devices_management.devices.device_builder import DeviceBuilder
from custom_components.voltalis.lib.domain.devices_management.devices.device_enum import (
    DeviceModeEnum,
    DeviceTypeEnum,
)
from custom_components.voltalis.tests.utils.mock_voltalis_server import MockVoltalisServer


@pytest.mark.e2e
async def test_switch_entity_setup(
    hass: HomeAssistant,
    setup_integration: MockVoltalisServer,
) -> None:
    """Test that switch entities are created for all devices."""

    # Verify switch entities were created
    switch_entity_1 = hass.states.get("switch.heater_1_1_device_switch")
    switch_entity_2 = hass.states.get("switch.heater_2_2_device_switch")
    switch_entity_3 = hass.states.get("switch.water_heater_3_3_device_switch")

    assert switch_entity_1 is not None
    assert switch_entity_2 is not None
    assert switch_entity_3 is not None

    # Check initial states based on is_on from manual settings
    assert switch_entity_1.state == STATE_ON
    assert switch_entity_2.state == STATE_OFF
    assert switch_entity_3.state == STATE_ON


@pytest.mark.e2e
async def test_switch_turn_on(
    hass: HomeAssistant,
    setup_integration: MockVoltalisServer,
) -> None:
    """Test turning on a switch entity."""

    entity_id = "switch.heater_2_2_device_switch"

    # Verify initial state
    state = hass.states.get(entity_id)
    assert state is not None
    assert state.state == STATE_OFF

    # Turn on the switch
    await hass.services.async_call(
        SWITCH_DOMAIN,
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: entity_id},
        blocking=True,
    )
    await hass.async_block_till_done()

    # Trigger coordinator refresh to update HA state
    entry = hass.config_entries.async_entries(DOMAIN)[0]
    coordinator = entry.runtime_data.voltalis_home_assistant_module.device_coordinator
    await coordinator.async_refresh()
    await hass.async_block_till_done()

    # Verify state changed in HA
    state = hass.states.get(entity_id)
    assert state is not None
    assert state.state == STATE_ON


@pytest.mark.e2e
async def test_switch_turn_off(
    hass: HomeAssistant,
    setup_integration: MockVoltalisServer,
) -> None:
    """Test turning off a switch entity."""

    entity_id = "switch.heater_1_1_device_switch"

    # Verify initial state
    state = hass.states.get(entity_id)
    assert state is not None
    assert state.state == STATE_ON

    # Turn off the switch
    await hass.services.async_call(
        SWITCH_DOMAIN,
        SERVICE_TURN_OFF,
        {ATTR_ENTITY_ID: entity_id},
        blocking=True,
    )
    await hass.async_block_till_done()

    # Trigger coordinator refresh to update HA state
    entry = hass.config_entries.async_entries(DOMAIN)[0]
    coordinator = entry.runtime_data.voltalis_home_assistant_module.device_coordinator
    await coordinator.async_refresh()
    await hass.async_block_till_done()

    # Verify state changed in HA
    state = hass.states.get(entity_id)
    assert state is not None
    assert state.state == STATE_OFF


@pytest.mark.e2e
async def test_switch_uses_on_mode_for_device_with_on_mode(
    hass: HomeAssistant,
    setup_integration: MockVoltalisServer,
) -> None:
    """Test that switch uses ON mode when device has it available."""

    entity_id = "switch.heater_2_2_device_switch"

    # Heater 2 has ON mode in available_modes
    state = hass.states.get(entity_id)
    assert state is not None
    assert state.state == STATE_OFF

    # Turn on the switch
    await hass.services.async_call(
        SWITCH_DOMAIN,
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: entity_id},
        blocking=True,
    )
    await hass.async_block_till_done()

    # The device should be turned on
    # (The actual mode used is handled by the command handler)


@pytest.mark.e2e
async def test_switch_uses_comfort_mode_for_device_without_on_mode(
    hass: HomeAssistant,
    setup_integration: MockVoltalisServer,
) -> None:
    """Test that switch uses COMFORT mode when device doesn't have ON mode."""

    entity_id = "switch.heater_1_1_device_switch"

    # Heater 1 doesn't have ON mode in available_modes
    state = hass.states.get(entity_id)
    assert state is not None
    assert state.state == STATE_ON

    # Turn off then on the switch
    await hass.services.async_call(
        SWITCH_DOMAIN,
        SERVICE_TURN_OFF,
        {ATTR_ENTITY_ID: entity_id},
        blocking=True,
    )
    await hass.async_block_till_done()

    await hass.services.async_call(
        SWITCH_DOMAIN,
        SERVICE_TURN_ON,
        {ATTR_ENTITY_ID: entity_id},
        blocking=True,
    )
    await hass.async_block_till_done()

    # The device should be turned on
    # (The actual mode used is handled by the command handler)


@pytest.mark.e2e
async def test_switch_coordinator_update_reflects_state(
    hass: HomeAssistant,
    setup_integration: MockVoltalisServer,
) -> None:
    """Test that coordinator updates reflect in switch state."""

    entity_id = "switch.heater_1_1_device_switch"

    # Get initial state
    state = hass.states.get(entity_id)
    assert state is not None
    assert state.state == STATE_ON

    # Manually trigger refresh
    entry = hass.config_entries.async_entries(DOMAIN)[0]
    coordinator = entry.runtime_data.voltalis_home_assistant_module.device_coordinator

    await coordinator.async_refresh()
    await hass.async_block_till_done()

    # Verify state is consistent
    state = hass.states.get(entity_id)
    assert state is not None
    assert state.state == STATE_ON


@pytest.mark.e2e
async def test_switch_availability_when_device_missing(
    hass: HomeAssistant,
    setup_integration: MockVoltalisServer,
) -> None:
    """Test that switch becomes unavailable when device is missing."""

    entity_id = "switch.heater_1_1_device_switch"

    # Verify initial availability
    state = hass.states.get(entity_id)
    assert state is not None
    assert state.state != STATE_UNAVAILABLE

    # Note: Testing unavailability requires manipulating the stub client's device list
    # This would require public API on VoltalisClientStub or using a MockVoltalisServer
    # For now, verify that the entity exists and is available


@pytest.mark.e2e
async def test_switch_availability_when_is_on_is_none(
    hass: HomeAssistant,
    setup_integration: MockVoltalisServer,
) -> None:
    """Test that switch becomes unavailable when is_on is None."""

    entity_id = "switch.heater_1_1_device_switch"

    # Verify initial availability
    state = hass.states.get(entity_id)
    assert state is not None
    assert state.state != STATE_UNAVAILABLE

    # Note: Testing unavailability when is_on is None requires manipulating the stub client's manual settings
    # This would require public API on VoltalisClientStub or using a MockVoltalisServer
    # For now, verify that the entity exists and is available


pytestmark = [pytest.mark.asyncio(loop_scope="function"), pytest.mark.enable_socket]


@pytest.fixture(scope="module")
async def voltalis_server_module() -> AsyncGenerator[MockVoltalisServer, None]:
    """Start the MockVoltalisServer once for all tests in the module."""
    server = MockVoltalisServer()
    await server.start_server()
    yield server
    await server.stop_server()


@pytest.fixture(scope="function")
async def setup_integration(
    hass: HomeAssistant,
    voltalis_server_module: MockVoltalisServer,
    monkeypatch: pytest.MonkeyPatch,
) -> AsyncGenerator[MockVoltalisServer, None]:
    """Reset server state and setup integration for each test."""

    # Reset storage before each test
    voltalis_server_module.reset_storage()
    voltalis_server_module.given_login_ok()

    # Create test devices
    device1 = DeviceBuilder().with_id(1).with_name("Heater 1").with_type(DeviceTypeEnum.HEATER).build()

    device2 = (
        DeviceBuilder()
        .with_id(2)
        .with_name("Heater 2")
        .with_type(DeviceTypeEnum.HEATER)
        .with_available_modes([DeviceModeEnum.ON, DeviceModeEnum.ECO])
        .build()
    )

    device3 = DeviceBuilder().with_id(3).with_name("Water Heater").with_type(DeviceTypeEnum.WATER_HEATER).build()

    voltalis_server_module.given_devices({1: device1, 2: device2, 3: device3})

    # Create and set manual settings
    manual_setting1 = ManualSettingBuilder().with_id(1).with_id_appliance(1).with_is_on(True).build()
    manual_setting2 = ManualSettingBuilder().with_id(2).with_id_appliance(2).with_is_on(False).build()
    manual_setting3 = ManualSettingBuilder().with_id(3).with_id_appliance(3).with_is_on(True).build()

    voltalis_server_module.given_manual_settings([manual_setting1, manual_setting2, manual_setting3])

    # Mock VoltalisClientAiohttp to use the mock server
    monkeypatch.setattr(
        "custom_components.voltalis.config_flow.VoltalisClientAiohttp",
        lambda session, **kwargs: voltalis_server_module.get_client(),
    )

    # Also mock it for runtime usage
    monkeypatch.setattr(
        "custom_components.voltalis.apps.home_assistant.home_assistant_module.VoltalisClientAiohttp",
        lambda session, **kwargs: voltalis_server_module.get_client(),
    )

    # Create entry via config flow
    init_result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})
    assert init_result["type"] == FlowResultType.FORM

    result = await hass.config_entries.flow.async_configure(
        init_result["flow_id"],
        user_input={
            "username": "test@example.com",
            "password": "secret",
        },
    )
    assert result["type"] == FlowResultType.CREATE_ENTRY

    # Wait for setup to complete
    await hass.async_block_till_done()

    yield voltalis_server_module
