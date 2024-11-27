import sys
import threading
import time
import traceback


def debug_threads(wait_time: float = 1):
    print("\nCurrent threads:")
    time.sleep(wait_time)

    for thread in threading.enumerate():
        if not thread.ident:
            continue
        print(f"\nThread {thread.name} ({thread.ident}):")
        frame = sys._current_frames().get(thread.ident)
        if frame:
            traceback.print_stack(frame)
