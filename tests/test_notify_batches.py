"""Mocked unit tests for sequential SMS notification batches."""

from __future__ import annotations

import asyncio
import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import AsyncMock, patch


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "custom_components.zte_sms"
INTEGRATION_DIR = ROOT / "custom_components" / "zte_sms"


def load_notify():
    """Load the real notify module with minimal Home Assistant stubs."""
    modules = {}

    def stub(name):
        module = types.ModuleType(name)
        modules[name] = module
        return module

    homeassistant = stub("homeassistant")
    homeassistant.__path__ = []
    components = stub("homeassistant.components")
    components.__path__ = []
    notify = stub("homeassistant.components.notify")
    notify.NotifyEntity = type("NotifyEntity", (), {})
    entries = stub("homeassistant.config_entries")
    entries.ConfigEntry = type("ConfigEntry", (), {})
    core = stub("homeassistant.core")
    core.HomeAssistant = type("HomeAssistant", (), {})
    helpers = stub("homeassistant.helpers")
    helpers.__path__ = []
    platform = stub("homeassistant.helpers.entity_platform")
    platform.AddEntitiesCallback = object

    package = stub(PACKAGE)
    package.__path__ = [str(INTEGRATION_DIR)]
    client = stub(f"{PACKAGE}.client")
    client.ZTEClient = type("ZTEClient", (), {})
    client.ZTESMSOutcomeUnknownError = type(
        "ZTESMSOutcomeUnknownError", (RuntimeError,), {}
    )
    const = stub(f"{PACKAGE}.const")
    const.DOMAIN = "zte_sms"
    const.CONF_BATCH_SIZE = "batch_size"
    const.DEFAULT_BATCH_SIZE = 5
    const.MIN_BATCH_SIZE = 1
    const.MAX_BATCH_SIZE = 5

    spec = importlib.util.spec_from_file_location(
        f"{PACKAGE}.notify", INTEGRATION_DIR / "notify.py"
    )
    module = importlib.util.module_from_spec(spec)
    modules[module.__name__] = module
    with patch.dict(sys.modules, modules):
        spec.loader.exec_module(module)
    return module, client.ZTESMSOutcomeUnknownError


