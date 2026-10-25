"""Regression checks for Home Assistant options schema compatibility.

These checks run without Home Assistant dependencies. Real serializer validation
must still be performed in a Home Assistant environment.
"""

from __future__ import annotations

import ast
from pathlib import Path
import unittest


CONFIG_FLOW = (
    Path(__file__).resolve().parents[1]
    / "custom_components"
    / "zte_sms"
    / "config_flow.py"
)


class OptionsSchemaTests(unittest.TestCase):
    """Prevent non-serializable custom validators in the options schema."""

    def test_batch_size_field_uses_supported_voluptuous_validators(self):
        tree = ast.parse(CONFIG_FLOW.read_text(encoding="utf-8"))
        options_class = next(
            node for node in tree.body
            if isinstance(node, ast.ClassDef)
            and node.name == "ZTESMSOptionsFlow"
        )
        step = next(
            node for node in options_class.body
            if isinstance(node, ast.AsyncFunctionDef)
            and node.name == "async_step_init"
        )
        schemas = [
            node for node in ast.walk(step)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "Schema"
        ]
        self.assertEqual(len(schemas), 1)
        schema_fields = schemas[0].args[0]
        self.assertIsInstance(schema_fields, ast.Dict)
        batch_validator = next(
            value for key, value in zip(schema_fields.keys, schema_fields.values)
            if isinstance(key, ast.Call)
            and isinstance(key.func, ast.Attribute)
            and key.func.attr == "Required"
            and key.args
            and isinstance(key.args[0], ast.Name)
            and key.args[0].id == "CONF_BATCH_SIZE"
        )
        self.assertIsInstance(batch_validator, ast.Call)
        self.assertIsInstance(batch_validator.func, ast.Attribute)
        self.assertEqual(batch_validator.func.attr, "All")
        validators = [
            call.func.attr for call in batch_validator.args
            if isinstance(call, ast.Call)
            and isinstance(call.func, ast.Attribute)
        ]
        self.assertEqual(validators, ["Coerce", "Range"])

    def test_strict_input_validation_is_retained(self):
        tree = ast.parse(CONFIG_FLOW.read_text(encoding="utf-8"))
        step = next(
            node for cls in tree.body
            if isinstance(cls, ast.ClassDef)
            and cls.name == "ZTESMSOptionsFlow"
            for node in cls.body
            if isinstance(node, ast.AsyncFunctionDef)
            and node.name == "async_step_init"
        )
        self.assertTrue(any(
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "validate_batch_size"
            for node in ast.walk(step)
        ))


if __name__ == "__main__":
    unittest.main()
