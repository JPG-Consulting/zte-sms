
"""SMS notification entity for ZTE SMS."""

from __future__ import annotations

from homeassistant.components.notify import NotifyEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .client import ZTEClient
from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the SMS notification entity."""
    client = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([ZTESMSNotifyEntity(entry, client)])


class ZTESMSNotifyEntity(NotifyEntity):
    """Send SMS notifications through the ZTE modem."""

    _attr_name = "ZTE SMS"
    _attr_unique_id = None

    def __init__(self, entry: ConfigEntry, client: ZTEClient) -> None:
        """Initialize the notification entity."""
        self._entry = entry
        self._client = client
        self._attr_unique_id = f"{entry.entry_id}_notify"

    async def async_send_message(
        self,
        message: str,
        title: str | None = None,
    ) -> None:
        """Send an SMS to every configured default recipient."""
        recipients = self._entry.options.get(
            "recipients",
            self._entry.data.get("recipients", []),
        )

        if not recipients:
            raise ValueError("No default SMS recipients configured")

        for number in recipients:
            await self._client.send_sms(number, message)
