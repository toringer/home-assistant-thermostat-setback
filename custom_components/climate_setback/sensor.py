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

from .const import (
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

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up climate setback sensor from a config entry."""
    async_add_entities([ClimateSetbackSensor(config_entry)])


class ClimateSetbackSensor(SensorEntity, RestoreEntity):
    """Representation of a climate setback sensor entity."""

    _attr_should_poll = False

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize the climate setback sensor."""
        self._config_entry = config_entry
        self._attr_name = f"{config_entry.data[CONF_CLIMATE_DEVICE].replace('climate.', '').replace('_', ' ').title()} Setback Status"
        self._attr_unique_id = f"climate_setback_sensor_{config_entry.entry_id}"

        # Configuration
        self._climate_device = config_entry.data[CONF_CLIMATE_DEVICE]
        self._schedule_device = config_entry.data[CONF_SCHEDULE_DEVICE]
        self._setback_temperature = config_entry.data[CONF_SETBACK_TEMPERATURE]
        self._normal_temperature = config_entry.data[CONF_NORMAL_TEMPERATURE]

        # State
        self._is_setback = False
        self._target_temperature = self._normal_temperature
        self._current_temperature = None

    @property
    def native_value(self) -> str:
        """Return the current setback status."""
        return STATE_ON if self._is_setback else STATE_OFF

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return the unit of measurement."""
        return None

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added to hass."""
        await super().async_added_to_hass()

        # Restore state
        if (last_state := await self.async_get_last_state()) is not None:
            self._is_setback = last_state.attributes.get(
                ATTR_IS_SETBACK, False)
            self._target_temperature = last_state.attributes.get(
                "target_temperature", self._normal_temperature)

        # Track climate device state changes
        self.async_on_remove(
            async_track_state_change(
                self.hass,
                self._climate_device,
                self._async_climate_changed,
            )
        )

        # Track schedule device state changes
        self.async_on_remove(
            async_track_state_change(
                self.hass,
                self._schedule_device,
                self._async_schedule_changed,
            )
        )

        # Initial state update
        await self._async_update_state()

    @callback
    def _async_climate_changed(self, entity_id: str, old_state: Any, new_state: Any) -> None:
        """Handle climate device state changes."""
        if new_state is None:
            return

        # Update current temperature
        if new_state.attributes.get("current_temperature") is not None:
            self._current_temperature = new_state.attributes["current_temperature"]

        self.async_write_ha_state()

    @callback
    def _async_schedule_changed(self, entity_id: str, old_state: Any, new_state: Any) -> None:
        """Handle schedule device state changes."""
        if new_state is None:
            return

        # Check if schedule is active (assuming schedule entity has 'is_on' attribute)
        schedule_active = new_state.state == "on" or new_state.attributes.get(
            "is_on", False)

        if schedule_active and not self._is_setback:
            # Schedule is active, enable setback
            self._is_setback = True
            self._target_temperature = self._setback_temperature
            self._async_control_climate()
        elif not schedule_active and self._is_setback:
            # Schedule is inactive, disable setback
            self._is_setback = False
            self._target_temperature = self._normal_temperature
            self._async_control_climate()

        self.async_write_ha_state()

    async def _async_update_state(self) -> None:
        """Update the entity state."""
        # Get current climate state
        climate_state = self.hass.states.get(self._climate_device)
        if climate_state:
            if climate_state.attributes.get("current_temperature") is not None:
                self._current_temperature = climate_state.attributes["current_temperature"]

        # Get current schedule state
        schedule_state = self.hass.states.get(self._schedule_device)
        if schedule_state:
            schedule_active = schedule_state.state == "on" or schedule_state.attributes.get(
                "is_on", False)
            if schedule_active and not self._is_setback:
                self._is_setback = True
                self._target_temperature = self._setback_temperature
                self._async_control_climate()
            elif not schedule_active and self._is_setback:
                self._is_setback = False
                self._target_temperature = self._normal_temperature
                self._async_control_climate()

    @callback
    def _async_control_climate(self) -> None:
        """Control the climate device."""
        from homeassistant.const import ATTR_TEMPERATURE

        self.hass.async_create_task(
            self.hass.services.async_call(
                "climate",
                "set_temperature",
                {
                    "entity_id": self._climate_device,
                    ATTR_TEMPERATURE: self._target_temperature,
                },
            )
        )

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        return {
            ATTR_IS_SETBACK: self._is_setback,
            ATTR_SETBACK_TEMPERATURE: self._setback_temperature,
            ATTR_NORMAL_TEMPERATURE: self._normal_temperature,
            "target_temperature": self._target_temperature,
            "current_temperature": self._current_temperature,
            "climate_device": self._climate_device,
            "schedule_device": self._schedule_device,
        }

    async def async_set_setback(self) -> None:
        """Manually enable setback mode."""
        self._is_setback = True
        self._target_temperature = self._setback_temperature
        self._async_control_climate()
        self.async_write_ha_state()

    async def async_clear_setback(self) -> None:
        """Manually disable setback mode."""
        self._is_setback = False
        self._target_temperature = self._normal_temperature
        self._async_control_climate()
        self.async_write_ha_state()
