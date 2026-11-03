"""
Interactive Developer Agent loop for RAgent.
Provides friendly greeting, tool selection, availability validation, and script execution.
"""

from pathlib import Path
import sys
from typing import Optional

from .executor import CommandExecutor, executor
from .logger import Colors, logger
from .validator import ToolStatus, ToolValidator, validator


class DeveloperAgent:
    """Interactive Agent designed to make human developer's workflow easy and friendly."""

    def __init__(
        self,
        tool_validator: ToolValidator = validator,
        cmd_executor: CommandExecutor = executor,
    ):
        self.validator = tool_validator
        self.executor = cmd_executor
        self.logger = logger

    def print_greeting(self) -> None:
        """Friendly greeting banner with zero required acknowledgements."""
        banner = f"""
{Colors.CYAN}{Colors.BOLD}╔════════════════════════════════════════════════════════════════╗
║                     🤖 Welcome to RAgent                       ║
║        Interactive CLI & Script Execution Assistant            ║
╚════════════════════════════════════════════════════════════════╝{Colors.RESET}
{Colors.DIM}Session Log:{Colors.RESET} {self.logger.session_log_file}
{Colors.GREEN}Ready to assist with your CLI tools and scripts.{Colors.RESET}
"""
        print(banner)
        self.logger.info("RAgent session initiated. Ready for developer input.")

    def run_interactive(self) -> None:
        """Main interactive agent loop."""
        self.print_greeting()

        while True:
            try:
                selected_tool = self.prompt_tool_selection()
                if not selected_tool:
                    print(
                        f"\n{Colors.GREEN}👋 Thank you for using RAgent! Happy coding!{Colors.RESET}"
                    )
                    self.logger.info("Developer session terminated normally.")
                    break

                # Validate tool availability
                status = self.validate_and_display_tool(selected_tool)
                if not status.available:
                    # Provide friendly hint and return to tool selection
                    continue

                # Run tool sub-actions
                self.run_tool_session(status)

            except (KeyboardInterrupt, EOFError):
                print(
                    f"\n\n{Colors.YELLOW}Session interrupted. Goodbye!{Colors.RESET}"
                )
                self.logger.warn("Session received SIGINT/EOF interrupt.")
                break

    def prompt_tool_selection(self) -> Optional[str]:
        """Displays tool options and prompts developer for which application to use."""
        tools_list = self.validator.list_all_tools()

        print(
            f"\n{Colors.BOLD}{Colors.WHITE}Which application or tool would you like to use?{Colors.RESET}"
        )
        print(f"{Colors.DIM}Type the number, tool name, or 'q' to quit:{Colors.RESET}\n")

        for idx, t in enumerate(tools_list, 1):
            if t.available:
                status_icon = f"{Colors.GREEN}✔ Available{Colors.RESET}"
                version_info = (
                    f" ({Colors.DIM}{t.version.splitlines()[0][:35]}{Colors.RESET})"
                    if t.version
                    else ""
                )
            else:
                status_icon = f"{Colors.RED}✘ Not Found{Colors.RESET}"
                version_info = ""

            print(
                f"  {Colors.BOLD}{idx:2d}){Colors.RESET} {t.name:<12} {status_icon}{version_info}"
            )

        print(f"  {Colors.BOLD} c){Colors.RESET} Custom CLI binary")
        print(f"  {Colors.BOLD} q){Colors.RESET} Exit")

        while True:
            try:
                choice = (
                    input(
                        f"\n{Colors.CYAN}{Colors.BOLD}Select application > {Colors.RESET}"
                    )
                    .strip()
                    .lower()
                )
            except (KeyboardInterrupt, EOFError):
                return None

            if not choice:
                continue

            if choice in ["q", "quit", "exit"]:
                return None

            if choice in ["c", "custom"]:
                custom_name = input(
                    f"{Colors.CYAN}Enter custom binary name or path > {Colors.RESET}"
                ).strip()
                if custom_name:
                    return custom_name
                continue

            # Numbered selection
            if choice.isdigit():
                num = int(choice)
                if 1 <= num <= len(tools_list):
                    return tools_list[num - 1].name

            # Name match
            for t in tools_list:
                if t.name.lower() == choice:
                    return t.name

            # Try as custom command directly
            print(
                f"{Colors.YELLOW}Notice: '{choice}' is not in catalog. Checking system PATH...{Colors.RESET}"
            )
            return choice

    def validate_and_display_tool(self, tool_name: str) -> ToolStatus:
        """Validates tool and prints friendly diagnostic feedback."""
        self.logger.step(f"Validating tool availability: '{tool_name}'...")
        status = self.validator.check_tool(tool_name)

        if status.available:
            self.logger.info(
                f"Tool '{status.name}' is validated and ready at {status.path}"
            )
            print(
                f"\n{Colors.GREEN}{Colors.BOLD}✔ Tool Verified:{Colors.RESET} {status.name}"
            )
            print(f"  {Colors.BOLD}Path:{Colors.RESET}    {status.path}")
            if status.version:
                print(f"  {Colors.BOLD}Version:{Colors.RESET} {status.version}")

            if status.present_env_vars:
                print(f"  {Colors.BOLD}Environment variables detected:{Colors.RESET}")
                for k, v in status.present_env_vars.items():
                    print(f"    • {k} = {v}")

            if status.missing_env_vars:
                print(
                    f"  {Colors.YELLOW}Notice: Optional configuration missing: {', '.join(status.missing_env_vars)}{Colors.RESET}"
                )
        else:
            self.logger.warn(
                f"Tool '{tool_name}' is not currently available in PATH."
            )
            print(
                f"\n{Colors.RED}{Colors.BOLD}✘ Tool Unavailable:{Colors.RESET} '{tool_name}'"
            )
            if status.remediation_hint:
                print(
                    f"  {Colors.YELLOW}💡 How to resolve:{Colors.RESET} {status.remediation_hint}"
                )
            print(
                f"  {Colors.DIM}Please install it or pick another tool from the menu.{Colors.RESET}"
            )

        return status

    def run_tool_session(self, tool_status: ToolStatus) -> None:
        """Action loop for a validated tool."""
        while True:
            print(
                f"\n{Colors.BOLD}{Colors.WHITE}Action for '{tool_status.name}':{Colors.RESET}"
            )
            print(
                f"  {Colors.BOLD}1){Colors.RESET} Execute command / query (e.g. arguments or script expression)"
            )
            print(f"  {Colors.BOLD}2){Colors.RESET} Execute a script file")
            print(f"  {Colors.BOLD}3){Colors.RESET} Choose another tool")
            print(f"  {Colors.BOLD}4){Colors.RESET} Exit")

            try:
                action = (
                    input(
                        f"\n{Colors.CYAN}{Colors.BOLD}[{tool_status.name}] Select action (1-4) > {Colors.RESET}"
                    )
                    .strip()
                    .lower()
                )
            except (KeyboardInterrupt, EOFError):
                break

            if action in ["3", "back", "b"]:
                break
            elif action in ["4", "q", "quit", "exit"]:
                sys.exit(0)
            elif action == "1":
                self._handle_command_action(tool_status)
            elif action == "2":
                self._handle_script_action(tool_status)
            else:
                print(
                    f"{Colors.YELLOW}Invalid option. Please choose 1, 2, 3, or 4.{Colors.RESET}"
                )

    def _handle_command_action(self, tool_status: ToolStatus) -> None:
        """Prompts for and executes an ad-hoc command."""
        prompt_hint = f"Enter arguments or command for '{tool_status.name}'"
        if tool_status.name == "jq":
            prompt_hint += " (e.g., '.[] | .name' data.json or --version)"
        elif tool_status.name == "vault":
            prompt_hint += " (e.g., status or kv list secret/)"
        elif tool_status.name in ["oc", "openshift"]:
            prompt_hint += " (e.g., whoami or get pods)"
        elif tool_status.name in ["bash", "zsh"]:
            prompt_hint += " (e.g., -c 'echo Hello World')"

        print(f"\n{Colors.DIM}{prompt_hint}:{Colors.RESET}")
        try:
            cmd_input = input(
                f"{Colors.CYAN}{tool_status.name} > {Colors.RESET}"
            ).strip()
        except (KeyboardInterrupt, EOFError):
            return

        if not cmd_input:
            print(f"{Colors.YELLOW}No input provided. Action cancelled.{Colors.RESET}")
            return

        # Execute and log
        self.executor.run_command(tool_status, cmd_input)

    def _handle_script_action(self, tool_status: ToolStatus) -> None:
        """Prompts for and executes a script file."""
        print(f"\n{Colors.DIM}Enter path to script file:{Colors.RESET}")
        try:
            script_path_str = input(
                f"{Colors.CYAN}Script path > {Colors.RESET}"
            ).strip()
        except (KeyboardInterrupt, EOFError):
            return

        if not script_path_str:
            print(
                f"{Colors.YELLOW}No script path provided. Action cancelled.{Colors.RESET}"
            )
            return

        # Optional script arguments
        try:
            args_input = input(
                f"{Colors.CYAN}Script arguments (optional, press Enter for none) > {Colors.RESET}"
            ).strip()
        except (KeyboardInterrupt, EOFError):
            args_input = ""

        script_args = args_input.split() if args_input else []
        self.executor.run_script(
            tool_status, script_path=script_path_str, script_args=script_args
        )

