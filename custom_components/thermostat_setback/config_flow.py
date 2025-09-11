"""Config flow for climate setback integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector
from homeassistant.helpers import config_validation as cv

from .const import (
    CONF_CLIMATE_DEVICE,
    CONF_SCHEDULE_DEVICE,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


def get_user_data_schema() -> vol.Schema:
    """Return the user data schema with translations."""
    return vol.Schema(
        {
            vol.Required(CONF_NAME, description={"suggested_value": "Thermostat Setback Controller"}): cv.string,
            vol.Required(CONF_CLIMATE_DEVICE, description={"suggested_value": "Select a climate device to control"}): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="climate")
            ),
            vol.Required(CONF_SCHEDULE_DEVICE, description={"suggested_value": "Select a schedule device to monitor"}): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="schedule")
            ),
        }
    )


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for climate setback."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=get_user_data_schema()
            )

        # Validate that the climate device exists
        climate_entity_id = user_input[CONF_CLIMATE_DEVICE]
        if not self.hass.states.get(climate_entity_id):
            return self.async_show_form(
                step_id="user",
                data_schema=get_user_data_schema(),
                errors={"base": "climate_device_not_found"},
            )

        # Validate that the schedule device exists
        schedule_entity_id = user_input[CONF_SCHEDULE_DEVICE]
        if not self.hass.states.get(schedule_entity_id):
            return self.async_show_form(
                step_id="user",
                data_schema=get_user_data_schema(),
                errors={"base": "schedule_device_not_found"},
            )

        return self.async_create_entry(
            title=user_input[CONF_NAME], data=user_input
        )
