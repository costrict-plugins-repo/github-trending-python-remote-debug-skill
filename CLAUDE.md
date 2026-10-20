# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Claude Code plugin/skill for debugging running Python processes using Python 3.14+ `sys.remote_exec()`. It injects debugging scripts into live processes to get stack traces without stopping them.

## Repository Structure

```
.claude-plugin/          # Plugin metadata (plugin.json, marketplace.json)
skills/debug-remote/     # The skill definition
  SKILL.md              # Skill instructions shown to Claude when invoked
  scripts/              # Debug scripts injected into target processes
    debug_threads.py    # Stack traces from all OS threads
    debug_gevent.py     # Stack traces from gevent greenlets
```

## Testing Changes

### Load the plugin locally
```bash
claude --plugin-dir .
```

### Test the skill
```bash
# In Claude Code, run:
/python-remote-debug-skill:debug-remote
```

### Test debug scripts manually
```bash
# Start a test process
python3.14 -c "import time; time.sleep(60)" &
PID=$!

# Test thread debugging
sudo python3.14 -c "import sys; sys.remote_exec($PID, 'skills/debug-remote/scripts/debug_threads.py')"
cat /tmp/debug_threads_$PID.txt

# Clean up
kill $PID
```

## Key Technical Details

- **sys.remote_exec()** executes scripts asynchronously at the next "safe point" in Python's interpreter
- Output files include target PID to avoid overwrites: `/tmp/debug_threads_<PID>.txt`, `/tmp/debug_gevent_<PID>.txt`
- For gevent processes, `sys._current_frames()` only shows OS threads; use `gc.get_objects()` to find Greenlet objects
- Requires **sudo on macOS** for `com.apple.system-task-ports` privilege

## Releasing

When bumping the version, update **both** JSON files in `.claude-plugin/`:
- `plugin.json` - the `version` field
- `marketplace.json` - the `metadata.version` field

## Code Style for Debug Scripts

- Keep scripts simple and self-contained (they run in the target process's context)
- Always write output to `/tmp/` files
- Wrap code in try/except to capture errors
- Update SKILL.md when adding new capabilities
