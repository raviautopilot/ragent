# 🤖 RAgent - Developer CLI & Script Execution Assistant

A friendly, interactive Python agent designed to streamline developer workflows. RAgent validates configured CLI tools (`bash`, `zsh`, `vault`, `openshift` / `oc`, `jq`, `curl`, etc.), executes ad-hoc commands and script files, and automatically audits all inputs, outputs, and debug information with millisecond-precision timestamps.

---

## ✨ Features

- **Friendly Zero-Friction Greeting:** Greets the developer immediately with session information and no tedious acknowledgement prompts.
- **Environment & Tool Discovery:** Interactively prompts for the desired tool and verifies availability in `PATH`.
- **Helpful Remediation:** If a requested tool (e.g., `vault`, `oc`, `zsh`) is missing, RAgent displays friendly installation and configuration hints rather than crashing.
- **Script & Ad-Hoc Command Execution:** Runs inline commands or script files (`.sh`, `.py`, `.sql`, etc.) with real-time output streaming.
- **Timestamped Audit Trail:** Every command input, stdout/stderr stream, debug message, execution duration, and exit status is logged with millisecond timestamps (`YYYY-MM-DD HH:MM:SS.mmm`).
- **Standard Library Powered:** Zero external Python package dependencies required.

---

## 🚀 Quick Start

### 1. Interactive Mode (Default)
Run the agent directly from the repository root:
```bash
./ragent.py
```
Or with Python:
```bash
python3 ragent.py
# or
python3 -m ragent.cli
```

You will be greeted with the tool selection menu:
```text
╔════════════════════════════════════════════════════════════════╗
║                     🤖 Welcome to RAgent                       ║
║        Interactive CLI & Script Execution Assistant            ║
╚════════════════════════════════════════════════════════════════╝

Which application or tool would you like to use?
Type the number, tool name, or 'q' to quit:

   1) bash         ✔ Available (GNU bash, version 5.2.15)
   2) zsh          ✘ Not Found
   3) jq           ✔ Available (jq-1.6)
   4) vault        ✘ Not Found
   5) openshift    ✘ Not Found
   6) kubectl      ✘ Not Found
   7) curl         ✔ Available (curl 7.88.1)
   8) git          ✔ Available (git version 2.39.5)
   9) python3      ✔ Available (Python 3.11.2)
   c) Custom CLI binary
   q) Exit
```

---

## ⚙️ How to Set & Customize Constants (`ragent/config.py`)

