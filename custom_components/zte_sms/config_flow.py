
"""Configuration flow for ZTE SMS."""

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries

from .const import DOMAIN, DEFAULT_HOST


class ZTESMSConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the ZTE SMS configuration flow."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Configure the modem address."""
        errors = {}

        if user_input is not None:
            host = user_input["host"].strip()

            await self.async_set_unique_id(host)
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=f"ZTE SMS ({host})",
                data={"host": host},
            )

        schema = vol.Schema(
            {
                vol.Required(
                    "host",
                    default=DEFAULT_HOST,
                ): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )
