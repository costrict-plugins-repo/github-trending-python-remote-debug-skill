"""
Remote debugging script for gevent-based processes (e.g., Celery workers with -P gevent).

This script uses gc.get_objects() to find all Greenlet objects since
sys._current_frames() only shows OS threads, not gevent greenlets.

Usage:
    sudo python3.14 -c "import sys; sys.remote_exec(<PID>, 'debug_gevent.py')"
    cat /tmp/debug_gevent_<PID>.txt

Output: /tmp/debug_gevent_<PID>.txt (PID of target process)
"""

import gc
import io
import os
import sys
import traceback
from datetime import datetime


pid = os.getpid()
output_file = f"/tmp/debug_gevent_{pid}.txt"
output = io.StringIO()

output.write("\n" + "=" * 80 + "\n")
output.write("REMOTE DEBUG: Gevent greenlet stack traces\n")
output.write("=" * 80 + "\n\n")

output.write(f"PID: {pid}\n")
output.write(f"Timestamp: {datetime.now().isoformat()}\n")
output.write(f"Python: {sys.version}\n")
output.write(f"Executable: {sys.executable}\n\n")

try:
    import gevent
    from greenlet import greenlet as raw_greenlet

    output.write(f"Gevent version: {gevent.__version__}\n\n")

    # Get the hub info
    hub = gevent.get_hub()
    output.write(f"Hub: {hub}\n")
    output.write(f"Hub loop pending count: {hub.loop.pendingcnt}\n\n")

    # Find all Greenlet objects via garbage collector
    greenlets = [obj for obj in gc.get_objects() if isinstance(obj, gevent.Greenlet)]
    output.write(f"Found {len(greenlets)} Greenlet objects\n\n")

    for i, g in enumerate(greenlets):
        output.write(f"\n--- Greenlet {i}: {g!r} ---\n")
        output.write(f"  Dead: {g.dead}, Started: {g.started}, Ready: {g.ready()}\n")

        # Get stack trace if greenlet has a frame
        if hasattr(g, "gr_frame") and g.gr_frame is not None:
            output.write("  Stack trace:\n")
            for line in traceback.format_stack(g.gr_frame):
                output.write("    " + line)

    # Also check raw greenlets (hub, etc.)
    raw_greenlets = [
        obj for obj in gc.get_objects() if isinstance(obj, raw_greenlet) and not isinstance(obj, gevent.Greenlet)
    ]
    output.write(f"\nFound {len(raw_greenlets)} raw greenlet objects\n")
    for i, g in enumerate(raw_greenlets[:5]):
        output.write(f"\n--- Raw Greenlet {i}: {g!r} ---\n")
        if hasattr(g, "gr_frame") and g.gr_frame is not None:
            for line in traceback.format_stack(g.gr_frame):
                output.write("    " + line)

except ImportError as e:
    output.write(f"Gevent not available in target process: {e}\n")
    output.write("This script requires the target process to have gevent installed.\n")
except Exception as e:
    output.write(f"\nError during debug: {e}\n")
    output.write(traceback.format_exc())

with open(output_file, "w") as f:
    f.write(output.getvalue())
