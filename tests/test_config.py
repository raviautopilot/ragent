"""Tests for centralized constants and configuration."""

import os
from pathlib import Path
import unittest

from ragent.config import get_constants


class TestAgentConfig(unittest.TestCase):

    def test_default_constants(self):
        cfg = get_constants()
        self.assertIsNotNone(cfg.scripts_dir)
        self.assertIn("openshift", str(cfg.oc_path))
        self.assertTrue(str(cfg.oc_login_script).endswith("ocLogin.sh"))
        self.assertIn("vault", str(cfg.vault_path))
        self.assertTrue(str(cfg.vault_login_script).endswith("vaultLogin.sh"))

    def test_shortcuts_registered(self):
        cfg = get_constants()
        oc_shortcut = cfg.get_shortcut("oc-login")
        self.assertIsNotNone(oc_shortcut)
        self.assertEqual(oc_shortcut["tool"], "bash")
        self.assertIn("ocLogin.sh", oc_shortcut["script"])

        vault_shortcut = cfg.get_shortcut("vault-login")
        self.assertIsNotNone(vault_shortcut)
        self.assertEqual(vault_shortcut["tool"], "bash")
        self.assertIn("vaultLogin.sh", vault_shortcut["script"])

    def test_env_overrides(self):
        custom_oc = "/custom/path/to/ocLogin.sh"
        custom_vault = "/custom/vault/dir"

        try:
            os.environ["OC_LOGIN_SCRIPT"] = custom_oc
            os.environ["VAULT_PATH"] = custom_vault

            cfg = get_constants()
            self.assertEqual(str(cfg.oc_login_script), custom_oc)
            self.assertEqual(str(cfg.vault_path), custom_vault)
            self.assertEqual(
                str(cfg.vault_login_script), "/custom/vault/dir/vaultLogin.sh"
            )
        finally:
            os.environ.pop("OC_LOGIN_SCRIPT", None)
            os.environ.pop("VAULT_PATH", None)


if __name__ == "__main__":
    unittest.main()

