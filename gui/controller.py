import threading
import time

class Controller:
    def __init__(self, download_dir="downloads"):
        self._continue = True
        self.paused = False
        self.lock = threading.Lock()
        self.download_dir = download_dir

        # Progress tracking
        self._progress = 0.0
        self._tracks_done = 0
        self._total_tracks = 0
        self._start_time = None

    # --- Control Flags ---
    def should_continue(self):
        with self.lock:
            return self._continue

    def cancel(self):
        with self.lock:
            self._continue = False

    def pause(self):
        with self.lock:
            self.paused = True

    def resume(self):
        with self.lock:
            self.paused = False

    # --- Progress Tracking ---
    def start_batch(self, total_tracks: int):
        self._total_tracks = total_tracks
        self._tracks_done = 0
        self._progress = 0.0
        self._start_time = time.time()

    def update_progress(self, fraction: float):
        """fraction = tracks_done / total_tracks"""
        with self.lock:
            self._progress = fraction

    def update_speed(self, tracks_done: int, total_tracks: int):
        with self.lock:
            self._tracks_done = tracks_done
            self._total_tracks = total_tracks

    def get_status(self):
        """Return current progress, speed, and ETA for GUI display."""
        with self.lock:
            if not self._start_time or self._tracks_done == 0:
                return {"progress": self._progress, "eta": None, "speed": None}

            elapsed = time.time() - self._start_time
            speed = self._tracks_done / elapsed  # tracks per second
            remaining = self._total_tracks - self._tracks_done
            eta = remaining / speed if speed > 0 else None

            return {
                "progress": self._progress,
                "speed": speed * 60,  # tracks per minute
                "eta": eta
            }
