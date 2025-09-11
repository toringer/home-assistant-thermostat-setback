"""Constants for the climate setback integration."""

from __future__ import annotations

DOMAIN = "climate_setback"

# Configuration keys
CONF_CLIMATE_DEVICE = "climate_device"
CONF_SCHEDULE_DEVICE = "schedule_device"
CONF_SETBACK_TEMPERATURE = "setback_temperature"
CONF_NORMAL_TEMPERATURE = "normal_temperature"

# Service names
SERVICE_SET_SETBACK = "set_setback"
SERVICE_CLEAR_SETBACK = "clear_setback"

# Attributes
ATTR_IS_SETBACK = "is_setback"
ATTR_SETBACK_TEMPERATURE = "setback_temperature"
ATTR_NORMAL_TEMPERATURE = "normal_temperature"
ATTR_CONTROLLER_ACTIVE = "controller_active"
