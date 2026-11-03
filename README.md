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

## ⚙️ Centralized Path Constants & Shortcuts (`ragent/config.py`)

All standard operational paths, login scripts (`<ocPath>/ocLogin.sh`, `<vault_path>/vaultLogin.sh`), and shortcuts are centralized in one single function in [`ragent/config.py`](file:///home/ubuntu/code/github/raviautopilot/rWork/shared/ragent/ragent/config.py):

```python
def get_constants() -> AgentConstants:
    # 1. OpenShift (<ocPath>/ocLogin.sh)
    oc_path = ...
    oc_login_script = oc_path / "ocLogin.sh"

    # 2. HashiCorp Vault (<vault_path>/vaultLogin.sh)
    vault_path = ...
    vault_login_script = vault_path / "vaultLogin.sh"
    ...
```

### Launching Configured Scripts

**In Interactive Mode:**
- Type `o` at the main menu to immediately run `ocLogin.sh`.
- Type `v` at the main menu to immediately run `vaultLogin.sh`.
- When executing a script file under `openshift` or `vault`, the prompt defaults to your pre-configured path so you can simply press `[Enter]` to run it without re-typing.

**From the Terminal (CLI Shortcuts):**
```bash
./ragent.py --oc-login
./ragent.py --vault-login
./ragent.py --shortcut oc-login
```

**Environment Variable Overrides (Optional):**
You can also override the defaults dynamically in your shell without editing files:
```bash
export OC_PATH="/custom/cluster/tools"
export OC_LOGIN_SCRIPT="/custom/cluster/tools/ocLogin.sh"
export VAULT_PATH="/custom/vault/tools"
export VAULT_LOGIN_SCRIPT="/custom/vault/tools/vaultLogin.sh"
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
