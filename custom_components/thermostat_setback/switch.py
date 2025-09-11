"""Switch entity for climate setback integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTR_CONTROLLER_ACTIVE,
    ATTR_IS_SETBACK,
    ATTR_NORMAL_TEMPERATURE,
    ATTR_SETBACK_TEMPERATURE,
    CONF_CLIMATE_DEVICE,
    CONF_SCHEDULE_DEVICE,
    DOMAIN,
)
from .coordinator import ClimateSetbackCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up climate setback switch from a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    async_add_entities([
        ClimateSetbackSwitch(config_entry, coordinator),
        ControllerSwitch(config_entry, coordinator)
    ])


class ClimateSetbackSwitch(SwitchEntity, CoordinatorEntity):
    """Representation of a climate setback switch entity."""

    _attr_should_poll = False

    def __init__(self, config_entry: ConfigEntry, coordinator: ClimateSetbackCoordinator) -> None:
        """Initialize the climate setback switch."""
        super().__init__(coordinator, context=config_entry.entry_id)
        self._config_entry = config_entry
        self.coordinator = coordinator
        self._attr_name = f"{config_entry.data[CONF_CLIMATE_DEVICE].replace('climate.', '').replace('_', ' ').title()} Setback"
        self._attr_unique_id = f"thermostat_setback_switch_{config_entry.entry_id}"
        self._attr_device_info = coordinator.device_info

    @property
    def is_on(self) -> bool:
        """Return True if the switch is on (setback is active)."""
        return self.coordinator.is_setback

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on (enable setback)."""
        self.coordinator.set_setback(True)
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off (disable setback)."""
        self.coordinator.set_setback(False)
        self.async_write_ha_state()


class ControllerSwitch(SwitchEntity, CoordinatorEntity):
    """Representation of a controller active switch entity."""

    _attr_should_poll = False

    def __init__(self, config_entry: ConfigEntry, coordinator: ClimateSetbackCoordinator) -> None:
        """Initialize the controller switch."""
        super().__init__(coordinator, context=config_entry.entry_id)
        self._config_entry = config_entry
        self.coordinator = coordinator
        self._attr_name = f"{config_entry.data[CONF_CLIMATE_DEVICE].replace('climate.', '').replace('_', ' ').title()} Thermostat Controller"
        self._attr_unique_id = f"thermostat_setback_controller_{config_entry.entry_id}"
        self._attr_device_info = coordinator.device_info

    @property
    def is_on(self) -> bool:
        """Return True if the controller is active."""
        return self.coordinator.controller_active

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the controller on (enable controller)."""
        self.coordinator.set_controller_active(True)
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the controller off (disable controller)."""
        self.coordinator.set_controller_active(False)
        self.async_write_ha_state()
