
"""Unit tests for the ZTE SMS service lifecycle.

Home Assistant and modem communication are mocked. No live SMS is sent.
"""

from __future__ import annotations

import asyncio
import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import AsyncMock, Mock, patch


ROOT = Path(__file__).resolve().parents[1]
INTEGRATION_DIR = ROOT / "custom_components" / "zte_sms"
MODULE_NAME = "custom_components.zte_sms"
DOMAIN = "zte_sms"


class FakeServices:
    """Minimal Home Assistant service registry."""

    def __init__(self):
        self.registered = {}

    def has_service(self, domain, service):
        return (domain, service) in self.registered

    def async_register(self, domain, service, handler, schema=None):
        self.registered[(domain, service)] = handler

    def async_remove(self, domain, service):
        self.registered.pop((domain, service), None)

    async def send(self, number, message):
        handler = self.registered[(DOMAIN, "send_sms")]
        await handler(
            types.SimpleNamespace(
                data={"number": number, "message": message}
            )
        )


class FakeHass:
    """Minimal Home Assistant instance."""

    def __init__(self):
        self.data = {}
        self.services = FakeServices()
        self.config_entries = types.SimpleNamespace(
            async_forward_entry_setups=AsyncMock(),
            async_unload_platforms=AsyncMock(return_value=True),
        )


def fake_entry(entry_id="entry-1", host="192.168.0.1"):
    """Create a simulated configuration entry."""
    return types.SimpleNamespace(
        entry_id=entry_id,
        data={"host": host},
    )


def load_integration():
    """Import the integration with Home Assistant dependencies mocked."""
    modules = {}

    def module(name):
        result = types.ModuleType(name)
        modules[name] = result
        return result

    voluptuous = module("voluptuous")
    voluptuous.Required = lambda key: key
    voluptuous.Schema = lambda schema: schema

    homeassistant = module("homeassistant")
    homeassistant.__path__ = []

    config_entries = module("homeassistant.config_entries")
    config_entries.ConfigEntry = type("ConfigEntry", (), {})

    core = module("homeassistant.core")
    core.HomeAssistant = type("HomeAssistant", (), {})
    core.ServiceCall = type("ServiceCall", (), {})

    helpers = module("homeassistant.helpers")
    helpers.__path__ = []

    config_validation = module(
        "homeassistant.helpers.config_validation"
    )
    config_validation.string = str
    helpers.config_validation = config_validation

    package = module(MODULE_NAME)
    package.__path__ = [str(INTEGRATION_DIR)]

    client_module = module(f"{MODULE_NAME}.client")
    client_module.ZTEClient = Mock()

    const_module = module(f"{MODULE_NAME}.const")
    const_module.DOMAIN = DOMAIN

    spec = importlib.util.spec_from_file_location(
        MODULE_NAME,
        INTEGRATION_DIR / "__init__.py",
        submodule_search_locations=[str(INTEGRATION_DIR)],
    )

    integration = importlib.util.module_from_spec(spec)
    modules[MODULE_NAME] = integration

    with patch.dict(sys.modules, modules):
        spec.loader.exec_module(integration)

    return integration, client_module.ZTEClient


class ServiceLifecycleTests(unittest.TestCase):
    """Test configuration-entry and service lifecycle behavior."""

    def setUp(self):
        self.integration, self.client_factory = load_integration()
        self.hass = FakeHass()
        self.entry = fake_entry()

        self.client = Mock()
        self.client.send_sms = AsyncMock(return_value=True)
        self.client.sms_lock = asyncio.Lock()
        self.client_factory.return_value = self.client

    def run_async(self, coroutine):
        return asyncio.run(coroutine)

    def test_setup_registers_service(self):
        result = self.run_async(
            self.integration.async_setup_entry(self.hass, self.entry)
        )

        self.assertTrue(result)
        self.client_factory.assert_called_once_with(
            base_url="http://192.168.0.1"
        )
        self.assertTrue(
            self.hass.services.has_service(DOMAIN, "send_sms")
        )
        self.assertIs(
            self.hass.data[DOMAIN][self.entry.entry_id],
            self.client,
        )

    def test_service_uses_active_client(self):
        self.run_async(
            self.integration.async_setup_entry(self.hass, self.entry)
        )

        self.run_async(
            self.hass.services.send(
                "+34000000000",
                "Test message",
            )
        )

        self.client.send_sms.assert_awaited_once_with(
            number="+34000000000",
            message="Test message",
        )

    def test_second_modem_is_rejected(self):
        self.run_async(
            self.integration.async_setup_entry(self.hass, self.entry)
        )

        second_entry = fake_entry(
            entry_id="entry-2",
            host="192.168.0.2",
        )

        with self.assertRaises(RuntimeError):
            self.run_async(
                self.integration.async_setup_entry(
                    self.hass,
                    second_entry,
                )
            )

        self.assertEqual(len(self.hass.data[DOMAIN]), 1)
        self.client_factory.assert_called_once()

    def test_unload_removes_service(self):
        self.run_async(
            self.integration.async_setup_entry(self.hass, self.entry)
        )

        result = self.run_async(
            self.integration.async_unload_entry(
                self.hass,
                self.entry,
            )
        )

        self.assertTrue(result)
        self.assertFalse(
            self.hass.services.has_service(DOMAIN, "send_sms")
        )
        self.assertEqual(self.hass.data[DOMAIN], {})

    def test_failed_unload_preserves_service(self):
        self.run_async(
            self.integration.async_setup_entry(self.hass, self.entry)
        )
        self.hass.config_entries.async_unload_platforms.return_value = False

        result = self.run_async(
            self.integration.async_unload_entry(
                self.hass,
                self.entry,
            )
        )

        self.assertFalse(result)
        self.assertTrue(
            self.hass.services.has_service(DOMAIN, "send_sms")
        )
        self.assertIn(self.entry.entry_id, self.hass.data[DOMAIN])

    def test_failed_platform_setup_restores_state(self):
        self.hass.config_entries.async_forward_entry_setups.side_effect = (
            RuntimeError("Simulated platform setup failure")
        )

        with self.assertRaises(RuntimeError):
            self.run_async(
                self.integration.async_setup_entry(
                    self.hass,
                    self.entry,
                )
            )

        self.assertEqual(self.hass.data[DOMAIN], {})
        self.assertFalse(
            self.hass.services.has_service(DOMAIN, "send_sms")
        )

    def test_service_uses_new_client_after_reload(self):
        self.run_async(
            self.integration.async_setup_entry(self.hass, self.entry)
        )
        self.run_async(
            self.integration.async_unload_entry(self.hass, self.entry)
        )

        new_client = Mock()
        new_client.send_sms = AsyncMock(return_value=True)
        new_client.sms_lock = asyncio.Lock()
        self.client_factory.return_value = new_client

        self.run_async(
            self.integration.async_setup_entry(self.hass, self.entry)
        )
        self.run_async(
            self.hass.services.send(
                "+34000000000",
                "After reload",
            )
        )

        self.client.send_sms.assert_not_awaited()
        new_client.send_sms.assert_awaited_once_with(
            number="+34000000000",
            message="After reload",
        )


if __name__ == "__main__":
    unittest.main()
