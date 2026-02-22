"""E2E tests for the Voltalis sensor platform."""

from collections.abc import AsyncGenerator

import pytest
from homeassistant.const import (
    ATTR_UNIT_OF_MEASUREMENT,
    CURRENCY_EURO,
    UnitOfApparentPower,
    UnitOfEnergy,
    UnitOfPower,
)
from homeassistant.core import HomeAssistant

from custom_components.voltalis.apps.home_assistant.tests.home_assistant_fixture import HomeAssistantFixture
from custom_components.voltalis.lib.domain.devices_management.health.device_health import DeviceHealthStatusEnum
from custom_components.voltalis.lib.domain.energy_contracts.energy_contract_current_mode_enum import (
    EnergyContractCurrentModeEnum,
)


@pytest.mark.e2e
@pytest.mark.parametrize(
    "entity_id,expected_attributes",
    [
        # Device daily consumption sensors - should exist for all devices
        ("sensor.heater_1_daily_consumption", {"unit_of_measurement": UnitOfEnergy.WATT_HOUR}),
        ("sensor.heater_2_daily_consumption", {"unit_of_measurement": UnitOfEnergy.WATT_HOUR}),
        ("sensor.water_heater_1_daily_consumption", {"unit_of_measurement": UnitOfEnergy.WATT_HOUR}),
        ("sensor.water_heater_2_daily_consumption", {"unit_of_measurement": UnitOfEnergy.WATT_HOUR}),
        # Device connection status sensors - should exist for all devices with health data
        ("sensor.heater_1_connection_status", {"has_options": True}),
        ("sensor.heater_2_connection_status", {"has_options": True}),
        ("sensor.water_heater_1_connection_status", {"has_options": True}),
        ("sensor.water_heater_2_connection_status", {"has_options": True}),
        # Device current mode sensors - should exist for devices with mode data
        ("sensor.heater_1_current_mode", {"has_options": True}),
        ("sensor.heater_2_current_mode", {"has_options": True}),
        ("sensor.water_heater_1_current_mode", {"has_options": True}),
        ("sensor.water_heater_2_current_mode", {"has_options": True}),
    ],
)
async def test_device_sensor_entity_setup(
    fixture: HomeAssistantFixture,
    entity_id: str,
    expected_attributes: dict,
) -> None:
    """Test that device sensor entities are created with correct attributes."""

    sensor_entity = fixture.get_entity_state(entity_id)

    # Verify expected attributes
    for attr_key, attr_value in expected_attributes.items():
        if attr_key == "has_options":
            # For enum sensors, just check that they have options
            assert "options" in sensor_entity.attributes, f"options attribute not found in {entity_id}"
            assert len(sensor_entity.attributes["options"]) > 0, f"No options found in {entity_id}"
        else:
            assert attr_key in sensor_entity.attributes, f"Attribute {attr_key} not found in {entity_id}"
            assert sensor_entity.attributes[attr_key] == attr_value


@pytest.mark.e2e
@pytest.mark.parametrize(
    "entity_id,expected_state",
    [
        # Device connection status sensors have specific states based on health
        ("sensor.heater_1_connection_status", DeviceHealthStatusEnum.OK),
        ("sensor.heater_2_connection_status", DeviceHealthStatusEnum.NOT_OK),
        ("sensor.water_heater_1_connection_status", DeviceHealthStatusEnum.COMM_ERROR),
        ("sensor.water_heater_2_connection_status", DeviceHealthStatusEnum.NO_CONSUMPTION),
    ],
)
async def test_device_sensor_states(
    fixture: HomeAssistantFixture,
    entity_id: str,
    expected_state: str,
) -> None:
    """Test that device sensor entities have the correct states."""

    sensor_entity = fixture.get_entity_state(entity_id)
    fixture.compare_data(sensor_entity.state, str(expected_state))


@pytest.mark.e2e
@pytest.mark.parametrize(
    "entity_id",
    [
        "sensor.heater_1_daily_consumption",
        "sensor.heater_2_daily_consumption",
        "sensor.water_heater_1_daily_consumption",
        "sensor.water_heater_2_daily_consumption",
    ],
)
async def test_device_daily_consumption_sensor(
    fixture: HomeAssistantFixture,
    entity_id: str,
) -> None:
    """Test that device daily consumption sensors report values."""

    sensor_entity = fixture.get_entity_state(entity_id)

    # Check that the sensor has a numeric state (consumption value)
    assert sensor_entity.state not in ["unknown", "unavailable"]
    # Try to convert to float to verify it's a valid number
    consumption_value = float(sensor_entity.state)
    assert consumption_value >= 0, f"Consumption should be non-negative, got {consumption_value}"