All common script locations (such as `<ocPath>/ocLogin.sh` and `<vault_path>/vaultLogin.sh`), directory paths, and shortcuts are centralized in a single function inside [`ragent/config.py`](file:///home/ubuntu/code/github/raviautopilot/rWork/shared/ragent/ragent/config.py). 

This ensures you **never have to re-type long script paths** or modify paths across multiple files.

### Method 1: Permanent Setup (Recommended)
Open [`ragent/config.py`](file:///home/ubuntu/code/github/raviautopilot/rWork/shared/ragent/ragent/config.py) and update the default paths directly in `get_constants()`:

```python
def get_constants() -> AgentConstants:
    base_dir = Path(__file__).resolve().parent.parent

    # 1. Base Scripts Directory
    default_scripts_dir = Path("/home/ubuntu/code/github/my-tools/scripts")
    ...

    # 2. OpenShift (<ocPath>/ocLogin.sh)
    default_oc_path = Path("/home/ubuntu/code/github/openshift-tools")
    oc_path = Path(os.environ.get("OC_PATH", str(default_oc_path)))
    
    default_oc_login = oc_path / "ocLogin.sh"
    oc_login_script = Path(os.environ.get("OC_LOGIN_SCRIPT", str(default_oc_login)))

    # 3. HashiCorp Vault (<vault_path>/vaultLogin.sh)
    default_vault_path = Path("/home/ubuntu/code/github/vault-tools")
    vault_path = Path(os.environ.get("VAULT_PATH", str(default_vault_path)))

    default_vault_login = vault_path / "vaultLogin.sh"
    vault_login_script = Path(os.environ.get("VAULT_LOGIN_SCRIPT", str(default_vault_login)))

    # 4. Adding Custom Script Shortcuts
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
        # Add your own new shortcuts here:
        "deploy": {
            "tool": "bash",
            "script": "/path/to/deploy.sh",
            "description": "Run standard deployment script",
        },
    }
```

---

### Method 2: Dynamic Shell Overrides (Environment Variables)
If you want to temporarily point to different directories without editing Python files (e.g. across different machines or environments), export these environment variables in your terminal:

```bash
# Override OpenShift paths:
export OC_PATH="/path/to/my/openshift"
export OC_LOGIN_SCRIPT="/path/to/my/openshift/ocLogin.sh"

# Override Vault paths:
export VAULT_PATH="/path/to/my/vault"
export VAULT_LOGIN_SCRIPT="/path/to/my/vault/vaultLogin.sh"

# Override root scripts directory:
export RAGENT_SCRIPTS_DIR="/path/to/my/scripts"
```

---

### How RAgent Uses Your Constants

1. **Interactive Main Menu (1-Key Shortcuts):**
   When you launch `./ragent.py`, your shortcuts appear right in the main menu:
   ```text
   ⚡ Configured Shortcuts (Single Source of Truth):
    o) OpenShift Login  (/path/to/ocLogin.sh)
    v) Vault Login      (/path/to/vaultLogin.sh)
   ```
   Simply type `o` or `v` to run the respective login script immediately!

2. **Pre-Filled Defaults in Tool Sub-Menus:**
   When you select `openshift` or `vault` from the menu:
   - Option `0)` provides a 1-click launch for the configured script.
   - If you select Option `2) Execute a script file`, the prompt automatically suggests your configured script:
     ```text
     Enter path to script file (Press [Enter] to use default: /path/to/ocLogin.sh):
     Script path > [Press Enter]
     Using configured default: /path/to/ocLogin.sh
     ```

3. **Direct CLI Invocation:**
   You can also launch your configured scripts directly from terminal commands:
   ```bash
   ./ragent.py --oc-login
   ./ragent.py --vault-login
   ./ragent.py --shortcut deploy
   ```

---

## 🛠️ Command-Line Options (Automation & Power Users)

RAgent also supports non-interactive direct invocation for automated scripts and CI pipelines:

### Check Health of All Tools
```bash
./ragent.py --check
```

### Direct Command Execution
```bash
# Process JSON with jq:
./ragent.py --tool jq --cmd '.data' package.json

# Run bash command:
./ragent.py --tool bash --cmd "echo 'Hello from RAgent'"

# Check HashiCorp Vault status:
./ragent.py --tool vault --cmd status

# Check OpenShift cluster connection:
./ragent.py --tool oc --cmd whoami
```

### Script Execution
```bash
# Execute a deployment script with arguments:
./ragent.py --tool bash --script deploy.sh -- production

# Execute a Python script:
./ragent.py --tool python3 --script worker.py
```

---

## 📋 Pre-Configured CLI Tool Catalogue

| Tool | Binary Aliases | Description | Environment Variables Checked |
| :--- | :--- | :--- | :--- |
| **`bash`** | `bash` | GNU Bourne-Again SHell | None |
| **`zsh`** | `zsh` | Z Shell interactive interpreter | None |
| **`jq`** | `jq` | Command-line JSON processor | None |
| **`vault`** | `vault` | HashiCorp Vault Secret Manager | `VAULT_ADDR`, `VAULT_TOKEN`, `VAULT_NAMESPACE` |
| **`openshift`** | `oc`, `openshift` | Red Hat OpenShift CLI | `KUBECONFIG` |
| **`kubectl`** | `kubectl` | Kubernetes Cluster Control CLI | `KUBECONFIG` |
| **`curl`** | `curl` | URL data transfer tool | None |
| **`git`** | `git` | Distributed revision control | None |
| **`python3`** | `python3`, `python` | Python 3 runtime | None |
| **Custom** | *(Any binary)* | Any executable found in system `PATH` | Custom |

---

## 📂 Timestamped Logging System

All execution sessions write to the `logs/` directory:
- **`logs/ragent.log`**: Cumulative rolling log across all sessions.
- **`logs/ragent_YYYYMMDD_HHMMSS.log`**: Isolated per-session log.

### Sample Log Output
```text
=== RAgent Session Started: 2026-11-03 17:55:48.559 ===

┌────────────────────────────────────────────────────────────
│ [2026-11-03 17:55:48.568] [TASK_START] Tool: jq | Type: COMMAND
│ Input: /usr/bin/jq --version
└────────────────────────────────────────────────────────────
[2026-11-03 17:55:48.569] [DEBUG] Working Directory: /home/ubuntu/code/github/raviautopilot/rWork/shared/ragent
[2026-11-03 17:55:48.571] [STDOUT] jq-1.6
[2026-11-03 17:55:48.571] [TASK_COMPLETE] Tool: jq | Status: SUCCESS | Duration: 0.002s
```

---

## 🧪 Running Unit Tests

Run the full automated test suite (12 tests covering logger, validator, and executor):
```bash
python3 -m unittest discover -s tests -p "test_*.py" -v
```
