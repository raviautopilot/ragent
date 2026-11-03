"""
Centralized Configuration and Path Constants for RAgent.
Defines common tool paths, login scripts (e.g., ocLogin.sh, vaultLogin.sh),
and workflow shortcuts in a single easily editable function.
"""

from dataclasses import dataclass, field
import os
from pathlib import Path
from typing import Dict, Optional


@dataclass
class AgentConstants:
    """Pre-configured operational constants, paths, and script shortcuts."""

    # Base workspace or script directories
    scripts_dir: Path

    # OpenShift Configuration
    oc_path: Path
    oc_login_script: Path

    # HashiCorp Vault Configuration
    vault_path: Path
    vault_login_script: Path

    # Custom or tool-specific script shortcuts: shortcut_name -> (tool_name, script_path)
    script_shortcuts: Dict[str, Dict[str, str]] = field(default_factory=dict)

    def get_shortcut(self, name: str) -> Optional[Dict[str, str]]:
        """Returns shortcut details by alias if registered."""
        return self.script_shortcuts.get(name.lower())


def get_constants() -> AgentConstants:
    """
    ===========================================================================
    SINGLE SOURCE OF TRUTH: Edit your paths and script constants here.
    ===========================================================================
    Modify the defaults below to match your environment. You can also override
    any path by exporting the corresponding environment variable.
    """
    # Base directory of the ragent package
    base_dir = Path(__file__).resolve().parent.parent

    # 1. Scripts Root Directory
    default_scripts_dir = base_dir / "scripts"
    scripts_dir_str = os.environ.get("RAGENT_SCRIPTS_DIR", str(default_scripts_dir))
    scripts_dir = Path(scripts_dir_str)

    # 2. OpenShift (<ocPath>/ocLogin.sh)
    default_oc_path = scripts_dir / "openshift"
    oc_path_str = os.environ.get("OC_PATH", str(default_oc_path))
    oc_path = Path(oc_path_str)

    default_oc_login = oc_path / "ocLogin.sh"
    oc_login_str = os.environ.get("OC_LOGIN_SCRIPT", str(default_oc_login))
    oc_login_script = Path(oc_login_str)

    # 3. HashiCorp Vault (<vault_path>/vaultLogin.sh)
    default_vault_path = scripts_dir / "vault"
    vault_path_str = os.environ.get("VAULT_PATH", str(default_vault_path))
    vault_path = Path(vault_path_str)

    default_vault_login = vault_path / "vaultLogin.sh"
    vault_login_str = os.environ.get("VAULT_LOGIN_SCRIPT", str(default_vault_login))
    vault_login_script = Path(vault_login_str)

    # 4. Registered Script Shortcuts
    # Add any common scripts you want 1-click access to
    shortcuts = {
        "oc-login": {
            "tool": "bash",
            "script": str(oc_login_script),
            "description": "Log into OpenShift cluster using ocLogin.sh",
        },
        "vault-login": {
            "tool": "bash",
            "script": str(vault_login_script),
            "description": "Authenticate with HashiCorp Vault using vaultLogin.sh",
        },
    }

    return AgentConstants(
        scripts_dir=scripts_dir,
        oc_path=oc_path,
        oc_login_script=oc_login_script,
        vault_path=vault_path,
        vault_login_script=vault_login_script,
        script_shortcuts=shortcuts,
    )


# Global singleton instance for quick access
constants = get_constants()