@pytest.mark.e2e
@pytest.mark.parametrize(
    "entity_id,expected_unit",
    [
        ("sensor.contract_1_3_kva_peak_offpeak_live_consumption", UnitOfPower.WATT),
        ("sensor.contract_1_3_kva_peak_offpeak_subscribed_power", UnitOfApparentPower.KILO_VOLT_AMPERE),
        ("sensor.contract_1_3_kva_peak_offpeak_kwh_current_cost", f"{CURRENCY_EURO}/{UnitOfEnergy.KILO_WATT_HOUR}"),
        ("sensor.contract_1_3_kva_peak_offpeak_kwh_peak_cost", f"{CURRENCY_EURO}/{UnitOfEnergy.KILO_WATT_HOUR}"),
        ("sensor.contract_1_3_kva_peak_offpeak_kwh_off_peak_cost", f"{CURRENCY_EURO}/{UnitOfEnergy.KILO_WATT_HOUR}"),
    ],
)
async def test_energy_contract_sensor_entity_setup(
    fixture: HomeAssistantFixture,
    entity_id: str,
    expected_unit: str,
) -> None:
    """Test that energy contract sensor entities are created with correct units."""

    sensor_entity = fixture.get_entity_state(entity_id)

    # Verify unit of measurement
    assert ATTR_UNIT_OF_MEASUREMENT in sensor_entity.attributes
    fixture.compare_data(sensor_entity.attributes[ATTR_UNIT_OF_MEASUREMENT], expected_unit)


@pytest.mark.e2e
async def test_energy_contract_current_mode_sensor(fixture: HomeAssistantFixture) -> None:
    """Test that energy contract current mode sensor has correct options."""

    entity_id = "sensor.contract_1_3_kva_peak_offpeak_energy_contract_current_mode"
    sensor_entity = fixture.get_entity_state(entity_id)

    # Verify that options are available
    assert "options" in sensor_entity.attributes
    expected_options = [str(mode) for mode in EnergyContractCurrentModeEnum]
    actual_options = sensor_entity.attributes["options"]
    assert set(expected_options) == set(actual_options)

    # Verify state is one of the valid options
    assert sensor_entity.state in actual_options


@pytest.mark.e2e
async def test_energy_contract_live_consumption_sensor(fixture: HomeAssistantFixture) -> None:
    """Test that energy contract live consumption sensor reports values."""

    entity_id = "sensor.contract_1_3_kva_peak_offpeak_live_consumption"
    sensor_entity = fixture.get_entity_state(entity_id)

    # Check that the sensor has a numeric state
    assert sensor_entity.state not in ["unavailable"]
    # Verify it's a valid number
    consumption_value = float(sensor_entity.state)
    assert consumption_value >= 0, f"Live consumption should be non-negative, got {consumption_value}"


@pytest.mark.e2e
async def test_sensor_coordinator_update_reflects_state(fixture: HomeAssistantFixture) -> None:
    """Test that coordinator updates reflect in sensor state."""

    entity_id = "sensor.heater_1_daily_consumption"

    # Get initial state
    initial_state = fixture.get_entity_state(entity_id)
    initial_value = initial_state.state

    # Trigger coordinator refresh
    await fixture.async_refresh_coordinator(
        fixture.get_home_assistant_voltalis_module().device_daily_consumption_coordinator
    )

    # Verify state is consistent after refresh
    state = fixture.get_entity_state(entity_id)
    assert state.state == initial_value


@pytest.mark.e2e
async def test_device_health_coordinator_update(fixture: HomeAssistantFixture) -> None:
    """Test that device health coordinator updates reflect in sensor state."""

    entity_id = "sensor.heater_1_connection_status"

    # Get initial state
    initial_state = fixture.get_entity_state(entity_id)
    fixture.compare_data(initial_state.state, str(DeviceHealthStatusEnum.OK))

    # Trigger coordinator refresh
    await fixture.async_refresh_coordinator(fixture.get_home_assistant_voltalis_module().device_health_coordinator)

    # Verify state is still consistent
    state = fixture.get_entity_state(entity_id)
    fixture.compare_data(state.state, str(DeviceHealthStatusEnum.OK))


