
"""ZTE SMS integration for Home Assistant."""

from __future__ import annotations

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv

from .client import ZTEClient
from .const import DOMAIN

SERVICE_SEND_SMS = "send_sms"
PLATFORMS = ["notify"]

SEND_SMS_SCHEMA = vol.Schema(
    {
        vol.Required("number"): cv.string,
        vol.Required("message"): cv.string,
    }
)


async def async_setup(
    hass: HomeAssistant,
    config: dict,
) -> bool:
    """Set up the integration."""
    return True


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Set up ZTE SMS from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    host = entry.data["host"]
    client = ZTEClient(base_url=f"http://{host}")

    hass.data[DOMAIN][entry.entry_id] = client

    async def async_send_sms(call: ServiceCall) -> None:
        """Send an SMS when explicitly requested."""
        await client.send_sms(
            number=call.data["number"],
            message=call.data["message"],
        )

    if not hass.services.has_service(DOMAIN, SERVICE_SEND_SMS):
        hass.services.async_register(
            DOMAIN,
            SERVICE_SEND_SMS,
            async_send_sms,
            schema=SEND_SMS_SCHEMA,
        )

    await hass.config_entries.async_forward_entry_setups(
        entry,
        PLATFORMS,
    )

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Unload a ZTE SMS config entry."""
    if not await hass.config_entries.async_unload_platforms(
        entry,
        PLATFORMS,
    ):
        return False

    hass.data[DOMAIN].pop(entry.entry_id, None)

    if not hass.data[DOMAIN]:
        hass.services.async_remove(DOMAIN, SERVICE_SEND_SMS)

    return True
