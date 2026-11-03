"""Tests for timestamped logging system."""

from pathlib import Path
import re
import shutil
import tempfile
import unittest

from ragent.logger import AgentLogger


class TestAgentLogger(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.logger = AgentLogger(log_dir=Path(self.temp_dir))

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_timestamp_format(self):
        ts = self.logger._get_timestamp()
        # Format: YYYY-MM-DD HH:MM:SS.mmm
        pattern = r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}$"
        self.assertRegex(ts, pattern)

    def test_log_file_creation(self):
        self.logger.info("Test informative message")
        self.logger.debug("Test debug message")

        self.assertTrue(self.logger.session_log_file.exists())
        self.assertTrue(self.logger.rolling_log_file.exists())

        content = self.logger.session_log_file.read_text()
        self.assertIn("[INFO] Test informative message", content)
        self.assertIn("[DEBUG] Test debug message", content)

    def test_task_lifecycle_logging(self):
        self.logger.log_task_start("jq", ".data", is_script=False)
        self.logger.log_task_output("STDOUT", "result string")
        self.logger.log_task_complete("jq", exit_code=0, duration_sec=0.123)

        content = self.logger.session_log_file.read_text()
        self.assertIn("[TASK_START] Tool: jq", content)
        self.assertIn(".data", content)
        self.assertIn("[STDOUT] result string", content)
        self.assertIn("[TASK_COMPLETE] Tool: jq | Status: SUCCESS", content)


if __name__ == "__main__":
    unittest.main()

