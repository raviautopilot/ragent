"""Tests for command and script execution."""

from pathlib import Path
import shutil
import tempfile
import unittest

from ragent.executor import CommandExecutor
from ragent.logger import AgentLogger
from ragent.validator import ToolValidator


class TestCommandExecutor(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.logger = AgentLogger(log_dir=Path(self.temp_dir))
        self.executor = CommandExecutor(agent_logger=self.logger)
        self.validator = ToolValidator()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_run_command_success(self):
        status = self.validator.check_tool("bash")
        self.assertTrue(status.available)

        res = self.executor.run_command(status, "-c 'echo \"Hello from RAgent\"'")
        self.assertEqual(res.exit_code, 0)
        self.assertIn("Hello from RAgent", res.stdout)
        self.assertGreater(res.duration_seconds, 0)

    def test_run_script_success(self):
        status = self.validator.check_tool("bash")
        self.assertTrue(status.available)

        # Create temporary test script
        script_file = Path(self.temp_dir) / "test_script.sh"
        script_file.write_text("#!/bin/bash\necho 'Script executed: arg1='$1\n")
        script_file.chmod(0o755)

        res = self.executor.run_script(
            status, script_path=script_file, script_args=["alpha"]
        )
        self.assertEqual(res.exit_code, 0)
        self.assertIn("Script executed: arg1=alpha", res.stdout)

    def test_run_nonexistent_script(self):
        status = self.validator.check_tool("bash")
        res = self.executor.run_script(status, script_path="/tmp/nonexistent_12345.sh")
        self.assertEqual(res.exit_code, 2)
        self.assertIn("not found", res.stderr)

    def test_run_jq_command(self):
        status = self.validator.check_tool("jq")
        self.assertTrue(status.available)

        # Create temporary json
        json_file = Path(self.temp_dir) / "data.json"
        json_file.write_text('{"service": "ragent", "active": true}')

        res = self.executor.run_command(status, f".service {json_file}")
        self.assertEqual(res.exit_code, 0)
        self.assertIn('"ragent"', res.stdout)


if __name__ == "__main__":
    unittest.main()

