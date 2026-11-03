"""Tests for tool validation and environment checks."""

import unittest

from ragent.validator import ToolValidator


class TestToolValidator(unittest.TestCase):

    def setUp(self):
        self.validator = ToolValidator()

    def test_bash_is_available(self):
        status = self.validator.check_tool("bash")
        self.assertTrue(status.available)
        self.assertIsNotNone(status.path)
        self.assertIn("bash", status.path)

    def test_jq_is_available(self):
        status = self.validator.check_tool("jq")
        self.assertTrue(status.available)
        self.assertIsNotNone(status.path)

    def test_nonexistent_tool_returns_remediation(self):
        status = self.validator.check_tool("definitely_nonexistent_tool_12345")
        self.assertFalse(status.available)
        self.assertIsNone(status.path)
        self.assertIn("was not found in PATH", status.remediation_hint)

    def test_catalog_missing_tool_hint(self):
        # vault might or might not be installed, test that definition exists
        self.assertIn("vault", self.validator.catalog)
        self.assertIn("openshift", self.validator.catalog)
        self.assertIn("zsh", self.validator.catalog)

    def test_list_all_tools(self):
        tools = self.validator.list_all_tools()
        names = [t.name for t in tools]
        self.assertIn("bash", names)
        self.assertIn("jq", names)
        self.assertIn("vault", names)
        self.assertIn("openshift", names)


if __name__ == "__main__":
    unittest.main()

