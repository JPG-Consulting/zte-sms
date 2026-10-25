"""Experimental, dependency-free async client for the ZTE MF833U1 HTTP API.

No requests are made on import. Sending an SMS is an explicit operation.
"""
from __future__ import annotations

import asyncio
from datetime import datetime
import json
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo


class ZTEAPIError(RuntimeError):
    """The modem could not complete an API operation."""


class ZTESMSRejectedError(ZTEAPIError):
    """SMS submission was definitively rejected (no verified cases yet)."""


class ZTESMSOutcomeUnknownError(ZTEAPIError):
    """SMS submission may have been processed; do not retry automatically."""


def encode_sms(text: str) -> str:
    return text.encode("utf-16-be").hex().upper()


def decode_sms(value: str) -> str:
    return bytes.fromhex(value).decode("utf-16-be")


def sms_timestamp(now: datetime | None = None, timezone: str = "Europe/Madrid") -> str:
    """Format observed timestamp; timezone semantics require further validation."""
    current = (now or datetime.now(ZoneInfo(timezone)))
    if current.tzinfo is None:
        raise ValueError("now must have timezone information")
    current = current.astimezone(ZoneInfo(timezone))
    offset = current.utcoffset()
    if offset is None or offset.total_seconds() % 3600:
        raise ValueError("Observed modem timestamp only supports whole-hour offsets")
    hours = int(offset.total_seconds() // 3600)
    return current.strftime("%y;%m;%d;%H;%M;%S;") + f"{hours:+d}"


class ZTEClient:
    def __init__(self, base_url: str = "http://192.168.0.1", timeout: float = 10.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _request(self, endpoint: str, params: dict[str, str], *, post: bool) -> dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        data = urlencode(params).encode("utf-8") if post else None
        if not post:
            url += "?" + urlencode(params)
        headers = {
            "Referer": f"{self.base_url}/index.html",
            "X-Requested-With": "XMLHttpRequest",
            "Accept": "application/json, text/javascript, */*; q=0.01",
        }
        if post:
            headers["Content-Type"] = "application/x-www-form-urlencoded; charset=UTF-8"
        request = Request(url, data=data, headers=headers, method="POST" if post else "GET")
        try:
            with urlopen(request, timeout=self.timeout) as response:
                payload = response.read().decode("utf-8")
            result = json.loads(payload)
        except (HTTPError, URLError, TimeoutError, UnicodeError, ValueError) as exc:
            raise ZTEAPIError("Modem HTTP request failed or returned invalid JSON") from exc
        if not isinstance(result, dict):
            raise ZTEAPIError("Unexpected modem response format")
        return result

    async def send_sms(self, number: str, message: str) -> bool:
        """Send one real SMS. Call only after explicit user authorization."""
        if not number or not number.startswith("+") or not number[1:].isdigit():
            raise ValueError("Use an international phone number, e.g. +34000000000")
        if not message:
            raise ValueError("SMS text cannot be empty")
        params = {
            "isTest": "false",
            "goformId": "SEND_SMS",
            "notCallback": "true",
            "Number": number,
            "sms_time": sms_timestamp(),
            "MessageBody": encode_sms(message),
            "ID": "-1",
            "encode_type": "UNICODE",
        }
        try:
            response = await asyncio.to_thread(
                self._request, "/goform/goform_set_cmd_process", params, post=True
            )
        except ZTEAPIError as exc:
            raise ZTESMSOutcomeUnknownError(
                "SMS outcome unknown after modem request; do not retry automatically"
            ) from exc
        if response.get("result") != "success":
            # No non-success response is yet verified as a definitive rejection.
            raise ZTESMSOutcomeUnknownError(
                "Modem did not confirm SMS submission; outcome unknown"
            )
        return True  # Initial submission success, NOT final status or delivery.

    async def get_messages(self) -> list[dict[str, Any]]:
        """Read SMS once; this method does not schedule polling."""
        params = {
            "isTest": "false",
            "cmd": "sms_data_total",
            "page": "0",
            "data_per_page": "500",
            "mem_store": "1",
            "tags": "10",
            "order_by": "order by id desc",
            "_": str(time.time_ns() // 1_000_000),
        }
        response = await asyncio.to_thread(
            self._request, "/goform/goform_get_cmd_process", params, post=False
        )
        messages = response.get("messages")
        if not isinstance(messages, list):
            raise ZTEAPIError("Modem response does not contain a messages list")
        decoded = []
        for item in messages:
            if not isinstance(item, dict):
                raise ZTEAPIError("Malformed SMS entry")
            record = dict(item)
            if isinstance(record.get("content"), str):
                try:
                    record["text"] = decode_sms(record["content"])
                except (ValueError, UnicodeError) as exc:
                    raise ZTEAPIError("Malformed SMS text encoding") from exc
            decoded.append(record)
        return decoded
