# Python Remote Debug Skill

A Claude Code plugin for debugging running Python processes using Python 3.14+ [remote debugging](https://docs.python.org/3/howto/remote_debugging.html) via `sys.remote_exec()`. This skill enables you to inject debugging scripts into live processes to get stack traces without stopping them.

## Features

- **Remote Process Inspection**: Inject Python scripts into running processes
- **Thread Stack Traces**: Get stack traces from all threads in a process
- **Gevent/Greenlet Support**: Special handling for gevent-based workers (like Celery with `-P gevent`)
- **Zero Downtime Debugging**: Diagnose stuck processes without stopping them

## Prerequisites

- **Python 3.14+** (both debugger and target process)
- **Elevated privileges** (sudo or equivalent) to attach to other processes. See [section below](#configuring-sudo-for-claude-code) for more detailed instructions on this.

## Installation

### As a Claude Code Plugin (Recommended)

1. Add the marketplace:
```bash
/plugin marketplace add promptromp/python-remote-debug-skill
```

2. Install the plugin:
```bash
/plugin install python-remote-debug-skill
```

### Local Development

Clone and load directly:
```bash
git clone https://github.com/promptromp/python-remote-debug-skill.git
claude --plugin-dir ./python-remote-debug-skill
```

### Standalone Skill

Extract the `skills/debug-remote/` folder to `~/.claude/skills/`:
```bash
cp -r skills/debug-remote ~/.claude/skills/
```

## Usage

Once installed, Claude can use the skill automatically when you ask about debugging Python processes, or invoke it directly:

```
/python-remote-debug-skill:debug-remote
```

### Example Prompts

- "Debug the stuck Celery worker process"
- "Get stack traces from the Python process with PID 12345"
- "Help me figure out why my gevent worker is hanging"

## Helper Scripts

The `skills/debug-remote/scripts/` directory contains ready-to-use debug scripts that can jumpstart the debugging process for some common scenarios involving concurrency:

- `debug_threads.py` - Get stack traces from all OS threads
- `debug_gevent.py` - Get stack traces from all gevent greenlets

## How It Works

Python 3.14 introduced `sys.remote_exec()` which allows injecting Python scripts into running processes. The script executes asynchronously at the next "safe point" in the interpreter.

Key characteristics:
- Script executes in the target process's context
- Output must be written to a file (stdout/stderr not visible)
- Call returns immediately; execution happens asynchronously
- If blocked in C code, script waits until Python resumes

## Common Issues Detected

This technique can reveal:

1. **Stuck in external library**: Process waiting in third-party code
2. **ThreadPoolExecutor deadlock**: Thread pool conflicts with gevent
3. **Missing timeouts**: HTTP clients without timeout parameters
4. **Unenforced time limits**: gevent cooperative scheduling bypassing limits

## Configuring sudo for Claude Code

Remote debugging requires elevated privileges to attach to other processes on most Unix-like systems. On **macOS**, this is needed for the `com.apple.system-task-ports` entitlement. On **Linux**, the `ptrace` system call is restricted by the Yama security module (enabled by default on Ubuntu and many other distributions). When Claude Code runs `sys.remote_exec()`, it needs sudo access. Here are several approaches, from simplest to most secure:

### Option 1: Full sudo Access (Simplest)

Grant your user passwordless sudo for all commands:

```bash
sudo visudo
```

Add this line (replace `yourusername` with your actual username):

```
yourusername ALL=(ALL) NOPASSWD: ALL
```

> **Warning**: This grants your user root-equivalent access without a password for any command. Only use this on personal development machines where convenience outweighs security concerns. Not recommended for shared or production systems.

### Option 2: Passwordless sudo for Python Only (Recommended)

A more secure approach—allow passwordless sudo only for the specific Python interpreter:

```bash
sudo visudo
```

Add this line (adjust paths to match your Python 3.14 installation):

```
yourusername ALL=(ALL) NOPASSWD: /opt/homebrew/bin/python3.14, /usr/local/bin/python3.14, /usr/bin/python3.14
```

This grants passwordless sudo only for the Python 3.14 interpreter, limiting exposure.

### Option 3: Dedicated User with Limited sudo (Advanced)

For stricter isolation, create a dedicated user for Claude Code sessions.

**On macOS:**

```bash
sudo dscl . -create /Users/claudecode
sudo dscl . -create /Users/claudecode UserShell /bin/zsh
sudo dscl . -create /Users/claudecode UniqueID 550
sudo dscl . -create /Users/claudecode PrimaryGroupID 20
sudo dscl . -create /Users/claudecode NFSHomeDirectory /Users/claudecode
sudo mkdir -p /Users/claudecode
sudo chown claudecode:staff /Users/claudecode
```

**On Linux:**

```bash
sudo useradd -m -s /bin/bash claudecode
```

Then add to `/etc/sudoers`:

```
claudecode ALL=(ALL) NOPASSWD: /opt/homebrew/bin/python3.14, /usr/local/bin/python3.14, /usr/bin/python3.14
```

Run Claude Code as this user:

```bash
sudo -u claudecode claude
```

### Linux-Specific: Relaxing ptrace Restrictions

On Linux systems with Yama enabled, you can alternatively relax ptrace restrictions system-wide (until reboot):

```bash
echo 0 | sudo tee /proc/sys/kernel/yama/ptrace_scope
```

This allows any process to ptrace any other process owned by the same user, which may reduce the need for sudo in some scenarios.

### Docker and Containers

If running inside a container, you must explicitly grant the `SYS_PTRACE` capability:

```bash
docker run --cap-add=SYS_PTRACE ...
```

Note that even with this capability, you may still need root inside the container.

### Security Considerations

- **Principle of least privilege**: Option 2 is preferred for most users—it balances convenience with security.
- **Audit trail**: sudo usage is logged (`/var/log/auth.log` on Linux, `/var/log/system.log` on macOS).
- **Process targeting**: The debug scripts only write to `/tmp/` and cannot modify the target process's state—they only read stack frames.

## Further Reading

For a detailed write-up on the techniques used in this skill, including a real-world example and the motivation behind combining Python 3.14's remote debugging with LLM assistance, see:

**[Debugging Stuck Processes with Python 3.14 and LLM Assistance](https://adamhadani.github.io/debugging/python/llm/2026/01/23/debugging-stuck-processes-python314-llm.html)**

## License

MIT License - see [LICENSE](LICENSE)

## Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.
