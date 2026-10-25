import asyncio
from datetime import datetime
from zoneinfo import ZoneInfo
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError
from io import BytesIO
from urllib.parse import parse_qs

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "custom_components" / "zte_sms"))

from client import (ZTEClient, ZTEAPIError, ZTESMSRejectedError,
                    ZTESMSOutcomeUnknownError, decode_sms, encode_sms, sms_timestamp)


class ClientTests(unittest.TestCase):
    def test_unicode_roundtrip(self):
        message = "Prueba áéíóú ñ"
        self.assertEqual(encode_sms(message), "005000720075006500620061002000E100E900ED00F300FA002000F1")
        self.assertEqual(decode_sms(encode_sms(message)), message)

    def test_timestamp(self):
        dt = datetime(2026, 10, 24, 16, 3, 44, tzinfo=ZoneInfo("Europe/Madrid"))
        self.assertEqual(sms_timestamp(dt), "26;10;24;16;03;44;+2")

    def test_send_is_mocked(self):
        client = ZTEClient()
        def fake_request(endpoint, params, *, post):
            self.assertTrue(post)
            self.assertEqual(params["goformId"], "SEND_SMS")
            self.assertEqual(params["encode_type"], "UNICODE")
            self.assertEqual(params["MessageBody"], encode_sms("áéíóú ñ"))
            return {"result": "success"}
        with patch.object(client, "_request", side_effect=fake_request):
            self.assertTrue(asyncio.run(client.send_sms("+34000000000", "áéíóú ñ")))

    def test_read_is_mocked(self):
        client = ZTEClient()
        def fake_request(endpoint, params, *, post):
            self.assertFalse(post)
            self.assertIn("_", params)
            self.assertEqual(params["cmd"], "sms_data_total")
            return {"messages": [{"id": "1", "content": encode_sms("Prueba")}]}
        with patch.object(client, "_request", side_effect=fake_request):
            self.assertEqual(asyncio.run(client.get_messages())[0]["text"], "Prueba")

    def test_empty_read_is_valid(self):
        client = ZTEClient()
        with patch.object(client, "_request", return_value={"messages": []}):
            self.assertEqual(asyncio.run(client.get_messages()), [])

    def test_send_failure(self):
        client = ZTEClient()
        with patch.object(client, "_request", return_value={"result": "failure"}):
            with self.assertRaises(ZTEAPIError):
                asyncio.run(client.send_sms("+34000000000", "Prueba"))


    def test_non_success_responses_have_unknown_outcome(self):
        for response in ({"result": "failure"}, {"result": "unexpected"}, {}, {"result": None}):
            with self.subTest(response=response):
                client = ZTEClient()
                with patch.object(client, "_request", return_value=response) as request:
                    with self.assertRaises(ZTESMSOutcomeUnknownError):
                        asyncio.run(client.send_sms("+34000000000", "Prueba"))
                    self.assertEqual(request.call_count, 1)

    def test_transport_and_response_errors_have_unknown_outcome(self):
        errors = (
            ZTEAPIError("Modem HTTP request failed or returned invalid JSON"),
            ZTEAPIError("Unexpected modem response format"),
        )
        for error in errors:
            with self.subTest(error=str(error)):
                client = ZTEClient()
                with patch.object(client, "_request", side_effect=error) as request:
                    with self.assertRaises(ZTESMSOutcomeUnknownError) as raised:
                        asyncio.run(client.send_sms("+34000000000", "Prueba"))
                    self.assertIs(raised.exception.__cause__, error)
                    self.assertEqual(request.call_count, 1)

    def test_http_timeout_and_bad_json_are_unknown(self):
        class FakeResponse:
            def __init__(self, payload):
                self.payload = payload
            def __enter__(self):
                return self
            def __exit__(self, *args):
                return False
            def read(self):
                return self.payload

        cases = (
            TimeoutError("timed out"),
            URLError("connection lost"),
            HTTPError("http://modem", 500, "error", {}, BytesIO(b"")),
            FakeResponse(b"not json"),
            FakeResponse(b"[]"),
            FakeResponse(b""),
        )
        for case in cases:
            with self.subTest(case=type(case).__name__):
                client = ZTEClient()
                with patch("client.urlopen", side_effect=case if isinstance(case, Exception) else None,
                           return_value=case if not isinstance(case, Exception) else None) as request:
                    with self.assertRaises(ZTESMSOutcomeUnknownError):
                        asyncio.run(client.send_sms("+34000000000", "Prueba"))
                    self.assertEqual(request.call_count, 1)

    def test_invalid_input_never_calls_modem(self):
        client = ZTEClient()
        with patch.object(client, "_request") as request:
            for number, message in (("123", "Prueba"), ("+34abc", "Prueba"),
                                    ("+34000000000", "")):
                with self.subTest(number=number, message=message):
                    with self.assertRaises(ValueError):
                        asyncio.run(client.send_sms(number, message))
            request.assert_not_called()

    def test_error_types_remain_api_errors(self):
        self.assertTrue(issubclass(ZTESMSOutcomeUnknownError, ZTEAPIError))
        self.assertTrue(issubclass(ZTESMSRejectedError, ZTEAPIError))
        self.assertNotEqual(ZTESMSRejectedError, ZTESMSOutcomeUnknownError)


if __name__ == "__main__":
    unittest.main()
