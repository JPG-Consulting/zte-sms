"""Pure decoding helper for research fixtures; not a Home Assistant integration yet."""


def decode_sms_hex(value: str) -> str:
    """Decode a ZTE SMS content field containing UTF-16-BE hexadecimal text.

    Raises ValueError for malformed hex/UTF-16 input.
    """
    if not isinstance(value, str):
        raise ValueError("SMS content must be a string")
    try:
        return bytes.fromhex(value).decode("utf-16-be")
    except (ValueError, UnicodeError) as exc:
        raise ValueError("Invalid UTF-16 hexadecimal SMS content") from exc
