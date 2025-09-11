"""Sensor entity for climate setback integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_state_change
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.const import STATE_OFF, STATE_ON
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTR_CONTROLLER_ACTIVE,
    ATTR_IS_SETBACK,
    ATTR_NORMAL_TEMPERATURE,
    ATTR_SETBACK_TEMPERATURE,
    CONF_CLIMATE_DEVICE,
    CONF_NORMAL_TEMPERATURE,
    CONF_SCHEDULE_DEVICE,
    CONF_SETBACK_TEMPERATURE,
    DOMAIN,
    SERVICE_CLEAR_SETBACK,
    SERVICE_SET_SETBACK,
)
from .coordinator import ClimateSetbackCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up climate setback sensor from a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    async_add_entities([ClimateSetbackSensor(config_entry, coordinator)])


class ClimateSetbackSensor(SensorEntity, CoordinatorEntity, RestoreEntity):
    """Representation of a climate setback sensor entity."""

    _attr_should_poll = False

    def __init__(self, config_entry: ConfigEntry, coordinator: ClimateSetbackCoordinator) -> None:
        super().__init__(coordinator, context=config_entry.entry_id)
        """Initialize the climate setback sensor."""
        self._config_entry = config_entry
        self.coordinator = coordinator
        self._attr_name = f"{config_entry.data[CONF_CLIMATE_DEVICE].replace('climate.', '').replace('_', ' ').title()} Setback Status"
        self._attr_unique_id = f"climate_setback_sensor_{config_entry.entry_id}"

    @property
    def native_value(self) -> str:
        """Return the current setback status."""
        return STATE_ON if self.coordinator.data["is_setback"] else STATE_OFF

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return the unit of measurement."""
        return None

    # async def async_added_to_hass(self) -> None:
    #     """Run when entity about to be added to hass."""
    #     await super().async_added_to_hass()

    #     # Register this entity in the domain data
    #     if self._config_entry.entry_id in self.hass.data[DOMAIN]:
    #         self.hass.data[DOMAIN][self._config_entry.entry_id]["entities"]["sensor"] = self

    #     # Restore state
    #     if (last_state := await self.async_get_last_state()) is not None:
    #         self._is_setback = last_state.attributes.get(
    #             ATTR_IS_SETBACK, False)
    #         self._target_temperature = last_state.attributes.get(
    #             "target_temperature", self._normal_temperature)

    #     # Initial state update
    #     await self._async_update_state()

    async def _async_update_state(self) -> None:
        """Update the entity state."""
        # Get current climate state
        climate_state = self.hass.states.get(self.coordinator.climate_device)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        return {
            ATTR_IS_SETBACK: self.coordinator.data["is_setback"],
            ATTR_SETBACK_TEMPERATURE: self.coordinator.setback_temperature,
            ATTR_NORMAL_TEMPERATURE: self.coordinator.normal_temperature,
            ATTR_CONTROLLER_ACTIVE: self.coordinator.controller_active,
            "climate_device": self.coordinator.climate_device,
            "schedule_device": self.coordinator.schedule_device,
        }
