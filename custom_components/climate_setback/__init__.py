"""Climate Setback Controller for Home Assistant."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import ClimateSetbackCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.SWITCH, Platform.NUMBER]


async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:
    """Set up the climate setback component."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up climate setback from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Create coordinator
    coordinator = ClimateSetbackCoordinator(hass, entry)
    await coordinator.async_setup()

    hass.data[DOMAIN][entry.entry_id] = {
        "config": entry.data,
        "coordinator": coordinator,
        "entities": {}
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        # Clean up coordinator
        if entry.entry_id in hass.data[DOMAIN]:
            coordinator = hass.data[DOMAIN][entry.entry_id].get("coordinator")
            if coordinator:
                coordinator.async_cleanup()
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
