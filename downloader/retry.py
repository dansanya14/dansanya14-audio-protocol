from typing import Callable
import time
from gui.logger import log_message
from config import RETRY_LIMIT

def retry(action: Callable, label: str, log_box=None) -> bool:
    for attempt in range(RETRY_LIMIT):
        try:
            action()
            log_message(log_box, f"{label} succeeded.", "SUCCESS") if log_box else print(f"✅ {label} succeeded.")
            return True
        except Exception as e:
            msg = f"{label} attempt {attempt+1} failed: {e}"
            log_message(log_box, msg, "ERROR") if log_box else print(f"❌ {msg}")
            time.sleep(2 ** attempt)
    final_msg = f"{label} skipped after {RETRY_LIMIT} attempts."
    log_message(log_box, final_msg, "WARNING") if log_box else print(f"⚠️ {final_msg}")
    return False
