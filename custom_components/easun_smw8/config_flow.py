"""Config flow for Easun SMW 8kW integration."""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant

from . import DOMAIN, send_command, COMMANDS

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("port", default="/dev/ttyUSB0"): str,
    }
)


async def validate_connection(hass: HomeAssistant, port: str) -> None:
    """Validate serial connection to inverter."""
    def test():
        response = send_command(port, COMMANDS["QPIGS"])
        if not response.startswith("("):
            raise ValueError(f"Invalid response: {response!r}")
    
    await hass.async_add_executor_job(test)


class EasunSMW8ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle config flow for Easun SMW8."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            try:
                await validate_connection(self.hass, user_input["port"])
                return self.async_create_entry(
                    title=f"Easun SMW8 ({user_input['port']})",
                    data=user_input,
                )
            except ValueError as e:
                errors["base"] = "cannot_connect"
            except Exception:
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
