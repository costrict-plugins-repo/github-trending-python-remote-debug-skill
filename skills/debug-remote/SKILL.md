---
name: debug-remote
description: Debug running Python processes using Python 3.14+ sys.remote_exec(). Inject debugging scripts to get stack traces from stuck processes, including gevent-based Celery workers with greenlet introspection.
---

# Python 3.14+ Remote Process Debugging

This skill helps you debug running Python processes by injecting debugging scripts using `sys.remote_exec()`. This is especially useful for diagnosing stuck or misbehaving processes without stopping them.

## Prerequisites

- **Python 3.14+** (both debugger and target process)
- **sudo access on macOS** (requires elevated privileges for `com.apple.system-task-ports`)
- Target process must be running Python and reach a "safe point" for script execution

## Basic Usage: Debug Any Python Process

### Step 1: Find the target process ID

```bash
# Find by name pattern
pgrep -f "python.*my_script"

# More detailed view
ps aux | grep python
```

### Step 2: Use the provided debug script

The skill includes ready-to-use scripts in `skills/debug-remote/scripts/`:
- `debug_threads.py` - For standard Python processes
- `debug_gevent.py` - For gevent-based processes (Celery with `-P gevent`)

### Step 3: Inject the script

```bash
sudo python3.14 -c "import sys; sys.remote_exec(<PID>, '/path/to/debug_threads.py')"
```

### Step 4: Read the output

Output files are named with the target PID to avoid overwrites when debugging multiple processes:

```bash
cat /tmp/debug_threads_<PID>.txt
```

## Debugging Celery Workers with gevent

Celery workers using the gevent pool (`-P gevent`) require special handling because they use greenlets (cooperative threads) instead of OS threads.

**The Problem**: `sys._current_frames()` only shows OS threads, not gevent greenlets. A gevent worker typically shows just one OS thread (the hub) even when many greenlets are active.

### Gevent-Aware Debug Script

Use the provided `debug_gevent.py` script which:
- Discovers all Greenlet objects via `gc.get_objects()`
- Reports hub status and pending event count
- Shows stack traces for active greenlets
- Distinguishes between gevent Greenlets and raw greenlets

Output is written to `/tmp/debug_gevent_<PID>.txt`.

### Finding the Right Celery Worker Process

When using `watchmedo` for auto-restart, multiple processes exist:

```bash
ps -p $(pgrep -f "celery.*worker" | tr '\n' ',') -o pid,ppid,command
```

Typical output:
```
PID   PPID  COMMAND
79130 72223 .../watchmedo auto-restart ...  # Parent watcher - NOT this one
79136 79130 .../celery -A myapp.celery worker ...  # Actual worker - USE THIS
79147 72223 tail -f celery-worker.log  # Log tailer
```

### Quick Debug Commands

One-liner to debug a stuck Celery worker:

```bash
PID=$(pgrep -f "celery.*worker" | head -1) && \
  echo "Attaching to PID $PID" && \
  sudo python3.14 -c "import sys; sys.remote_exec($PID, 'debug_gevent.py')" && \
  sleep 1 && cat /tmp/debug_gevent_$PID.txt
```

### Killing a Stuck Worker

If you need to kill a stuck worker (not the watchmedo parent):

```bash
kill -9 $(ps -p $(pgrep -f "celery.*worker") -o pid,command | grep -v watchmedo | awk 'NR>1 {print $1}')
```

## Key Points

- The script executes **asynchronously** at the next "safe point" in Python's interpreter
- Output must be written to a **file** since stdout/stderr may not be visible
- The call returns immediately; script execution happens in the target process
- If the process is blocked in C code (not Python), the script won't execute until Python resumes

## Common Issues Revealed by This Technique

1. **Stuck in external library**: Stack trace shows waiting in third-party code (e.g., `yfinance/multi.py:158 → _time.sleep`)
2. **ThreadPoolExecutor deadlock**: LangGraph's ToolNode uses `concurrent.futures.ThreadPoolExecutor` which can conflict with gevent
3. **Missing timeouts**: HTTP clients or external calls without timeout parameters
4. **Celery time limits not enforced**: gevent's cooperative scheduling means time limits only work if greenlets yield

## When to Use This Skill

Use `/python-remote-debug-skill:debug-remote` when:
- A Python process appears stuck or unresponsive
- You need to understand what a running process is doing without stopping it
- Celery tasks are timing out and you need to identify where they're blocked
- You suspect a deadlock or infinite loop in production code
