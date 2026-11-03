"""
Tool discovery, environment validation, and dependency checking for RAgent.
Validates tools like bash, zsh, vault, openshift (oc), jq, and custom binaries.
"""

from dataclasses import dataclass, field
import os
from pathlib import Path
import shutil
import subprocess
from typing import Dict, List, Optional, Tuple


@dataclass
class ToolDefinition:
    """Specification of a CLI application or tool."""

    name: str
    binary_aliases: List[str]
    description: str
    install_hint: str
    version_flag: str = "--version"
    required_env_vars: List[str] = field(default_factory=list)
    optional_env_vars: List[str] = field(default_factory=list)


@dataclass
class ToolStatus:
    """Current state of a tool on the host system."""

    name: str
    available: bool
    path: Optional[str] = None
    version: Optional[str] = None
    missing_env_vars: List[str] = field(default_factory=list)
    present_env_vars: Dict[str, str] = field(default_factory=dict)
    remediation_hint: str = ""


# Default catalog of supported tools
DEFAULT_TOOLS: Dict[str, ToolDefinition] = {
    "bash": ToolDefinition(
        name="bash",
        binary_aliases=["bash"],
        description="GNU Bourne-Again SHell",
        install_hint="Standard Linux shell. Install via: sudo apt install bash",
        version_flag="--version",
    ),
    "zsh": ToolDefinition(
        name="zsh",
        binary_aliases=["zsh"],
        description="Z Shell (powerful command interpreter)",
        install_hint="Install via: sudo apt install zsh (or brew install zsh)",
        version_flag="--version",
    ),
    "jq": ToolDefinition(
        name="jq",
        binary_aliases=["jq"],
        description="Lightweight and flexible command-line JSON processor",
        install_hint="Install via: sudo apt install jq (or brew install jq)",
        version_flag="--version",
    ),
    "vault": ToolDefinition(
        name="vault",
        binary_aliases=["vault"],
        description="HashiCorp Vault secret management CLI",
        install_hint="Install via HashiCorp apt repository, brew install vault, or download from https://releases.hashicorp.com/vault/",
        version_flag="version",
        required_env_vars=[],
        optional_env_vars=["VAULT_ADDR", "VAULT_TOKEN", "VAULT_NAMESPACE"],
    ),
    "openshift": ToolDefinition(
        name="openshift",
        binary_aliases=["oc", "openshift"],
        description="Red Hat OpenShift CLI (oc)",
        install_hint="Download oc client binary from Red Hat OpenShift console or mirror.openshift.com and put in /usr/local/bin",
        version_flag="version --client",
        required_env_vars=[],
        optional_env_vars=["KUBECONFIG"],
    ),
    "kubectl": ToolDefinition(
        name="kubectl",
        binary_aliases=["kubectl"],
        description="Kubernetes cluster control CLI",
        install_hint="Install via: sudo apt install kubectl (or curl -LO https://dl.k8s.io/release/...)",
        version_flag="version --client",
        optional_env_vars=["KUBECONFIG"],
    ),
    "curl": ToolDefinition(
        name="curl",
        binary_aliases=["curl"],
        description="Command line tool for transferring data with URLs",
        install_hint="Install via: sudo apt install curl",
        version_flag="--version",
    ),
    "git": ToolDefinition(
        name="git",
        binary_aliases=["git"],
        description="Fast, scalable, distributed revision control system",
        install_hint="Install via: sudo apt install git",
        version_flag="--version",
    ),
    "python3": ToolDefinition(
        name="python3",
        binary_aliases=["python3", "python"],
        description="Python 3 interactive interpreter & runtime",
        install_hint="Install via: sudo apt install python3",
        version_flag="--version",
    ),
}


class ToolValidator:
    """Validates CLI tools and environment variables."""

    def __init__(self, tools_catalog: Optional[Dict[str, ToolDefinition]] = None):
        self.catalog = tools_catalog or DEFAULT_TOOLS

    def check_tool(self, tool_name: str) -> ToolStatus:
        """Inspects whether a tool binary is present in PATH and checks its environment."""
        clean_name = tool_name.strip().lower()

        # Check if in catalog
        tool_def = self.catalog.get(clean_name)

        if not tool_def:
            # Fallback for arbitrary user-specified binary (e.g. custom script or tool)
            found_path = shutil.which(tool_name)
            if found_path:
                version = self._get_binary_version(found_path, "--version")
                return ToolStatus(
                    name=tool_name,
                    available=True,
                    path=found_path,
                    version=version,
                    remediation_hint="",
                )
            return ToolStatus(
                name=tool_name,
                available=False,
                path=None,
                version=None,
                remediation_hint=f"Binary '{tool_name}' was not found in PATH ($PATH={os.environ.get('PATH', '')}).",
            )

        # Check aliases
        found_path: Optional[str] = None
        for alias in tool_def.binary_aliases:
            resolved = shutil.which(alias)
            if resolved:
                found_path = resolved
                break

        if not found_path:
            return ToolStatus(
                name=tool_def.name,
                available=False,
                path=None,
                version=None,
                remediation_hint=tool_def.install_hint,
            )

        # Retrieve version string
        version_str = self._get_binary_version(found_path, tool_def.version_flag)

        # Check environment variables
        missing_required: List[str] = []
        present_vars: Dict[str, str] = {}

        for var in tool_def.required_env_vars:
            val = os.environ.get(var)
            if not val:
                missing_required.append(var)
            else:
                present_vars[var] = self._mask_sensitive(var, val)

        for var in tool_def.optional_env_vars:
            val = os.environ.get(var)
            if val:
                present_vars[var] = self._mask_sensitive(var, val)

        remediation = ""
        if missing_required:
            remediation = f"Missing required environment variables: {', '.join(missing_required)}."

        return ToolStatus(
            name=tool_def.name,
            available=True,
            path=found_path,
            version=version_str,
            missing_env_vars=missing_required,
            present_env_vars=present_vars,
            remediation_hint=remediation,
        )

    def list_all_tools(self) -> List[ToolStatus]:
        """Returns status for all registered tools in catalog."""
        return [self.check_tool(name) for name in self.catalog.keys()]

    @staticmethod
    def _get_binary_version(binary_path: str, version_flag: str) -> Optional[str]:
        """Safely invokes the binary with its version flag and extracts first line."""
        try:
            cmd = [binary_path] + version_flag.split()
            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3,
                check=False,
            )
            out = res.stdout.strip() or res.stderr.strip()
            if out:
                # Return first line
                return out.splitlines()[0]
        except (subprocess.SubprocessError, OSError):
            pass
        return None

    @staticmethod
    def _mask_sensitive(var_name: str, value: str) -> str:
        """Masks tokens and passwords for safe logging."""
        if any(s in var_name.upper() for s in ["TOKEN", "SECRET", "PASSWORD", "KEY"]):
            if len(value) > 8:
                return value[:3] + "..." + value[-3:]
            return "***"
        return value


# Global validator instance
validator = ToolValidator()

