
"""Configuration flow for ZTE SMS."""

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers import selector

from .const import DOMAIN, DEFAULT_HOST


def validate_recipients(recipients: list[str]) -> list[str]:
    """Validate and deduplicate phone numbers."""
    numbers = [number.strip() for number in recipients if number.strip()]

    if any(
        not number.startswith("+") or not number[1:].isdigit()
        for number in numbers
    ):
        raise ValueError("invalid_phone_number")

    return list(dict.fromkeys(numbers))


def recipients_schema(default: list[str] | None = None):
    """Build the recipient selector."""
    return vol.Optional(
        "recipients",
        default=default if default is not None else [],
    )


class ZTESMSConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the ZTE SMS configuration flow."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Configure the modem and default recipients."""
        # Only one modem is supported per Home Assistant installation.
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        errors = {}

        if user_input is not None:
            host = user_input["host"].strip()

            try:
                recipients = validate_recipients(
                    user_input.get("recipients", [])
                )
            except ValueError:
                errors["base"] = "invalid_phone_number"
            else:
                await self.async_set_unique_id(host)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"ZTE SMS ({host})",
                    data={
                        "host": host,
                        "recipients": recipients,
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
                recipients_schema(
                    user_input.get("recipients", [])
                    if user_input
                    else []
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

    @staticmethod
    def async_get_options_flow(config_entry):
        """Return the options flow."""
        return ZTESMSOptionsFlow()


class ZTESMSOptionsFlow(config_entries.OptionsFlow):
    """Manage default SMS recipients."""

    async def async_step_init(self, user_input=None):
        """Configure default recipients."""
        errors = {}

        if user_input is not None:
            try:
                recipients = validate_recipients(
                    user_input.get("recipients", [])
                )
            except ValueError:
                errors["base"] = "invalid_phone_number"
            else:
                return self.async_create_entry(
                    title="",
                    data={"recipients": recipients},
                )

        current_recipients = self.config_entry.options.get(
            "recipients",
            self.config_entry.data.get("recipients", []),
        )

        schema = vol.Schema(
            {
                recipients_schema(
                    user_input.get("recipients", current_recipients)
                    if user_input
                    else current_recipients
                ): selector.TextSelector(
                    selector.TextSelectorConfig(
                        type=selector.TextSelectorType.TEL,
                        multiple=True,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=schema,
            errors=errors,
        )
