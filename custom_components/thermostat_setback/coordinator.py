"""Coordinator for climate setback integration."""

from __future__ import annotations

import logging
from typing import Any
from datetime import datetime

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
        self._schedule_device = config_entry.options[CONF_SCHEDULE_DEVICE]
        self._binary_input = config_entry.options.get(CONF_BINARY_INPUT, None)

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
            "schedule_active": False,

            "forced_setback": False,
            "input_is_active": False,
            "controller_active": True,  # Controller is active by default
            "setback_temperature": 20,
            "normal_temperature": 16,
            "normal_temperature_min": 5.0,
            "normal_temperature_max": 35.0,
            "normal_temperature_step": 0.5,

            # Recovery time tracking
            "recovery_start_time": None,
            "last_recovery_time": None,  # Single recovery time in seconds
            "is_recovering": False,
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

        schedule_state = self.hass.states.get(self._schedule_device)
        if schedule_state is not None:
            self.data["schedule_active"] = schedule_state.state == "on"

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

        # Get min, max and step attributes from the climate device
        min_temp = new_state.attributes.get("min_temp")
        max_temp = new_state.attributes.get("max_temp")
        step = new_state.attributes.get("target_temp_step")
        if min_temp:
            self.data["normal_temperature_min"] = min_temp
        if max_temp:
            self.data["normal_temperature_max"] = max_temp
        if step:
            self.data["normal_temperature_step"] = step

        # Check if we're recovering and have reached the normal temperature
        if self.data["is_recovering"] and not self.data["is_setback"]:
            current_temp = new_state.attributes.get("current_temperature")
            target_temp = new_state.attributes.get("temperature")

            if current_temp is not None and target_temp is not None:
                # Consider temperature reached when current temp is equal or greater than target
                if current_temp >= target_temp:
                    # Recovery complete
                    recovery_time = (
                        datetime.now() - self.data["recovery_start_time"]).total_seconds()

                    # Store the single recovery time
                    self.data["last_recovery_time"] = round(recovery_time, 1)

                    self.data["is_recovering"] = False
                    self.data["recovery_start_time"] = None
                    _LOGGER.debug(
                        "Recovery completed in %.1f seconds", recovery_time)

        self._calculate_setback_state()
        self.async_update_listeners()

    @callback
    def _async_schedule_changed(self, event: Any) -> None:
        """Handle schedule device state changes."""
        new_state = event.data.get("new_state")
        if new_state is None:
            return

        # Activate setback if schedule is active
        self.data["schedule_active"] = new_state.state == "on" or new_state.attributes.get(
            "is_on", False)

        self._calculate_setback_state()
        self.async_update_listeners()

    @callback
    def _async_binary_input_changed(self, event: Any) -> None:
        """Handle binary input state changes."""
        new_state = event.data.get("new_state")
        if new_state is None:
            return

        # Set input is active based on binary input state (on/true/1)
        self.data["input_is_active"] = new_state.state in [
            "on", "true", "1"] or new_state.attributes.get("is_on", False)

        self._calculate_setback_state()
        self.async_update_listeners()

    def _update_climate_temperature(self) -> None:
        """Set the climate device temperature."""
        # Only control temperature if controller is active
        if not self.data["controller_active"]:
            return

        if self.data["is_setback"]:
            target_temperature = self.data["setback_temperature"]
        else:
            target_temperature = self.data["normal_temperature"]

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

    def _calculate_setback_state(self) -> None:
        """Calculate setback state."""
        previous_setback = self.data["is_setback"]
        self.data["is_setback"] = (self.data["schedule_active"] or self.data["input_is_active"]
                                   or self.data["forced_setback"]) and self.data["controller_active"]

        # Track when setback ends and recovery begins
        if previous_setback and not self.data["is_setback"]:
            # Setback just ended, start tracking recovery
            self.data["recovery_start_time"] = datetime.now()
            self.data["is_recovering"] = True
            _LOGGER.debug("Setback ended, starting recovery time tracking")

        self._update_climate_temperature()

    def set_forced_setback(self, forced_setback: bool) -> None:
        """Set forced setback."""
        self.data["forced_setback"] = forced_setback
        self._calculate_setback_state()
        self.async_update_listeners()

    def set_controller_active(self, active: bool) -> None:
        """Set controller active state."""
        self.data["controller_active"] = active
        self._calculate_setback_state()
        self.async_update_listeners()

    def set_setback_temperature(self, temperature: float) -> None:
        """Set setback temperature."""
        self.data["setback_temperature"] = temperature
        self._calculate_setback_state()
        self.async_update_listeners()

    def set_normal_temperature(self, temperature: float) -> None:
        """Set normal temperature."""
        self.data["normal_temperature"] = temperature
        self._calculate_setback_state()
        self.async_update_listeners()

    @property
    def is_setback(self) -> bool:
        """Return if setback is currently active."""
        return self.data["is_setback"]

    @property
    def forced_setback(self) -> bool:
        """Return if setback is forced (manual override)."""
        return self.data["forced_setback"]

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

    @property
    def controller_active(self) -> bool:
        """Return if controller is active."""
        return self.data["controller_active"]

    @property
    def last_recovery_time(self) -> float | None:
        """Return the last recovery time in seconds."""
        return self.data["last_recovery_time"]

    @property
    def is_recovering(self) -> bool:
        """Return if currently recovering from setback."""
        return self.data["is_recovering"]

    @property
    def recovery_start_time(self) -> datetime | None:
        """Return when current recovery started."""
        return self.data["recovery_start_time"]

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info for this integration."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.config_entry.entry_id)},
            name=self._name,
            manufacturer="Thermostat Setback Controller",
            model="Setback Controller",
        )
