"""
Command and Script Execution Engine for RAgent.
Runs tasks with live stdout/stderr streaming, capture, duration timing, and timestamped logging.
"""

from dataclasses import dataclass
import os
from pathlib import Path
import shlex
import subprocess
import sys
import time
from typing import Dict, List, Optional, Union

from .logger import Colors, logger
from .validator import ToolStatus


@dataclass
class ExecutionResult:
    """Outcome of a command or script execution."""

    tool: str
    command: str
    exit_code: int
    stdout: str
    stderr: str
    duration_seconds: float
    is_script: bool = False

    @property
    def success(self) -> bool:
        return self.exit_code == 0


class CommandExecutor:
    """Executes ad-hoc CLI commands or script files safely with timestamped logging."""

    def __init__(self, agent_logger=logger):
        self.logger = agent_logger

    def run_command(
        self,
        tool_status: ToolStatus,
        args_str: str,
        cwd: Optional[Union[str, Path]] = None,
        extra_env: Optional[Dict[str, str]] = None,
    ) -> ExecutionResult:
        """Executes an ad-hoc command using the specified tool."""
        if not tool_status.available or not tool_status.path:
            err_msg = f"Cannot execute: Tool '{tool_status.name}' is not available."
            self.logger.error(err_msg)
            return ExecutionResult(
                tool=tool_status.name,
                command=args_str,
                exit_code=127,
                stdout="",
                stderr=err_msg,
                duration_seconds=0.0,
            )

        # Assemble full command
        binary = tool_status.path
        parsed_args = shlex.split(args_str) if args_str.strip() else []

        # If shell tool (bash/zsh), run with -c if compound expression and not already starting with -c
        if (
            tool_status.name in ["bash", "zsh"]
            and any(c in args_str for c in ["|", ";", "&&", "||", ">", "<", "$"])
            and not args_str.startswith("-c")
        ):
            cmd = [binary, "-c", args_str]
            display_cmd = f"{binary} -c '{args_str}'"
        else:
            cmd = [binary] + parsed_args
            display_cmd = f"{binary} {args_str}".strip()

        return self._execute(
            tool_name=tool_status.name,
            cmd_args=cmd,
            display_str=display_cmd,
            cwd=cwd,
            extra_env=extra_env,
            is_script=False,
        )

    def run_script(
        self,
        tool_status: ToolStatus,
        script_path: Union[str, Path],
        script_args: Optional[List[str]] = None,
        cwd: Optional[Union[str, Path]] = None,
        extra_env: Optional[Dict[str, str]] = None,
    ) -> ExecutionResult:
        """Executes a script file using the designated tool interpreter."""
        path_obj = Path(script_path).resolve()
        args = script_args or []

        if not path_obj.is_file():
            err_msg = f"Script file not found: {script_path}"
            self.logger.error(err_msg)
            return ExecutionResult(
                tool=tool_status.name,
                command=str(script_path),
                exit_code=2,
                stdout="",
                stderr=err_msg,
                duration_seconds=0.0,
                is_script=True,
            )

        if not tool_status.available or not tool_status.path:
            err_msg = f"Cannot run script: Tool '{tool_status.name}' is not available."
            self.logger.error(err_msg)
            return ExecutionResult(
                tool=tool_status.name,
                command=str(path_obj),
                exit_code=127,
                stdout="",
                stderr=err_msg,
                duration_seconds=0.0,
                is_script=True,
            )

        # Build execution array
        cmd = [tool_status.path, str(path_obj)] + args
        display_cmd = f"{tool_status.path} {path_obj} {' '.join(args)}".strip()

        return self._execute(
            tool_name=tool_status.name,
            cmd_args=cmd,
            display_str=display_cmd,
            cwd=cwd or path_obj.parent,
            extra_env=extra_env,
            is_script=True,
        )

    def _execute(
        self,
        tool_name: str,
        cmd_args: List[str],
        display_str: str,
        cwd: Optional[Union[str, Path]] = None,
        extra_env: Optional[Dict[str, str]] = None,
        is_script: bool = False,
    ) -> ExecutionResult:
        """Core execution loop with live streaming and structured logging."""
        # Log task start with timestamp
        self.logger.log_task_start(
            tool=tool_name, task_input=display_str, is_script=is_script
        )
        self.logger.debug(f"Working Directory: {cwd or os.getcwd()}")

        merged_env = os.environ.copy()
        if extra_env:
            merged_env.update(extra_env)

        start_time = time.perf_counter()
        stdout_lines: List[str] = []
        stderr_lines: List[str] = []

        try:
            process = subprocess.Popen(
                cmd_args,
                cwd=str(cwd) if cwd else None,
                env=merged_env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
            )

            # Read stdout line by line
            if process.stdout:
                try:
                    for line in iter(process.stdout.readline, ""):
                        if not line:
                            break
                        print(line, end="")
                        stdout_lines.append(line)
                        self.logger.log_task_output("STDOUT", line)
                finally:
                    process.stdout.close()

            # Read stderr if any
            if process.stderr:
                try:
                    for line in iter(process.stderr.readline, ""):
                        if not line:
                            break
                        sys.stderr.write(f"{Colors.RED}{line}{Colors.RESET}")
                        stderr_lines.append(line)
                        self.logger.log_task_output("STDERR", line)
                finally:
                    process.stderr.close()

            process.wait()
            exit_code = process.returncode

        except KeyboardInterrupt:
            self.logger.warn("Task interrupted by developer (Ctrl+C).")
            exit_code = 130
        except OSError as e:
            self.logger.error(f"Process execution failed: {e}")
            exit_code = 1
            stderr_lines.append(str(e))

        duration = time.perf_counter() - start_time
        full_stdout = "".join(stdout_lines)
        full_stderr = "".join(stderr_lines)

        # Log completion
        self.logger.log_task_complete(
            tool=tool_name, exit_code=exit_code, duration_sec=duration
        )

        return ExecutionResult(
            tool=tool_name,
            command=display_str,
            exit_code=exit_code,
            stdout=full_stdout,
            stderr=full_stderr,
            duration_seconds=duration,
            is_script=is_script,
        )


# Global executor instance
executor = CommandExecutor()
