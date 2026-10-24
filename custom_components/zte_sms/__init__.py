
"""ZTE SMS integration for Home Assistant."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN


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
    hass.data[DOMAIN][entry.entry_id] = {
        "host": entry.data["host"],
    }

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Unload a ZTE SMS config entry."""
    hass.data[DOMAIN].pop(entry.entry_id, None)
    return True
