
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
    clients = hass.data.setdefault(DOMAIN, {})

    # Only one modem can be active at a time.
    if clients and entry.entry_id not in clients:
        raise RuntimeError(
            "ZTE SMS supports only one modem configuration"
        )

    host = entry.data["host"]
    client = ZTEClient(base_url=f"http://{host}")

    # Forward the platform before publishing the new client.
    # The notify platform retrieves its client from hass.data,
    # so make it available temporarily during setup.
    previous_client = clients.get(entry.entry_id)
    clients[entry.entry_id] = client

    try:
        await hass.config_entries.async_forward_entry_setups(
            entry,
            PLATFORMS,
        )
    except Exception:
        # Restore the previous state if platform setup fails.
        if previous_client is None:
            clients.pop(entry.entry_id, None)
        else:
            clients[entry.entry_id] = previous_client
        raise

    async def async_send_sms(call: ServiceCall) -> None:
        """Send an SMS using the currently active modem."""
        active_clients = hass.data.get(DOMAIN, {})

        if len(active_clients) != 1:
            raise RuntimeError(
                "ZTE SMS requires exactly one active modem"
            )

        active_client = next(iter(active_clients.values()))

        await active_client.send_sms(
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

    clients = hass.data.get(DOMAIN, {})
    clients.pop(entry.entry_id, None)

    if not clients and hass.services.has_service(
        DOMAIN,
        SERVICE_SEND_SMS,
    ):
        hass.services.async_remove(
            DOMAIN,
            SERVICE_SEND_SMS,
        )

    return True
