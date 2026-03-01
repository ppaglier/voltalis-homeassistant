"""Unit tests for ManualSettingBuilder."""

from datetime import datetime

import pytest

from custom_components.voltalis.lib.domain.devices_management.climates.manual_setting_builder import (
    ManualSettingBuilder,
)
from custom_components.voltalis.lib.domain.devices_management.devices.device_enum import DeviceModeEnum


@pytest.mark.unit
def test_manual_setting_builder_default_values() -> None:
    """Test that ManualSettingBuilder creates a setting with default values."""

    assert ManualSettingBuilder().build() == ManualSettingBuilder.DEFAULT_VALUES


@pytest.mark.unit
def test_manual_setting_builder_creates_valid_setting() -> None:
    """Test that ManualSettingBuilder creates a valid manual setting."""

    # Act
    setting = (
        ManualSettingBuilder()
        .with_id(1)
        .with_enabled(True)
        .with_id_appliance(5)
        .with_until_further_notice(True)
        .with_is_on(True)
        .with_mode(DeviceModeEnum.COMFORT)
        .with_temperature_target(20.0)
        .build()
    )

    # Assert
    assert setting.id == 1
    assert setting.enabled is True
    assert setting.id_appliance == 5
    assert setting.until_further_notice is True
    assert setting.is_on is True
    assert setting.mode == DeviceModeEnum.COMFORT
    assert setting.temperature_target == 20.0


@pytest.mark.unit
def test_manual_setting_builder_with_end_date() -> None:
    """Test ManualSettingBuilder with an end date."""

    # Act
    end_date = datetime(2025, 3, 15, 18, 30)
    setting = (
        ManualSettingBuilder()
        .with_id(2)
        .with_enabled(True)
        .with_id_appliance(3)
        .with_until_further_notice(False)
        .with_end_date(end_date)
        .build()
    )

    # Assert
    assert setting.until_further_notice is False
    assert setting.end_date == end_date


@pytest.mark.unit
def test_manual_setting_builder_with_temperature_modes() -> None:
    """Test ManualSettingBuilder with different modes."""

    # Test ECO mode
    setting = ManualSettingBuilder().with_id(3).with_mode(DeviceModeEnum.ECO).build()
    assert setting.mode == DeviceModeEnum.ECO

    # Test TEMPERATURE mode
    setting = ManualSettingBuilder().with_id(4).with_mode(DeviceModeEnum.TEMPERATURE).build()
    assert setting.mode == DeviceModeEnum.TEMPERATURE


@pytest.mark.unit
def test_manual_setting_builder_temperature_target_precision() -> None:
    """Test ManualSettingBuilder preserves temperature precision."""

    # Act
    setting = ManualSettingBuilder().with_id(5).with_temperature_target(19.5).build()

    # Assert
    assert setting.temperature_target == 19.5