class BatchTests(unittest.TestCase):
    """Exercise notifications without any real modem requests."""

    def setUp(self):
        self.module, self.UnknownError = load_notify()
        self.numbers = [f"+340000000{i:02d}" for i in range(11)]
        self.sent = []
        self.maintenance = []

    def make_entity(self, count=11, batch_size=None, failure=None):
        options = {}
        if batch_size is not None:
            options["batch_size"] = batch_size
        entry = types.SimpleNamespace(
            entry_id="entry-1",
            data={"recipients": self.numbers[:count]},
            options=options,
        )

        async def send_sms(number, message):
            self.sent.append(number)
            if failure is not None and number in failure:
                raise failure[number]
            return True

        entity = self.module.ZTESMSNotifyEntity(
            entry, types.SimpleNamespace(send_sms=send_sms, sms_lock=asyncio.Lock())
        )

        async def maintenance():
            self.maintenance.append(len(self.sent))

        entity._between_batches = maintenance
        return entity

    def run_send(self, entity):
        return asyncio.run(entity.async_send_message("Test message"))

    def test_default_batch_size_and_order(self):
        entity = self.make_entity()
        self.run_send(entity)
        self.assertEqual(self.sent, self.numbers)
        self.assertEqual(self.maintenance, [5, 10])

    def test_batch_sizes_one_to_five(self):
        for size in range(1, 6):
            with self.subTest(size=size):
                self.sent.clear()
                self.maintenance.clear()
                entity = self.make_entity(count=7, batch_size=size)
                self.run_send(entity)
                self.assertEqual(self.sent, self.numbers[:7])
                self.assertEqual(
                    self.maintenance, list(range(size, 7, size))
                )

    def test_invalid_stored_batch_sizes_fall_back_without_blocking(self):
        for invalid in (0, -2, 8, "abc", "3", 2.5, True, None):
            with self.subTest(invalid=invalid):
                self.sent.clear()
                self.maintenance.clear()
                entity = self.make_entity(count=11, batch_size=invalid)
                entity._entry.options["batch_size"] = invalid
                with self.assertLogs(self.module._LOGGER, level="WARNING") as logs:
                    self.run_send(entity)
                self.assertEqual(self.sent, self.numbers)
                self.assertEqual(self.maintenance, [5, 10])
                self.assertEqual(len(logs.output), 1)
                self.assertIn("using default value 5", logs.output[0])
                self.assertEqual(entity._entry.options["batch_size"], invalid)

    def test_success_does_not_raise(self):
        self.run_send(self.make_entity(count=3))
        self.assertEqual(len(self.sent), 3)

    def test_partial_failure_continues_and_classifies(self):
        failures = {
            self.numbers[1]: ValueError("invalid"),
            self.numbers[3]: self.UnknownError("timeout"),
        }
        entity = self.make_entity(count=6, batch_size=2, failure=failures)
        with self.assertLogs(self.module._LOGGER, level="WARNING") as logs:
            with self.assertRaises(self.module.SMSBatchError) as caught:
                self.run_send(entity)
        self.assertEqual(len(logs.output), 2)
        self.assertIn("recipient validation failed", logs.output[0])
        self.assertIn("submission outcome unknown", logs.output[1])
        for record in logs.output:
            self.assertNotIn("+340", record)
            self.assertNotIn("Test message", record)
        result = caught.exception.result
        self.assertEqual(result.status, "partial_failure")
        self.assertEqual((result.total, result.accepted, result.rejected, result.unknown), (6, 4, 1, 1))
        self.assertEqual(self.sent, self.numbers[:6])
        self.assertEqual(self.maintenance, [2, 4])
        self.assertNotIn(self.numbers[1], str(caught.exception))

    def test_complete_failure(self):
        failures = {
            self.numbers[0]: ValueError("invalid"),
            self.numbers[1]: self.UnknownError("timeout"),
        }
        entity = self.make_entity(count=2, failure=failures)
        with self.assertRaises(self.module.SMSBatchError) as caught:
            self.run_send(entity)
        self.assertEqual(caught.exception.result.status, "complete_failure")
        self.assertEqual(caught.exception.result.accepted, 0)

    def test_unexpected_failure_is_unknown_and_processing_continues(self):
        entity = self.make_entity(
            count=3, failure={self.numbers[0]: RuntimeError("unexpected")}
        )
        with self.assertLogs(self.module._LOGGER, level="ERROR") as logs:
            with self.assertRaises(self.module.SMSBatchError) as caught:
                self.run_send(entity)
        self.assertEqual(len(logs.output), 1)
        self.assertIn("Unexpected error", logs.output[0])
        self.assertNotIn("+340", logs.output[0])
        self.assertNotIn("Test message", logs.output[0])
        self.assertNotIn("unexpected)", logs.output[0])
        self.assertEqual(caught.exception.result.unknown, 1)
        self.assertEqual(self.sent, self.numbers[:3])

    def test_maintenance_failure_does_not_interrupt_batches(self):
        entity = self.make_entity(count=7, batch_size=3)

        async def failed_maintenance():
            self.maintenance.append(len(self.sent))
            raise RuntimeError("simulated maintenance failure")

        entity._between_batches = failed_maintenance
        with self.assertLogs(self.module._LOGGER, level="WARNING") as captured:
            self.run_send(entity)
        self.assertEqual(self.sent, self.numbers[:7])
        self.assertEqual(self.maintenance, [3, 6])
        self.assertEqual(len(captured.output), 2)
        self.assertNotIn(self.numbers[0], " ".join(captured.output))

    def test_concurrent_notifications_are_serialized(self):
        """A second notification waits for the first batch operation."""
        async def scenario():
            first_started = asyncio.Event()
            release_first = asyncio.Event()
            calls = []

            async def send_sms(number, message):
                calls.append((message, number))
                if message == "A" and number == self.numbers[0]:
                    first_started.set()
                    await release_first.wait()
                return True

            entry = types.SimpleNamespace(
                entry_id="entry-1",
                data={"recipients": self.numbers[:2]},
                options={"batch_size": 2},
            )
            entity = self.module.ZTESMSNotifyEntity(
                entry, types.SimpleNamespace(send_sms=send_sms, sms_lock=asyncio.Lock())
            )
            first = asyncio.create_task(entity.async_send_message("A"))
            await asyncio.wait_for(first_started.wait(), timeout=1)
            second = asyncio.create_task(entity.async_send_message("B"))
            await asyncio.sleep(0)
            self.assertEqual(calls, [("A", self.numbers[0])])
            release_first.set()
            await asyncio.wait_for(asyncio.gather(first, second), timeout=1)
            return calls

        calls = asyncio.run(scenario())
        self.assertEqual(
            calls,
            [
                ("A", self.numbers[0]),
                ("A", self.numbers[1]),
                ("B", self.numbers[0]),
                ("B", self.numbers[1]),
            ],
        )

    def test_empty_recipients(self):
        with self.assertRaisesRegex(ValueError, "No default SMS recipients"):
            self.run_send(self.make_entity(count=0))


if __name__ == "__main__":
    unittest.main()
