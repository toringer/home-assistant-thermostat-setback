"""Test the climate setback integration."""

from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.components.climate import HVACMode
from homeassistant.const import ATTR_TEMPERATURE
from homeassistant.core import HomeAssistant

from custom_components.thermostat_setback.climate import ClimateSetbackEntity
from custom_components.thermostat_setback.const import (
    ATTR_IS_SETBACK,
    ATTR_NORMAL_TEMPERATURE,
    ATTR_SETBACK_TEMPERATURE,
    CONF_CLIMATE_DEVICE,
    CONF_SCHEDULE_DEVICE,
)


@pytest.fixture
def mock_config_entry():
    """Mock config entry."""
    from unittest.mock import MagicMock

    config_entry = MagicMock()
    config_entry.entry_id = "test_entry"
    config_entry.data = {
        CONF_CLIMATE_DEVICE: "climate.test_thermostat",
        CONF_SCHEDULE_DEVICE: "schedule.test_schedule"
    }
    return config_entry


@pytest.fixture
def climate_entity(mock_config_entry):
    """Create climate setback entity."""
    return ClimateSetbackEntity(mock_config_entry)


async def test_initial_state(climate_entity):
    """Test initial state of the climate entity."""
    assert climate_entity.name == "Test Thermostat"
    assert climate_entity.unique_id == "thermostat_setback_test_entry"
    assert climate_entity.target_temperature == 22.0
    assert climate_entity.hvac_mode == HVACMode.OFF
    assert not climate_entity.extra_state_attributes[ATTR_IS_SETBACK]


async def test_setback_attributes(climate_entity):
    """Test setback attributes."""
    attributes = climate_entity.extra_state_attributes
    assert attributes[ATTR_SETBACK_TEMPERATURE] == 18.0
    assert attributes[ATTR_NORMAL_TEMPERATURE] == 22.0
    assert not attributes[ATTR_IS_SETBACK]


async def test_manual_setback_control(climate_entity):
    """Test manual setback control methods."""
    # Test setting setback
    await climate_entity.async_set_setback()
    assert climate_entity.extra_state_attributes[ATTR_IS_SETBACK] is True
    assert climate_entity.target_temperature == 18.0

    # Test clearing setback
    await climate_entity.async_clear_setback()
    assert climate_entity.extra_state_attributes[ATTR_IS_SETBACK] is False
    assert climate_entity.target_temperature == 22.0


async def test_temperature_control(climate_entity):
    """Test temperature control."""
    await climate_entity.async_set_temperature(temperature=20.0)
    assert climate_entity.target_temperature == 20.0


async def test_hvac_mode_control(climate_entity):
    """Test HVAC mode control."""
    await climate_entity.async_set_hvac_mode(HVACMode.HEAT)
    assert climate_entity.hvac_mode == HVACMode.HEAT

    await climate_entity.async_set_hvac_mode(HVACMode.OFF)
    assert climate_entity.hvac_mode == HVACMode.OFF


async def test_turn_on_off(climate_entity):
    """Test turn on/off methods."""
    await climate_entity.async_turn_on()
    assert climate_entity.hvac_mode == HVACMode.HEAT

    await climate_entity.async_turn_off()
    assert climate_entity.hvac_mode == HVACMode.OFF
