"""Coordinator for climate setback integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.climate import ATTR_TEMPERATURE
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.const import CONF_NAME

from .const import (
    CONF_BINARY_INPUT,
    CONF_CLIMATE_DEVICE,
    CONF_SCHEDULE_DEVICE,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class ClimateSetbackCoordinator(DataUpdateCoordinator):
    """Coordinator for climate setback state management."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        self.config_entry = config_entry
        self._name = config_entry.data[CONF_NAME]
        self._climate_device = config_entry.data[CONF_CLIMATE_DEVICE]
        self._schedule_device = config_entry.data[CONF_SCHEDULE_DEVICE]
        self._binary_input = config_entry.data.get(CONF_BINARY_INPUT)

        # Default temperature values
        self._default_normal_temperature = 20.0
        self._default_setback_temperature = 16.0

        # Store unsubscribe callbacks
        self._unsub_climate = None
        self._unsub_schedule = None
        self._unsub_binary_input = None

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{config_entry.entry_id}",
            update_interval=None,  # We update on state changes, not on schedule
        )

        # Initialize data structure with default values
        self.data = {
            "is_setback": False,
            "forced_setback": False,
            "controller_active": True,  # Controller is active by default
            "setback_temperature": self._default_setback_temperature,
            "normal_temperature": self._default_normal_temperature,
            "normal_temperature_min": 5.0,
            "normal_temperature_max": 35.0,
            "normal_temperature_step": 0.5,
        }

    async def _async_update_data(self) -> dict[str, Any]:
        """Update coordinator data."""
        # This method is called by the base coordinator but we handle updates
        # through state change callbacks instead
        return self.data

    async def async_setup(self) -> None:
        """Set up the coordinator."""
        # Track climate device state changes
        self._unsub_climate = async_track_state_change_event(
            self.hass,
            [self._climate_device],
            self._async_climate_changed,
        )

        # Track schedule device state changes
        self._unsub_schedule = async_track_state_change_event(
            self.hass,
            [self._schedule_device],
            self._async_schedule_changed,
        )

        # Track binary input state changes if configured
        if self._binary_input:
            self._unsub_binary_input = async_track_state_change_event(
                self.hass,
                [self._binary_input],
                self._async_binary_input_changed,
            )

    def async_cleanup(self) -> None:
        """Clean up the coordinator."""
        if self._unsub_climate:
            self._unsub_climate()
        if self._unsub_schedule:
            self._unsub_schedule()
        if self._unsub_binary_input:
            self._unsub_binary_input()

    @callback
    def _async_climate_changed(self, event: Any) -> None:
        """Handle climate device state changes."""
        new_state = event.data.get("new_state")
        if new_state is None:
            return

        min_temp = new_state.attributes.get("min_temp")
        max_temp = new_state.attributes.get("max_temp")
        step = new_state.attributes.get("target_temp_step")
        if min_temp:
            self.data["normal_temperature_min"] = min_temp
        if max_temp:
            self.data["normal_temperature_max"] = max_temp
        if step:
            self.data["normal_temperature_step"] = step

        self.set_climate_temperature()
        self.async_update_listeners()

    @callback
    def _async_schedule_changed(self, event: Any) -> None:
        """Handle schedule device state changes."""
        new_state = event.data.get("new_state")
        if new_state is None:
            return
        self.data["is_setback"] = new_state.state == "on" or new_state.attributes.get(
            "is_on", False)

        self.set_climate_temperature()
        self.async_update_listeners()

    @callback
    def _async_binary_input_changed(self, event: Any) -> None:
        """Handle binary input state changes."""
        new_state = event.data.get("new_state")
        if new_state is None:
            return

        # Check if binary input is active (on/true/1)
        is_active = new_state.state in [
            "on", "true", "1"] or new_state.attributes.get("is_on", False)

        # Set forced setback based on binary input state
        self.data["forced_setback"] = is_active

        self.set_climate_temperature()
        self.async_update_listeners()

    def set_climate_temperature(self) -> None:
        """Set the climate device temperature."""
        # Only control temperature if controller is active
        if not self.data["controller_active"]:
            return

        target_temperature = self.data["setback_temperature"] if self.data[
            "is_setback"] or self.data["forced_setback"] else self.data["normal_temperature"]

        self.hass.async_create_task(
            self.hass.services.async_call(
                "climate",
                "set_temperature",
                {
                    "entity_id": self._climate_device,
                    ATTR_TEMPERATURE: target_temperature,
                },
            )
        )

    def set_setback(self, is_setback: bool) -> None:
        """Set setback."""
        # Only allow setback changes if controller is active
        if not self.data["controller_active"]:
            return

        # get schedule state as bool into variable
        schedule_state = self.hass.states.get(self._schedule_device)
        schedule_active = schedule_state.state == "on" or schedule_state.attributes.get(
            "is_on", False)

        self.data["is_setback"] = schedule_active or is_setback
        self.set_climate_temperature()
        self.async_update_listeners()

    @property
    def is_setback(self) -> bool:
        """Return if setback is currently active."""
        return self.data["is_setback"]

    @property
    def forced_setback(self) -> bool:
        """Return if setback is forced (manual override)."""
        return self.data["forced_setback"]

    def set_forced_setback(self, forced_setback: bool) -> None:
        """Set forced setback."""
        self.data["forced_setback"] = forced_setback
        self.set_climate_temperature()
        self.async_update_listeners()

    @property
    def setback_temperature(self) -> float:
        """Return setback temperature."""
        return self.data["setback_temperature"]

    @property
    def normal_temperature(self) -> float:
        """Return normal temperature."""
        return self.data["normal_temperature"]

    @property
    def normal_temperature_min(self) -> float:
        """Return normal temperature minimum."""
        return self.data["normal_temperature_min"]

    @property
    def normal_temperature_max(self) -> float:
        """Return normal temperature maximum."""
        return self.data["normal_temperature_max"]

    @property
    def normal_temperature_step(self) -> float:
        """Return normal temperature step."""
        return self.data["normal_temperature_step"]

    @property
    def climate_device(self) -> str:
        """Return climate device entity ID."""
        return self._climate_device

    @property
    def schedule_device(self) -> str:
        """Return schedule device entity ID."""
        return self._schedule_device

    @property
    def binary_input_device(self) -> str | None:
        """Return binary input device entity ID."""
        return self._binary_input

    def set_controller_active(self, active: bool) -> None:
        """Set controller active state."""
        self.data["controller_active"] = active

        # If controller is being deactivated, stop controlling temperature
        if not active:
            self.data["is_setback"] = False

        self.set_setback(False)
        self.async_update_listeners()

    @property
    def controller_active(self) -> bool:
        """Return if controller is active."""
        return self.data["controller_active"]

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info for this integration."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.config_entry.entry_id)},
            name=self._name,
            manufacturer="Thermostat Setback Controller",
            model="Setback Controller",
        )
