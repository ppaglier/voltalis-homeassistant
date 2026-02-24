"""Unit tests for EnergyContractBuilder."""

from datetime import date

import pytest

from custom_components.voltalis.lib.domain.energy_contracts.energy_contract_builder import EnergyContractBuilder
from custom_components.voltalis.lib.domain.energy_contracts.energy_contract_enum import EnergyContractTypeEnum


@pytest.mark.unit
def test_energy_contract_builder_default_values() -> None:
    """Test that EnergyContractBuilder creates a contract with default values."""

    assert EnergyContractBuilder().build() == EnergyContractBuilder.DEFAULT_VALUES


@pytest.mark.unit
def test_energy_contract_builder_creates_valid_contract() -> None:
    """Test that EnergyContractBuilder creates a valid energy contract."""

    # Act
    contract = EnergyContractBuilder().with_id(1).with_contract_id(100).with_type(EnergyContractTypeEnum.BASE).build()

    # Assert
    assert contract.id == 1
    assert contract.contract_id == 100
    assert contract.type == EnergyContractTypeEnum.BASE


@pytest.mark.unit
def test_energy_contract_builder_with_all_fields() -> None:
    """Test EnergyContractBuilder with all optional fields."""

    # Act
    end_date = date(2025, 12, 31)
    contract = (
        EnergyContractBuilder()
        .with_id(2)
        .with_contract_id(200)
        .with_type(EnergyContractTypeEnum.PEAK_OFFPEAK)
        .with_end_date(end_date)
        .build()
    )

    # Assert
    assert contract.id == 2
    assert contract.end_date == end_date
    assert contract.type == EnergyContractTypeEnum.PEAK_OFFPEAK
