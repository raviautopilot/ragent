"""
Timestamped logging system for RAgent.
Logs all inputs, outputs, executions, and debug information with millisecond precision.
"""

from datetime import datetime
import os
from pathlib import Path
import sys
from typing import Optional


class Colors:
    """ANSI terminal styling."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    BLUE = "\033[0;34m"
    MAGENTA = "\033[0;35m"
    CYAN = "\033[0;36m"
    WHITE = "\033[1;37m"


class AgentLogger:
    """Handles structured, timestamped logging to both stdout and persistent log files."""

    def __init__(self, log_dir: Optional[Path] = None, session_name: str = "ragent"):
        if log_dir is None:
            # Default to logs/ in project root
            base_dir = Path(__file__).resolve().parent.parent
            log_dir = base_dir / "logs"

        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_log_file = self.log_dir / f"{session_name}_{now_str}.log"
        self.rolling_log_file = self.log_dir / f"{session_name}.log"

        # Initialize session log
        self._write_file(f"=== RAgent Session Started: {self._get_timestamp()} ===\n")

    @staticmethod
    def _get_timestamp() -> str:
        """Returns current timestamp with millisecond resolution: YYYY-MM-DD HH:MM:SS.mmm."""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

    def _write_file(self, content: str) -> None:
        """Appends line to both the session log file and the rolling log file."""
        try:
            with open(self.session_log_file, "a", encoding="utf-8") as f:
                f.write(content)
            with open(self.rolling_log_file, "a", encoding="utf-8") as f:
                f.write(content)
        except OSError as e:
            sys.stderr.write(
                f"[LOGGER-ERROR] Failed writing to log file: {e}\n"
            )

    def log(
        self,
        level: str,
        message: str,
        color: str = Colors.WHITE,
        console: bool = True,
    ) -> None:
        """Base log method that outputs timestamped record."""
        ts = self._get_timestamp()
        file_entry = f"[{ts}] [{level.upper()}] {message}\n"
        self._write_file(file_entry)

        if console:
            console_entry = (
                f"{Colors.DIM}[{ts}]{Colors.RESET} "
                f"{color}[{level.upper()}]{Colors.RESET} {message}"
            )
            print(console_entry)

    def info(self, message: str) -> None:
        self.log("INFO", message, color=Colors.GREEN)

    def debug(self, message: str) -> None:
        self.log("DEBUG", message, color=Colors.MAGENTA)

    def warn(self, message: str) -> None:
        self.log("WARN", message, color=Colors.YELLOW)

    def error(self, message: str) -> None:
        self.log("ERROR", message, color=Colors.RED)

    def step(self, message: str) -> None:
        self.log("STEP", message, color=Colors.CYAN)

    def log_task_start(
        self, tool: str, task_input: str, is_script: bool = False
    ) -> None:
        """Record the initiation of a task with input details."""
        ts = self._get_timestamp()
        task_type = "SCRIPT" if is_script else "COMMAND"
        divider = "─" * 60
        header = (
            f"\n┌{divider}\n"
            f"│ [{ts}] [TASK_START] Tool: {tool} | Type: {task_type}\n"
            f"│ Input: {task_input}\n"
            f"└{divider}"
        )
        self._write_file(header + "\n")
        print(f"\n{Colors.CYAN}{Colors.BOLD}🚀 [{ts}] [TASK START]{Colors.RESET}")
        print(f"  {Colors.BOLD}Tool:{Colors.RESET}  {tool}")
        print(f"  {Colors.BOLD}Input:{Colors.RESET} {task_input}\n")

    def log_task_output(self, stream_type: str, data: str) -> None:
        """Record output chunks from running command or script."""
        ts = self._get_timestamp()
        for line in data.splitlines():
            file_entry = f"[{ts}] [{stream_type.upper()}] {line}\n"
            self._write_file(file_entry)

    def log_task_complete(
        self, tool: str, exit_code: int, duration_sec: float
    ) -> None:
        """Record task completion with returncode and execution duration."""
        ts = self._get_timestamp()
        status_str = "SUCCESS" if exit_code == 0 else f"FAILED({exit_code})"
        color = Colors.GREEN if exit_code == 0 else Colors.RED

        summary = (
            f"[{ts}] [TASK_COMPLETE] Tool: {tool} | "
            f"Status: {status_str} | Duration: {duration_sec:.3f}s\n"
        )
        self._write_file(summary)

        print(
            f"\n{color}{Colors.BOLD}🏁 [{ts}] [TASK COMPLETE]{Colors.RESET} "
            f"Status: {color}{status_str}{Colors.RESET} | "
            f"Duration: {duration_sec:.3f}s\n"
        )


# Global singleton instance for easy import across modules
logger = AgentLogger()

