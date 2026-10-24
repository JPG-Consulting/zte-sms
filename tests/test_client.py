import asyncio
from datetime import datetime
from zoneinfo import ZoneInfo
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs

from zte_client import ZTEClient, ZTEAPIError, decode_sms, encode_sms, sms_timestamp


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


if __name__ == "__main__":
    unittest.main()
