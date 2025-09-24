"""Sensor entity for climate setback integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.const import STATE_OFF, STATE_ON
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_CLIMATE_DEVICE,
    DOMAIN,
)
from .coordinator import ClimateSetbackCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up climate setback sensors from a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    async_add_entities([
        ClimateSetbackSensor(config_entry, coordinator),
        ClimateRecoveryTimeSensor(config_entry, coordinator)
    ])


class ClimateSetbackSensor(SensorEntity, CoordinatorEntity):
    """Representation of a climate setback sensor entity."""

    _attr_should_poll = False

    def __init__(self, config_entry: ConfigEntry, coordinator: ClimateSetbackCoordinator) -> None:
        super().__init__(coordinator, context=config_entry.entry_id)
        """Initialize the climate setback sensor."""
        self._config_entry = config_entry
        self.coordinator = coordinator
        self._attr_name = "Setback Status"
        self._attr_unique_id = f"thermostat_setback_sensor_{config_entry.entry_id}"
        self._attr_device_info = coordinator.device_info

    @property
    def native_value(self) -> str:
        """Return the current setback status."""
        return STATE_ON if self.coordinator.data["is_setback"] else STATE_OFF

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return the unit of measurement."""
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        return {
            "climate_device": self.coordinator.climate_device,
            "schedule_device": self.coordinator.schedule_device,
            "binary_input_device": self.coordinator.binary_input_device,
        }


class ClimateRecoveryTimeSensor(SensorEntity, CoordinatorEntity):
    """Representation of a climate recovery time sensor entity."""

    _attr_should_poll = False
    _attr_device_class = SensorDeviceClass.DURATION

    def __init__(self, config_entry: ConfigEntry, coordinator: ClimateSetbackCoordinator) -> None:
        super().__init__(coordinator, context=config_entry.entry_id)
        """Initialize the climate recovery time sensor."""
        self._config_entry = config_entry
        self.coordinator = coordinator
        self._attr_name = "Recovery Time"
        self._attr_unique_id = f"thermostat_recovery_time_sensor_{config_entry.entry_id}"
        self._attr_device_info = coordinator.device_info

    @property
    def native_value(self) -> float | None:
        """Return the last recovery time."""
        return self.coordinator.last_recovery_time

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return the unit of measurement."""
        return "s"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        return {
            "is_recovering": self.coordinator.is_recovering,
        }
