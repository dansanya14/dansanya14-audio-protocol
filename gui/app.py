import threading
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from tkinter.scrolledtext import ScrolledText
import json
import os
import shutil, subprocess, sys

from config import DOWNLOAD_DIR
from downloader.pipeline import FAILED_TRACKS_FILE, download_tracks
from downloader.spotify import parse_exportify_csv
from downloader.youtube import (
    resolve_youtube_url,
    download_audio,
    is_playlist_url,
    get_playlist_items,
    is_channel_url,
    get_channel_items,
)
from gui.logger import Logger
from gui.controller import Controller


class AudioProtocolApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Dansanya14 Audio Protocol")
        self.failed_tracks = []
        self.tracks = []

        # --- Controller ---
        self.controller = Controller(download_dir=DOWNLOAD_DIR)

        # --- Tabs ---
        notebook = ttk.Notebook(root)
        notebook.pack(expand=True, fill="both")

        self._build_spotify_tab(notebook)
        self._build_youtube_tab(notebook)

        # --- Global Progress + Status ---
        self.progress = ttk.Progressbar(root, orient="horizontal", length=600, mode="determinate")
        self.progress.pack(padx=10, pady=(0, 5))

        self.status_var = tk.StringVar(value="Idle")
        self.status_label = tk.Label(root, textvariable=self.status_var, anchor="w")
        self.status_label.pack(fill="x", padx=10, pady=(0, 5))

        # Load failed tracks
        self.load_failed_tracks()

        # Start periodic status updates
        self.update_status_bar()

    # ---------------------------
    # Spotify Tab
    # ---------------------------
    def _build_spotify_tab(self, notebook):
        spotify_frame = tk.Frame(notebook)
        notebook.add(spotify_frame, text="Spotify CSV")

        self.log_box = ScrolledText(spotify_frame, height=20, width=80, state="disabled")
        self.log_box.pack(padx=10, pady=10)
        self.logger = Logger(self.log_box)

        button_frame = tk.Frame(spotify_frame)
        button_frame.pack(pady=5)

        self.start_btn = tk.Button(button_frame, text="Start", command=self.start_download)
        self.start_btn.grid(row=0, column=0, padx=5)

        self.pause_btn = tk.Button(button_frame, text="Pause", command=self.controller.pause)
        self.pause_btn.grid(row=0, column=1, padx=5)

        self.resume_btn = tk.Button(button_frame, text="Resume", command=self.controller.resume)
        self.resume_btn.grid(row=0, column=2, padx=5)

        self.cancel_btn = tk.Button(button_frame, text="Cancel", command=self.controller.cancel)
        self.cancel_btn.grid(row=0, column=3, padx=5)

        self.retry_btn = tk.Button(button_frame, text="Retry Failed", command=self.retry_failed, state="disabled")
        self.retry_btn.grid(row=0, column=4, padx=5)

        self.dir_btn = tk.Button(button_frame, text="Select Download Folder", command=self.select_folder)
        self.dir_btn.grid(row=0, column=5, padx=5)

        self.clear_failed_btn = tk.Button(button_frame, text="Clear Failed List", command=self.clear_failed, state="disabled")
        self.clear_failed_btn.grid(row=0, column=6, padx=5)

        self.csv_btn = tk.Button(button_frame, text="Load CSV", command=self.load_csv)
        self.csv_btn.grid(row=0, column=7, padx=5)

        self.clear_spotify_log_btn = tk.Button(button_frame, text="Clear Log", command=self.clear_spotify_log)
        self.clear_spotify_log_btn.grid(row=0, column=8, padx=5)

    # ---------------------------
    # YouTube Tab
    # ---------------------------
    def _build_youtube_tab(self, notebook):
        youtube_frame = tk.Frame(notebook)
        notebook.add(youtube_frame, text="YouTube")

        yt_label = tk.Label(youtube_frame, text="Enter YouTube URL or search query:")
        yt_label.pack(pady=(10, 0))

        self.youtube_entry = tk.Entry(youtube_frame, width=80)
        self.youtube_entry.pack(padx=10, pady=5)

        yt_button = tk.Button(youtube_frame, text="Download", command=self.start_youtube_download)
        yt_button.pack(pady=5)

        self.clear_youtube_log_btn = tk.Button(youtube_frame, text="Clear Log", command=self.clear_youtube_log)
        self.clear_youtube_log_btn.pack(pady=(0, 5))

        self.youtube_log = ScrolledText(youtube_frame, height=15, width=80, state="disabled")
        self.youtube_log.pack(padx=10, pady=10)
        self.youtube_logger = Logger(self.youtube_log)

    # ---------------------------
    # Spotify Actions
    # ---------------------------
    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.controller.download_dir = folder
            self.logger.log_message(f"Download location set to: {folder}", "INFO")

    def load_csv(self):
        file_path = filedialog.askopenfilename(
            title="Select Exportify CSV",
            filetypes=[("CSV Files", "*.csv")]
        )
        if not file_path:
            return
        try:
            self.tracks = parse_exportify_csv(file_path)
            self.logger.log_message(f"Loaded {len(self.tracks)} tracks from {file_path}", "INFO")
        except Exception as e:
            self.logger.log_message(f"Failed to load CSV: {e}", "ERROR")

    def start_download(self):
        if not self.tracks:
            self.logger.log_message("No tracks loaded. Please load a CSV first.", "WARNING")
            return
        self.failed_tracks = []
        self.update_failed_buttons()
        self.logger.log_message("Starting batch download...", "INFO")
        threading.Thread(target=self._run_pipeline, daemon=True).start()

    def _run_pipeline(self):
        results = download_tracks(self.tracks, self.controller, self.logger)
        self.failed_tracks = results["failed"]
        self.update_failed_buttons()
        saved_path = self.logger.save_to_file(prefix="spotify")
        if saved_path:
            self.logger.log_message(f"Log saved to {saved_path}", "INFO")

    def retry_failed(self):
        if not self.failed_tracks:
            self.logger.log_message("No failed tracks to retry.", "WARNING")
            return
        self.logger.log_message("Retrying failed tracks...", "INFO")
        threading.Thread(
            target=lambda: download_tracks(self.failed_tracks, self.controller, self.logger),
            daemon=True
        ).start()

    def clear_failed(self):
        self.failed_tracks = []
        if os.path.exists(FAILED_TRACKS_FILE):
            try:
                os.remove(FAILED_TRACKS_FILE)
                self.logger.log_message("Cleared failed track list and deleted failed_tracks.json", "INFO")
            except Exception as e:
                self.logger.log_message(f"Could not delete failed_tracks.json: {e}", "ERROR")
        else:
            self.logger.log_message("No failed track file found to clear.", "WARNING")
        self.update_failed_buttons()

    def clear_spotify_log(self):
        self.log_box.config(state="normal")
        self.log_box.delete("1.0", tk.END)
        self.log_box.config(state="disabled")
        self.logger.log_message("Spotify log cleared.", "INFO")

    # ---------------------------
    # YouTube Actions
    # ---------------------------
    def start_youtube_download(self):
        query = self.youtube_entry.get().strip()
        if not query:
            self.youtube_logger.log_message("Please enter a YouTube URL or search query.", "WARNING")
            return

        self.youtube_logger.log_message(f"Resolving YouTube input: {query}", "INFO")

        def run():
            url = resolve_youtube_url(query, self.youtube_logger)
            if not url:
                self.youtube_logger.log_message("Could not resolve YouTube input.", "ERROR")
                return

            if is_channel_url(url):
                urls = get_channel_items(url, self.youtube_logger)
                self.youtube_logger.log_message(f"Detected channel with {len(urls)} items (excluding Shorts).", "INFO")
            elif is_playlist_url(url):
                urls = get_playlist_items(url, self.youtube_logger)
                self.youtube_logger.log_message(f"Detected playlist with {len(urls)} items.", "INFO")
            else:
                urls = [url]

            total = len(urls)
            for idx, u in enumerate(urls, start=1):
                self.youtube_logger.log_message(f"({idx}/{total}) Downloading {u}", "INFO")
                output_template = os.path.join(self.controller.download_dir, "%(title)s.%(ext)s")
                success = download_audio(u, output_template, self.youtube_logger)
                if success is None:
                    self.youtube_logger.log_message(f"Failed: {u}", "ERROR")
                else:
                    self.youtube_logger.log_message(f"Completed: {u}", "SUCCESS")

                self.controller.update_progress(idx / total)
                self.controller.update_speed(tracks_done=idx, total_tracks=total)

                        self.youtube_logger.log_message("YouTube run complete.", "INFO")
            saved_path = self.youtube_logger.save_to_file(prefix="youtube")
            if saved_path:
                self.youtube_logger.log_message(f"Log saved to {saved_path}", "INFO")

        threading.Thread(target=run, daemon=True).start()

    def clear_youtube_log(self):
        self.youtube_log.config(state="normal")
        self.youtube_log.delete("1.0", tk.END)
        self.youtube_log.config(state="disabled")
        self.youtube_logger.log_message("YouTube log cleared.", "INFO")

    # ---------------------------
    # Failed Track Management
    # ---------------------------
    def load_failed_tracks(self):
        if os.path.exists(FAILED_TRACKS_FILE):
            try:
                with open(FAILED_TRACKS_FILE, "r", encoding="utf-8") as f:
                    self.failed_tracks = json.load(f)
                self.logger.log_message(
                    f"Loaded {len(self.failed_tracks)} failed track(s) from previous session.",
                    "INFO"
                )
            except Exception as e:
                self.logger.log_message(f"Could not load failed tracks: {e}", "ERROR")
                self.failed_tracks = []
        else:
            self.failed_tracks = []
        self.update_failed_buttons()

    def update_failed_buttons(self):
        if self.failed_tracks:
            self.retry_btn.config(state="normal")
            self.clear_failed_btn.config(state="normal")
        else:
            self.retry_btn.config(state="disabled")
            self.clear_failed_btn.config(state="disabled")

    # ---------------------------
    # Status Bar Updates
    # ---------------------------
    def update_status_bar(self):
        status = self.controller.get_status()
        if status["progress"] > 0:
            prog = f"{status['progress']*100:.1f}%"
            eta = f" ETA: {status['eta']:.1f}s" if status["eta"] else ""
            speed = f" Speed: {status['speed']:.2f} tracks/min" if status["speed"] else ""
            self.status_var.set(f"Progress: {prog}{eta}{speed}")
            self.progress["value"] = status["progress"] * 100
        else:
            self.status_var.set("Idle")
            self.progress["value"] = 0
        # schedule next update
        self.root.after(1000, self.update_status_bar)


# ---------------------------
# Dependency Verification
# ---------------------------
def verify_dependencies():
    missing = []
    if not shutil.which("yt-dlp"):
        missing.append("yt-dlp")
    if not shutil.which("ffmpeg"):
        missing.append("ffmpeg")

    if missing:
        msg = f"Missing dependencies: {', '.join(missing)}.\n\nInstall now?"
        root = tk.Tk()
        root.withdraw()
        if messagebox.askyesno("Dependencies Missing", msg):
            for dep in missing:
                if dep == "yt-dlp":
                    subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp"])
                elif dep == "ffmpeg":
                    messagebox.showinfo(
                        "Manual Install Required",
                        "Please install ffmpeg manually from https://ffmpeg.org/download.html"
                    )
        root.destroy()
        return verify_dependencies()
    return True


def run_app():
    if not verify_dependencies():
        return
    root = tk.Tk()
    app = AudioProtocolApp(root)
    root.mainloop()
