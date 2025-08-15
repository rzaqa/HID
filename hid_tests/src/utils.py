# hid_tests/src/utils.py
from __future__ import annotations

import time

import hash_wrapper as hw


def _wait_done(op_id: int, timeout_s: float = 5.0, interval_s: float = 0.05) -> bool:
    start = time.time()
    end = start + timeout_s
    while time.time() < end:
        try:
            running = hw.get_status(op_id)
            if running is False:
                print(
                    f"[DEBUG] Hashing completed in {time.time() - start:.2f}s"
                )  # For testing purpose, to see if file exceeds timeout
                return True
        except RuntimeError as e:
            print(f"[wait_done] Error: {e}")
        time.sleep(interval_s)
    print(f"[DEBUG] Hashing did NOT complete in time ({timeout_s}s)")
    return False
