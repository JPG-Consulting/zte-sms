
"""Configuration flow for ZTE SMS."""

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers import selector

from .const import DOMAIN, DEFAULT_HOST


class ZTESMSConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the ZTE SMS configuration flow."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Configure the modem and default SMS recipients."""
        errors = {}

        if user_input is not None:
            host = user_input["host"].strip()

            recipients = [
                number.strip()
                for number in user_input.get("recipients", [])
                if number.strip()
            ]

            if any(
                not number.startswith("+")
                or not number[1:].isdigit()
                for number in recipients
            ):
                errors["base"] = "invalid_phone_number"
            else:
                await self.async_set_unique_id(host)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"ZTE SMS ({host})",
                    data={
                        "host": host,
                        "recipients": list(dict.fromkeys(recipients)),
                    },
                )

        schema = vol.Schema(
            {
                vol.Required(
                    "host",
                    default=(
                        user_input.get("host", DEFAULT_HOST)
                        if user_input
                        else DEFAULT_HOST
                    ),
                ): str,
                vol.Optional(
                    "recipients",
                    default=(
                        user_input.get("recipients", [])
                        if user_input
                        else []
                    ),
                ): selector.TextSelector(
                    selector.TextSelectorConfig(
                        type=selector.TextSelectorType.TEL,
                        multiple=True,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )
