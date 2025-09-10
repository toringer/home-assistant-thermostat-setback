"""Services for climate setback integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import entity_registry as er

from .const import DOMAIN, SERVICE_CLEAR_SETBACK, SERVICE_SET_SETBACK

_LOGGER = logging.getLogger(__name__)


async def async_setup_services(hass: HomeAssistant) -> None:
    """Set up services for climate setback."""

    async def async_set_setback_service(service: ServiceCall) -> None:
        """Handle set_setback service call."""
        entity_id = service.data.get("entity_id")
        if not entity_id:
            _LOGGER.error("No entity_id provided")
            return

        # Get the entity
        entity_registry = er.async_get(hass)
        entity = entity_registry.async_get(entity_id)
        if not entity or entity.platform != DOMAIN:
            _LOGGER.error(
                "Entity %s not found or not a climate setback entity", entity_id)
            return

        # Find the climate setback sensor entity and enable setback
        for entry_id, entry_data in hass.data[DOMAIN].items():
            if entry_id == entity.config_entry_id:
                # Get the sensor entity
                sensor_entity = None
                for entity_platform in hass.data[DOMAIN][entry_id].values():
                    if hasattr(entity_platform, "async_set_setback"):
                        sensor_entity = entity_platform
                        break

                if sensor_entity:
                    await sensor_entity.async_set_setback()
                else:
                    _LOGGER.error(
                        "Climate setback sensor entity not found for entry %s", entry_id)
                break

    async def async_clear_setback_service(service: ServiceCall) -> None:
        """Handle clear_setback service call."""
        entity_id = service.data.get("entity_id")
        if not entity_id:
            _LOGGER.error("No entity_id provided")
            return

        # Get the entity
        entity_registry = er.async_get(hass)
        entity = entity_registry.async_get(entity_id)
        if not entity or entity.platform != DOMAIN:
            _LOGGER.error(
                "Entity %s not found or not a climate setback entity", entity_id)
            return

        # Find the climate setback sensor entity and disable setback
        for entry_id, entry_data in hass.data[DOMAIN].items():
            if entry_id == entity.config_entry_id:
                # Get the sensor entity
                sensor_entity = None
                for entity_platform in hass.data[DOMAIN][entry_id].values():
                    if hasattr(entity_platform, "async_clear_setback"):
                        sensor_entity = entity_platform
                        break

                if sensor_entity:
                    await sensor_entity.async_clear_setback()
                else:
                    _LOGGER.error(
                        "Climate setback sensor entity not found for entry %s", entry_id)
                break

    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_SETBACK,
        async_set_setback_service,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_CLEAR_SETBACK,
        async_clear_setback_service,
    )
