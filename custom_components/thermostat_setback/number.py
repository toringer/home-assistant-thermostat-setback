"""Number entities for climate setback integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.restore_state import RestoreEntity

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
    """Set up climate setback number entities from a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    async_add_entities([
        SetbackTemperatureNumber(config_entry, coordinator),
        NormalTemperatureNumber(config_entry, coordinator)
    ])


class SetbackTemperatureNumber(NumberEntity, CoordinatorEntity, RestoreEntity):
    """Representation of a setback temperature number entity."""

    _attr_should_poll = False
    _attr_mode = NumberMode.AUTO

    def __init__(self, config_entry: ConfigEntry, coordinator: ClimateSetbackCoordinator) -> None:
        """Initialize the setback temperature number."""
        super().__init__(coordinator, context=config_entry.entry_id)
        self._config_entry = config_entry
        self.coordinator = coordinator
        self._attr_name = "Setback Temperature"
        self._attr_unique_id = f"thermostat_setback_temperature_{config_entry.entry_id}"
        self._attr_native_unit_of_measurement = "°C"
        self._attr_device_info = coordinator.device_info
        self._attr_icon = "mdi:thermometer-low"

    @property
    def native_value(self) -> float:
        """Return the current setback temperature."""
        return self.coordinator.data["setback_temperature"]

    @property
    def native_min_value(self) -> float:
        """Return the current setback temperature minimum."""
        return self.coordinator.normal_temperature_min

    @property
    def native_max_value(self) -> float:
        """Return the current setback temperature maximum."""
        return self.coordinator.normal_temperature_max

    @property
    def native_step(self) -> float:
        """Return the current setback temperature step."""
        return self.coordinator.normal_temperature_step

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        return {
            "climate_device": self.coordinator.climate_device,
            "schedule_device": self.coordinator.schedule_device,
            "controller_active": self.coordinator.controller_active,
        }

    async def async_set_native_value(self, value: float) -> None:
        """Set the setback temperature."""
        self.coordinator.set_setback_temperature(value)
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        """Handle entity which will be added."""
        await super().async_added_to_hass()

        state = await self.async_get_last_state()
        if not state:
            return
        self.coordinator.data["setback_temperature"] = state.state


class NormalTemperatureNumber(NumberEntity, CoordinatorEntity, RestoreEntity):
    """Representation of a normal temperature number entity."""

    _attr_should_poll = False
    _attr_mode = NumberMode.SLIDER

    def __init__(self, config_entry: ConfigEntry, coordinator: ClimateSetbackCoordinator) -> None:
        """Initialize the normal temperature number."""
        super().__init__(coordinator, context=config_entry.entry_id)
        self._config_entry = config_entry
        self.coordinator = coordinator
        self._attr_name = "Normal Temperature"
        self._attr_unique_id = f"climate_normal_temperature_{config_entry.entry_id}"
        self._attr_native_unit_of_measurement = "°C"
        self._attr_device_info = coordinator.device_info
        self._attr_icon = "mdi:thermometer"

    @property
    def native_min_value(self) -> float:
        """Return the current normal temperature minimum."""
        return self.coordinator.normal_temperature_min

    @property
    def native_max_value(self) -> float:
        """Return the current normal temperature maximum."""
        return self.coordinator.normal_temperature_max

    @property
    def native_step(self) -> float:
        """Return the current normal temperature step."""
        return self.coordinator.normal_temperature_step

    @property
    def native_value(self) -> float:
        """Return the current normal temperature."""
        return self.coordinator.data["normal_temperature"]

    async def async_set_native_value(self, value: float) -> None:
        """Set the normal temperature."""
        self.coordinator.set_normal_temperature(value)
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        """Handle entity which will be added."""
        await super().async_added_to_hass()

        state = await self.async_get_last_state()
        if not state:
            return
        self.coordinator.data["normal_temperature"] = state.state
