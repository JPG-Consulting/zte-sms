"""Offline unit tests with synthetic, non-sensitive content."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "custom_components"))
from zte_sms.encoding import decode_sms_hex


class DecodeSmsHexTests(unittest.TestCase):
    def test_simple_text(self):
        self.assertEqual(decode_sms_hex("005000720075006500620061"), "Prueba")

    def test_non_bmp_character(self):
        self.assertEqual(decode_sms_hex("D83DDE00"), "😀")

    def test_empty(self):
        self.assertEqual(decode_sms_hex(""), "")

    def test_malformed(self):
        for invalid in ("XYZ", "0", "D800", "00"):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    decode_sms_hex(invalid)


if __name__ == "__main__":
    unittest.main()
