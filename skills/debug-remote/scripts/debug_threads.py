"""
Remote debugging script to get stack traces from all OS threads.

Usage:
    sudo python3.14 -c "import sys; sys.remote_exec(<PID>, 'debug_threads.py')"
    cat /tmp/debug_threads_<PID>.txt

Output: /tmp/debug_threads_<PID>.txt (PID of target process)
"""

import io
import os
import sys
import threading
import traceback
from datetime import datetime


pid = os.getpid()
output_file = f"/tmp/debug_threads_{pid}.txt"
output = io.StringIO()

try:
    output.write("\n" + "=" * 80 + "\n")
    output.write("REMOTE DEBUG: Stack traces for all threads\n")
    output.write("=" * 80 + "\n\n")

    output.write(f"PID: {pid}\n")
    output.write(f"Timestamp: {datetime.now().isoformat()}\n")
    output.write(f"Python: {sys.version}\n")
    output.write(f"Executable: {sys.executable}\n\n")

    frames = sys._current_frames()
    threads = {t.ident: t.name for t in threading.enumerate()}
    output.write(f"Found {len(frames)} thread(s)\n\n")

    for thread_id, frame in frames.items():
        thread_name = threads.get(thread_id, "Unknown")
        output.write(f"\n--- Thread {thread_id} ({thread_name}) ---\n")
        output.write("".join(traceback.format_stack(frame)))
        output.write("\n")

except Exception as e:
    output.write(f"\nError during debug: {e}\n")
    output.write(traceback.format_exc())

# Write to file (can't rely on stdout in remote process)
with open(output_file, "w") as f:
    f.write(output.getvalue())
