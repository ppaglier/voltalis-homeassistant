"""Tests for the new Voltalis sensors."""

import pytest
from datetime import datetime

from custom_components.voltalis.lib.domain.device import (
    VoltalisConsumptionObjective,
    VoltalisDevice,
    VoltalisDeviceModeEnum,
    VoltalisDeviceModulatorTypeEnum,
    VoltalisDeviceProgTypeEnum,
    VoltalisDeviceTypeEnum,
    VoltalisProgram,
    VoltalisRealTimeConsumption,
)
from custom_components.voltalis.lib.infrastructure.voltalis_client_stub import VoltalisClientStub


@pytest.mark.asyncio
async def test_get_consumption_objective() -> None:
    """Test getting consumption objective."""
    client = VoltalisClientStub()

    # Set up test data
    client._VoltalisClientStub__storage.consumption_objective = VoltalisConsumptionObjective(
        yearly_objective_in_wh=5000.0,
        yearly_objective_in_currency=750.0,
    )

    # Test the method
    objective = await client.get_consumption_objective()
    assert objective is not None
    assert objective.yearly_objective_in_wh == 5000.0
    assert objective.yearly_objective_in_currency == 750.0


@pytest.mark.asyncio
async def test_get_consumption_objective_none() -> None:
    """Test getting consumption objective when it's None."""
    client = VoltalisClientStub()

    # Don't set any data (should be None by default)
    objective = await client.get_consumption_objective()
    assert objective is None


@pytest.mark.asyncio
async def test_get_realtime_consumption() -> None:
    """Test getting real-time consumption."""
    client = VoltalisClientStub()

    # Set up test data
    client._VoltalisClientStub__storage.realtime_consumptions = [
        VoltalisRealTimeConsumption(
            timestamp="2025-01-17T10:00:00Z",
            total_consumption_in_wh=100.0,
            total_consumption_in_currency=15.0,
        ),
        VoltalisRealTimeConsumption(
            timestamp="2025-01-17T10:10:00Z",
            total_consumption_in_wh=110.0,
            total_consumption_in_currency=16.5,
        ),
    ]

    # Test the method
    consumptions = await client.get_realtime_consumption(num_points=10)
    assert len(consumptions) == 2
    assert consumptions[0].total_consumption_in_wh == 100.0
    assert consumptions[1].total_consumption_in_wh == 110.0


@pytest.mark.asyncio
async def test_get_realtime_consumption_limit() -> None:
    """Test getting real-time consumption with limit."""
    client = VoltalisClientStub()

    # Set up test data with more points than we'll request
    client._VoltalisClientStub__storage.realtime_consumptions = [
        VoltalisRealTimeConsumption(
            timestamp=f"2025-01-17T10:{i*10:02d}:00Z",
            total_consumption_in_wh=100.0 + i * 10,
            total_consumption_in_currency=15.0 + i,
        )
        for i in range(15)
    ]

    # Test the method with limit
    consumptions = await client.get_realtime_consumption(num_points=5)
    assert len(consumptions) == 5


@pytest.mark.asyncio
async def test_get_programs() -> None:
    """Test getting programs."""
    client = VoltalisClientStub()

    # Set up test data
    client._VoltalisClientStub__storage.programs = [
        VoltalisProgram(
            id=1,
            name="Eco Program",
            enabled=True,
            program_type=VoltalisDeviceProgTypeEnum.USER,
            program_name="eco",
            until_further_notice=True,
            end_date=None,
            geoloc_currently_on=False,
        ),
        VoltalisProgram(
            id=2,
            name="Default Program",
            enabled=False,
            program_type=VoltalisDeviceProgTypeEnum.DEFAULT,
            program_name="default",
            until_further_notice=True,
            end_date=None,
            geoloc_currently_on=False,
        ),
    ]

    # Test the method
    programs = await client.get_programs()
    assert len(programs) == 2
    assert programs[0].name == "Eco Program"
    assert programs[0].enabled is True
    assert programs[1].name == "Default Program"
    assert programs[1].enabled is False


@pytest.mark.asyncio
async def test_get_programs_empty() -> None:
    """Test getting programs when there are none."""
    client = VoltalisClientStub()

    # Don't set any data (should be empty list by default)
    programs = await client.get_programs()
    assert len(programs) == 0
