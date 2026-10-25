"""SMS notification entity for ZTE SMS."""

from __future__ import annotations

from dataclasses import dataclass
import logging

from homeassistant.components.notify import NotifyEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .client import ZTEClient, ZTESMSOutcomeUnknownError
from .const import (
    CONF_BATCH_SIZE,
    DEFAULT_BATCH_SIZE,
    DOMAIN,
    MAX_BATCH_SIZE,
    MIN_BATCH_SIZE,
)

_LOGGER = logging.getLogger(__name__)


@dataclass
class SMSBatchResult:
    """Results for a single multi-recipient notification operation."""

    total: int = 0
    accepted: int = 0
    rejected: int = 0
    unknown: int = 0

    @property
    def status(self) -> str:
        """Classify the complete operation by confirmed modem acceptance."""
        if self.accepted == self.total:
            return "success"
        if self.accepted == 0:
            return "complete_failure"
        return "partial_failure"


class SMSBatchError(RuntimeError):
    """One or more recipients lacked confirmed SMS acceptance."""

    def __init__(self, result: SMSBatchResult) -> None:
        """Expose counts without leaking phone numbers or message contents."""
        self.result = result
        super().__init__(
            f"ZTE SMS {result.status}: {result.accepted}/{result.total} accepted, "
            f"{result.rejected} rejected, {result.unknown} unknown"
        )


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

    async def _between_batches(self) -> None:
        """Reserved for future safe modem maintenance; currently a no-op."""

    async def async_send_message(
        self,
        message: str,
        title: str | None = None,
    ) -> None:
        """Send sequential batches, continuing after individual SMS failures."""
        recipients = self._entry.options.get(
            "recipients",
            self._entry.data.get("recipients", []),
        )

        if not recipients:
            raise ValueError("No default SMS recipients configured")

        result = SMSBatchResult(total=len(recipients))
        # These lists exist only for this operation; never log their contents.
        rejected_numbers: list[str] = []
        unknown_numbers: list[str] = []

        batch_size = self._entry.options.get(CONF_BATCH_SIZE, DEFAULT_BATCH_SIZE)
        if (
            type(batch_size) is not int
            or not MIN_BATCH_SIZE <= batch_size <= MAX_BATCH_SIZE
        ):
            _LOGGER.warning(
                "Invalid SMS batch size configuration; using default value %d",
                DEFAULT_BATCH_SIZE,
            )
            batch_size = DEFAULT_BATCH_SIZE

        for start in range(0, len(recipients), batch_size):
            if start:
                try:
                    await self._between_batches()
                except Exception:
                    # Maintenance failures must not interrupt SMS submissions.
                    _LOGGER.warning(
                        "ZTE SMS maintenance between batches failed; continuing",
                    )

            for number in recipients[start : start + batch_size]:
                try:
                    await self._client.send_sms(number, message)
                except ValueError:
                    # Validation happens before the modem request.
                    result.rejected += 1
                    rejected_numbers.append(number)
                except ZTESMSOutcomeUnknownError:
                    result.unknown += 1
                    unknown_numbers.append(number)
                except Exception:
                    # Unexpected failures must not stop remaining recipients.
                    # Their submission outcome cannot be assumed.
                    result.unknown += 1
                    unknown_numbers.append(number)
                else:
                    result.accepted += 1

        if result.status != "success":
            raise SMSBatchError(result)
