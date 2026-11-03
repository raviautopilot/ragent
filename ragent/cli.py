"""
CLI entrypoint and argument parser for RAgent.
Supports interactive mode, direct execution, tool healthchecks, and automation flags.
"""

import argparse
import sys
from typing import List, Optional

from .agent import DeveloperAgent
from .executor import executor
from .logger import Colors, logger
from .validator import validator


def build_parser() -> argparse.ArgumentParser:
    """Configures command line arguments."""
    parser = argparse.ArgumentParser(
        prog="ragent",
        description="RAgent - Friendly Interactive Developer Assistant for CLI & Script Execution.",
        epilog="Examples:\n"
        "  ragent                          # Start interactive session\n"
        "  ragent --check                  # Check availability of all configured tools\n"
        "  ragent --tool jq --cmd '.foo' data.json\n"
        "  ragent --tool bash --script deploy.sh\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "-t",
        "--tool",
        type=str,
        help="Specify the tool to use (e.g. jq, vault, oc, bash, zsh).",
    )

    parser.add_argument(
        "-c",
        "--cmd",
        nargs=argparse.REMAINDER,
        help="Direct command or arguments to execute with the selected tool.",
    )

    parser.add_argument(
        "-s",
        "--script",
        type=str,
        help="Path to a script file to execute with the selected tool.",
    )

    parser.add_argument(
        "--check",
        action="store_true",
        help="Run environment health check on all configured tools.",
    )

    parser.add_argument(
        "--list",
        action="store_true",
        help="List all supported tools in catalog.",
    )

    parser.add_argument(
        "extra_args",
        nargs="*",
        help="Additional arguments passed to the script or command.",
    )

    return parser


def run_healthcheck() -> int:
    """Displays availability and status of all configured tools."""
    logger.info("Executing environment healthcheck on configured tools...")
    tools = validator.list_all_tools()

    print(
        f"\n{Colors.BOLD}{Colors.BLUE}======================================================{Colors.RESET}"
    )
    print(
        f"  {Colors.BOLD}🔍 RAgent Tool Environment Health Check{Colors.RESET}"
    )
    print(
        f"{Colors.BOLD}{Colors.BLUE}======================================================{Colors.RESET}\n"
    )

    available_count = 0
    for t in tools:
        if t.available:
            available_count += 1
            print(
                f"  {Colors.GREEN}✔ {t.name:<12}{Colors.RESET} [{t.path}]"
            )
            if t.version:
                print(f"      Version: {Colors.DIM}{t.version}{Colors.RESET}")
            if t.present_env_vars:
                for k, v in t.present_env_vars.items():
                    print(f"      Config:  {k}={v}")
        else:
            print(f"  {Colors.RED}✘ {t.name:<12}{Colors.RESET} [Not Found]")
            if t.remediation_hint:
                print(
                    f"      Hint:    {Colors.YELLOW}{t.remediation_hint}{Colors.RESET}"
                )

    print(
        f"\n{Colors.CYAN}Summary: {available_count}/{len(tools)} tools available in system PATH.{Colors.RESET}\n"
    )
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    """CLI application entrypoint."""
    parser = build_parser()
    args = parser.parse_args(argv)

    # Health check flag
    if args.check or args.list:
        return run_healthcheck()

    # Direct execution mode
    if args.tool:
        status = validator.check_tool(args.tool)
        if not status.available:
            logger.error(
                f"Requested tool '{args.tool}' is not installed or available."
            )
            if status.remediation_hint:
                print(
                    f"{Colors.YELLOW}💡 Install Hint:{Colors.RESET} {status.remediation_hint}"
                )
            return 127

        # Script execution
        if args.script:
            script_args = args.extra_args or []
            res = executor.run_script(
                status, script_path=args.script, script_args=script_args
            )
            return res.exit_code

        # Command execution
        if args.cmd:
            if isinstance(args.cmd, list):
                full_cmd = " ".join(args.cmd)
            else:
                full_cmd = str(args.cmd)
            if args.extra_args:
                full_cmd += " " + " ".join(args.extra_args)
            res = executor.run_command(status, full_cmd)
            return res.exit_code

        # If tool specified without cmd or script, enter tool-specific session
        agent = DeveloperAgent()
        agent.run_tool_session(status)
        return 0

    # Default: Interactive Agent Mode
    agent = DeveloperAgent()
    agent.run_interactive()
    return 0


if __name__ == "__main__":
    sys.exit(main())
