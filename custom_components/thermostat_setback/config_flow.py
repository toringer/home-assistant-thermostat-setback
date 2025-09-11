"""Config flow for climate setback integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_NAME, CONF_TEMPERATURE_UNIT
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector
from homeassistant.helpers import config_validation as cv

from .const import (
    CONF_CLIMATE_DEVICE,
    CONF_NORMAL_TEMPERATURE,
    CONF_SCHEDULE_DEVICE,
    CONF_SETBACK_TEMPERATURE,
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
            vol.Required(CONF_SETBACK_TEMPERATURE, description={"suggested_value": "Temperature when in setback mode (e.g., 16.0)"}): vol.Coerce(float),
            vol.Required(CONF_NORMAL_TEMPERATURE, description={"suggested_value": "Normal temperature when not in setback (e.g., 20.0)"}): vol.Coerce(float),
        }
    )


def get_options_schema(config_entry: config_entries.ConfigEntry) -> vol.Schema:
    """Return the options schema with translations."""
    return vol.Schema(
        {
            vol.Required(
                CONF_SETBACK_TEMPERATURE,
                default=config_entry.options.get(
                    CONF_SETBACK_TEMPERATURE,
                    config_entry.data[CONF_SETBACK_TEMPERATURE],
                ),
                description={
                    "suggested_value": "Temperature when in setback mode (e.g., 16.0)"}
            ): vol.Coerce(float),
            vol.Required(
                CONF_NORMAL_TEMPERATURE,
                default=config_entry.options.get(
                    CONF_NORMAL_TEMPERATURE,
                    config_entry.data[CONF_NORMAL_TEMPERATURE],
                ),
                description={
                    "suggested_value": "Normal temperature when not in setback (e.g., 20.0)"}
            ): vol.Coerce(float),
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

        # Validate temperature values
        if user_input[CONF_SETBACK_TEMPERATURE] >= user_input[CONF_NORMAL_TEMPERATURE]:
            return self.async_show_form(
                step_id="user",
                data_schema=get_user_data_schema(),
                errors={"base": "invalid_temperature_range"},
            )

        return self.async_create_entry(
            title=user_input[CONF_NAME], data=user_input
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> OptionsFlowHandler:
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for climate setback."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=get_options_schema(self.config_entry),
        )
