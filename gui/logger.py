import os
import datetime
import threading

class Logger:
    """
    Logger that fans out messages to:
      - Tkinter ScrolledText widget (GUI log box)
      - Console (stdout)
      - Auto-saved log files in /logs
    """

    def __init__(self, text_widget=None):
        self.text_widget = text_widget
        self._lock = threading.Lock()
        os.makedirs("logs", exist_ok=True)

        # Create a session log file for this run
        ts = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
        self.session_path = os.path.join("logs", f"session_{ts}.log")

    def log_message(self, message, level="INFO"):
        """
        Log a message to GUI, console, and append to session log file.
        """
        line = f"[{level}] {message}"

        # GUI
        if self.text_widget:
            self.text_widget.config(state="normal")
            self.text_widget.insert("end", line + "\n")
            self.text_widget.see("end")
            self.text_widget.config(state="disabled")

        # Console
        print(line)

        # File
        with self._lock:
            with open(self.session_path, "a", encoding="utf-8") as f:
                f.write(line + "\n")

    def save_to_file(self, prefix="session"):
        """
        Dump the current GUI log contents to a new timestamped file.
        This is in addition to the rolling session log.
        """
        if not self.text_widget:
            return None

        content = self.text_widget.get("1.0", "end").strip()
        if not content:
            return None

        os.makedirs("logs", exist_ok=True)
        ts = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
        path = os.path.join("logs", f"{prefix}_{ts}.log")

        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

        return path
