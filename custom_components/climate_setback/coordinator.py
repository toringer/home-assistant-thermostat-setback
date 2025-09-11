"""Coordinator for climate setback integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.climate import ATTR_TEMPERATURE
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.event import async_track_state_change
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    CONF_CLIMATE_DEVICE,
    CONF_NORMAL_TEMPERATURE,
    CONF_SCHEDULE_DEVICE,
    CONF_SETBACK_TEMPERATURE,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class ClimateSetbackCoordinator(DataUpdateCoordinator):
    """Coordinator for climate setback state management."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        self.config_entry = config_entry
        self._climate_device = config_entry.data[CONF_CLIMATE_DEVICE]
        self._schedule_device = config_entry.data[CONF_SCHEDULE_DEVICE]
        self._setback_temperature = config_entry.data[CONF_SETBACK_TEMPERATURE]
        self._normal_temperature = config_entry.data[CONF_NORMAL_TEMPERATURE]

        # Store unsubscribe callbacks
        self._unsub_climate = None
        self._unsub_schedule = None

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{config_entry.entry_id}",
            update_interval=None,  # We update on state changes, not on schedule
        )

        # Initialize data structure
        self.data = {
            "is_setback": False,
            "forced_setback": False,
            "controller_active": True,  # Controller is active by default
            "setback_temperature": self._setback_temperature,
            "normal_temperature": self._normal_temperature,
        }

    async def _async_update_data(self) -> dict[str, Any]:
        """Update coordinator data."""
        # This method is called by the base coordinator but we handle updates
        # through state change callbacks instead
        return self.data

    async def async_setup(self) -> None:
        """Set up the coordinator."""
        # Track climate device state changes
        self._unsub_climate = async_track_state_change(
            self.hass,
            self._climate_device,
            self._async_climate_changed,
        )

        # Track schedule device state changes
        self._unsub_schedule = async_track_state_change(
            self.hass,
            self._schedule_device,
            self._async_schedule_changed,
        )

    def async_cleanup(self) -> None:
        """Clean up the coordinator."""
        if self._unsub_climate:
            self._unsub_climate()
        if self._unsub_schedule:
            self._unsub_schedule()

    @callback
    def _async_climate_changed(self, entity_id: str, old_state: Any, new_state: Any) -> None:
        """Handle climate device state changes."""
        if new_state is None:
            return

        self.set_climate_temperature()
        self.async_update_listeners()

    @callback
    def _async_schedule_changed(self, entity_id: str, old_state: Any, new_state: Any) -> None:
        """Handle schedule device state changes."""
        if new_state is None:
            return
        self.data["is_setback"] = new_state.state == "on" or new_state.attributes.get(
            "is_on", False)

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

        # # Only auto-control if not manually controlled
        # if not self.data["is_manually_controlled"]:
        #     # Check if schedule is active
        #     schedule_active = new_state.state == "on" or new_state.attributes.get(
        #         "is_on", False)

        #     if schedule_active and not self.data["is_setback"]:
        #         # Schedule is active, enable setback
        #         self.hass.async_create_task(
        #             self.async_set_setback(True, forced=False))
        #     elif not schedule_active and self.data["is_setback"] and not self.data["forced_setback"]:
        #         # Schedule is inactive, disable setback (only if not forced)
        #         self.hass.async_create_task(
        #             self.async_set_setback(False, forced=False))

    # set setback

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

    @property
    def setback_temperature(self) -> float:
        """Return setback temperature."""
        return self.data["setback_temperature"]

    @property
    def normal_temperature(self) -> float:
        """Return normal temperature."""
        return self.data["normal_temperature"]

    @property
    def climate_device(self) -> str:
        """Return climate device entity ID."""
        return self._climate_device

    @property
    def schedule_device(self) -> str:
        """Return schedule device entity ID."""
        return self._schedule_device

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
            name=f"Climate Setback Controller ({self._climate_device.replace('climate.', '').replace('_', ' ').title()})",
            manufacturer="Climate Setback Controller",
            model="Setback Controller",
            sw_version="1.0.0",
        )
