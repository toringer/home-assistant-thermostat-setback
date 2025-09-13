"""Config flow for climate setback integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant.core import callback
from homeassistant.const import CONF_NAME
from homeassistant.data_entry_flow import FlowResult
from homeassistant.config_entries import ConfigFlow, OptionsFlowWithReload, ConfigFlowResult, ConfigEntry
from homeassistant.helpers import selector
from homeassistant.helpers import config_validation as cv

from .const import (
    CONF_BINARY_INPUT,
    CONF_CLIMATE_DEVICE,
    CONF_SCHEDULE_DEVICE,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


def get_initial_config_schema() -> vol.Schema:
    """Return the initial config flow schema with only basic required fields."""
    return vol.Schema(
        {
            vol.Required(CONF_NAME, description={"suggested_value": "Thermostat Setback Controller"}): cv.string,
            vol.Required(CONF_CLIMATE_DEVICE, description={"suggested_value": "Select a climate device to control"}): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="climate")
            ),
            vol.Required(CONF_SCHEDULE_DEVICE, description={"suggested_value": "Select a schedule device to monitor"}): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="schedule")
            ),
            vol.Optional(CONF_BINARY_INPUT, description={"suggested_value": "Select a binary input or switch for forced mode"}): selector.EntitySelector(
                selector.EntitySelectorConfig(
                    domain=["binary_sensor", "switch"])
            ),
        }
    )


def get_options_schema() -> vol.Schema:
    """Return the options flow schema for advanced configuration."""
    return vol.Schema(
        {
            vol.Required(CONF_SCHEDULE_DEVICE, description={"suggested_value": "Select a schedule device to monitor"}): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="schedule")
            ),
            vol.Optional(CONF_BINARY_INPUT, description={"suggested_value": "Select a binary input or switch for forced mode"}): selector.EntitySelector(
                selector.EntitySelectorConfig(
                    domain=["binary_sensor", "switch"])
            ),
        }
    )


class ConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for climate setback."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=get_initial_config_schema()
            )

        # Validate that the climate device exists
        climate_entity_id = user_input[CONF_CLIMATE_DEVICE]
        if not self.hass.states.get(climate_entity_id):
            return self.async_show_form(
                step_id="user",
                data_schema=get_initial_config_schema(),
                errors={"base": "climate_device_not_found"},
            )

        # Validate that the schedule device exists if provided
        schedule_entity_id = user_input[CONF_SCHEDULE_DEVICE]
        if not self.hass.states.get(schedule_entity_id):
            return self.async_show_form(
                step_id="user",
                data_schema=get_initial_config_schema(),
                errors={"base": "schedule_device_not_found"},
            )

        # Validate binary input if provided
        if CONF_BINARY_INPUT in user_input and user_input[CONF_BINARY_INPUT]:
            binary_entity_id = user_input[CONF_BINARY_INPUT]
            if not self.hass.states.get(binary_entity_id):
                return self.async_show_form(
                    step_id="user",
                    data_schema=get_initial_config_schema(),
                    errors={"base": "binary_input_not_found"},
                )

        return self.async_create_entry(title=user_input[CONF_NAME], data=user_input, options=user_input)

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> MyOptionsFlow:
        """Create the options flow."""
        return MyOptionsFlow(config_entry)


class MyOptionsFlow(OptionsFlowWithReload):
    """Handle options flow for climate setback."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:

            # Validate that the schedule device exists if provided
            if CONF_SCHEDULE_DEVICE in user_input and user_input[CONF_SCHEDULE_DEVICE]:
                schedule_entity_id = user_input[CONF_SCHEDULE_DEVICE]
                if not self.hass.states.get(schedule_entity_id):
                    current_data = {**self.config_entry.data,
                                    **self.config_entry.options}
                    return self.async_show_form(
                        step_id="init",
                        data_schema=self.add_suggested_values_to_schema(
                            get_options_schema(), self.config_entry.options
                        ),
                        errors={"base": "schedule_device_not_found"},
                    )

            # Validate binary input if provided
            if CONF_BINARY_INPUT in user_input and user_input[CONF_BINARY_INPUT]:
                binary_entity_id = user_input[CONF_BINARY_INPUT]
                if not self.hass.states.get(binary_entity_id):
                    current_data = {**self.config_entry.data,
                                    **self.config_entry.options}
                    return self.async_show_form(
                        step_id="init",
                        data_schema=self.add_suggested_values_to_schema(
                            get_options_schema(), self.config_entry.options
                        ),
                        errors={"base": "binary_input_not_found"},
                    )

            # Replace overlapping data in config_entry.data with user_input
            # user_input values take precedence over existing config_entry.data values
            updated_data = {**self.config_entry.data, **user_input}

            # Update the config entry with the updated data
            # self.hass.config_entries.async_update_entry(
            #     self.config_entry, data=self.config_entry.options
            # )

            # Clear options since they're now in data
            return self.async_create_entry(data=user_input)

        # Load existing settings from config_entry.data and options
        current_data = {**self.config_entry.data, **self.config_entry.options}

        return self.async_show_form(
            step_id="init",
            data_schema=self.add_suggested_values_to_schema(
                get_options_schema(), current_data
            ),
        )