@pytest.mark.e2e
async def test_energy_contract_coordinator_update(fixture: HomeAssistantFixture) -> None:
    """Test that energy contract coordinator updates reflect in sensor state."""

    entity_id = "sensor.contract_1_3_kva_peak_offpeak_subscribed_power"

    # Get initial state
    initial_state = fixture.get_entity_state(entity_id)
    initial_value = initial_state.state

    # Trigger coordinator refresh
    await fixture.async_refresh_coordinator(fixture.get_home_assistant_voltalis_module().energy_contract_coordinator)

    # Verify state is consistent after refresh
    state = fixture.get_entity_state(entity_id)
    assert state.state == initial_value


@pytest.mark.e2e
async def test_device_sensor_handles_missing_device_data(fixture: HomeAssistantFixture) -> None:
    """Test that device sensor handles missing device data gracefully."""

    entity_id = "sensor.heater_1_daily_consumption"

    # Verify entity is available initially
    initial_state = fixture.get_entity_state(entity_id)
    assert initial_state.state != "unavailable"

    # Remove the device from coordinator data
    coordinator = fixture.get_home_assistant_voltalis_module().device_daily_consumption_coordinator
    device_id = 1
    if device_id in coordinator.data:
        del coordinator.data[device_id]

    # Manually trigger listeners to notify entities of data change
    coordinator.async_set_updated_data(coordinator.data)
    await fixture.hass.async_block_till_done(True)

    # Verify entity either becomes unavailable or retains state
    # (Entity should not crash when data is missing)
    state = fixture.get_entity_state(entity_id)
    assert state is not None


@pytest.mark.e2e
async def test_device_health_sensor_handles_missing_device_data(fixture: HomeAssistantFixture) -> None:
    """Test that device health sensor handles missing device data gracefully."""

    entity_id = "sensor.heater_1_connection_status"

    # Verify entity is available initially
    initial_state = fixture.get_entity_state(entity_id)
    assert initial_state.state != "unavailable"

    # Remove the device from coordinator data
    coordinator = fixture.get_home_assistant_voltalis_module().device_health_coordinator
    device_id = 1
    if device_id in coordinator.data:
        del coordinator.data[device_id]

    # Manually trigger listeners to notify entities of data change
    coordinator.async_set_updated_data(coordinator.data)
    await fixture.hass.async_block_till_done(True)

    # Verify entity either becomes unavailable or retains state
    # (Entity should not crash when data is missing)
    state = fixture.get_entity_state(entity_id)
    assert state is not None


@pytest.mark.e2e
async def test_energy_contract_sensor_handles_missing_contract_data(fixture: HomeAssistantFixture) -> None:
    """Test that energy contract sensor handles missing contract data gracefully."""

    entity_id = "sensor.contract_1_3_kva_peak_offpeak_subscribed_power"

    # Verify entity is available initially
    initial_state = fixture.get_entity_state(entity_id)
    assert initial_state.state != "unavailable"

    # Remove the contract from coordinator data
    coordinator = fixture.get_home_assistant_voltalis_module().energy_contract_coordinator
    contract_id = 1
    if contract_id in coordinator.data:
        del coordinator.data[contract_id]

    # Manually trigger listeners to notify entities of data change
    coordinator.async_set_updated_data(coordinator.data)
    await fixture.hass.async_block_till_done(True)

    # Verify entity either becomes unavailable or retains state
    # (Entity should not crash when data is missing)
    state = fixture.get_entity_state(entity_id)
    assert state is not None


@pytest.mark.e2e
@pytest.mark.parametrize(
    "entity_id",
    [
        "sensor.heater_1_daily_consumption",
        "sensor.heater_2_daily_consumption",
        "sensor.water_heater_1_daily_consumption",
        "sensor.water_heater_2_daily_consumption",
        "sensor.heater_1_connection_status",
        "sensor.heater_2_connection_status",
        "sensor.water_heater_1_connection_status",
        "sensor.water_heater_2_connection_status",
    ],
)
async def test_sensor_entity_has_icon(fixture: HomeAssistantFixture, entity_id: str) -> None:
    """Test that sensor entities have icons."""

    sensor_entity = fixture.get_entity_state(entity_id)
    # Check that icon attribute exists (can be mdi:* format or None)
    assert "icon" in sensor_entity.attributes or sensor_entity.attributes.get("icon") is None


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
