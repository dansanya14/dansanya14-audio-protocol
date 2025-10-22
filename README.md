🎧 Dansanya14's Audio Protocol

A user-friendly media automation tool that downloads and organizes Spotify and YouTube playlists with rich metadata, FLAC conversion.

==========================
 Requirements
==========================

yt-dlp>=2025.1.1
mutagen>=1.47.0        # for tagging metadata
tkinterdnd2>=0.3.0     # drag-and-drop support
Pillow>=10.0.0         # if you embed/resize thumbnails
requests>=2.31.0       # safe to include for any web fetches


tkinter itself ships with Python, but tkinterdnd2 is the extra package for drag‑and‑drop.

ffmpeg is an external binary, not pip‑installable — the dependency check handles that.

==========================
 Module Structure
==========================

│
├── main.py                # Entry point (starts GUI)
├── config.py              # Global settings (download dir, caption lang, etc.)
│
├── gui/
│   ├── app.py             # Main Tkinter/TkinterDnD2 GUI
│   ├── controller.py      # Pause/Resume/Cancel logic
│   ├── logger.py          # GUI log box + fan-out to console + file
│   └── widgets.py         # Custom widgets (progress bar, status line, etc.)
│
├── downloader/
│   ├── youtube.py         # YouTube resolver + download pipeline
│   ├── spotify.py         # Spotify CSV parser + resolver
│   ├── pipeline.py        # Unified _download_tracks() loop
│   ├── retry.py           # Retry logic + backoff
│   ├── metadata.py        # Tagging (title, artist, album)
│   ├── thumbnails.py      # Download + embed YouTube thumbnails
│   └── captions.py        # Extract + embed captions if owner-uploaded
│
├── utils/
│   ├── ffmpeg.py          # ffmpeg detection + validation
│   ├── cleaner.py         # Title cleaning, filename sanitization
│   └── files.py           # File existence checks, safe paths
│
└── logs/
    └── session-YYYY-MM-DD_HHMM.log   # Auto-saved logs

==========================
 Module Responsibilities
==========================


1. config.py: Stores defaults:
	DOWNLOAD_DIR
	CAPTION_LANG = "en"
	AUDIO_FORMAT = "flac"

	User’s chosen download folder overrides DOWNLOAD_DIR.

2. gui/
		app.py:	Builds the main window, tabs for YouTube/Spotify, drag-and-drop CSV, buttons (Start, Pause, Resume, Cancel, Retry Failed).
		
		controller.py: 
			should_continue()
			paused flag
			update_progress()
			update_speed()
		
		logger.py: log_message(level, message) → fans out to console, GUI, and file.
		
		widgets.py: Custom progress bar, thumbnail preview, status line.
	
3. downloader/
		youtube.py
			resolve_youtube_url(query_or_link)
			Handles video, playlist, channel (skips Shorts).
		spotify.py
			parse_exportify_csv(path) → returns track dicts.
		pipeline.py
			_download_tracks(tracks, controller, log_box)
			Applies retry, metadata, captions, thumbnails.
			Uses taxonomy for logging outcomes.
		retry.py
			retry(action, description, log_box) with exponential backoff.
		metadata.py
			tag_audio(file, tags) (title, artist, album).
		thumbnails.py
			download_thumbnail(video_id)
			embed_thumbnail(file, image_data)
		captions.py
			has_manual_subs(url, lang)
			extract_clean_captions(srt_path)
			embed_captions(file, text).

4. utils/
		ffmpeg.py
			get_ffmpeg_location()
			check_ffmpeg_installed() → GUI prompt if missing.
		cleaner.py
			clean_title(raw) → strips junk.
		files.py
			file_exists(track) → prevents duplicates.
			safe_filename(title).

5. logs/
    Auto-created per session.
    Rotating or timestamped filenames.
    Mirrors console + GUI logs.


==========================
 Usage  
==========================
	
1. Spotify

		Export your playlists with Exportify
		Load the CSV into the app.
		Hit Start to begin batch downloading.

2. YouTube

		Paste a video, playlist, or channel URL.
		Or enter a search query (first result is used).
		Hit Download.

3. Controls

		Pause, Resume, Cancel, Retry Failed.
        Select a custom download folder.
        View logs in‑app or open saved log files.
		
==========================
	High Level Flow
==========================
	
                ┌──────────────────────┐
                │   AudioProtocolApp   │
                └─────────┬────────────┘
                          │
                ┌─────────┴───────────┐
                │       Notebook       │
                └───────┬───────┬─────┘
                        │       │
        ┌───────────────┘       └────────────────┐
        ▼                                        ▼
┌───────────────────────┐              ┌───────────────────────┐
│     Spotify Tab       │              │     YouTube Tab       │
└─────────┬─────────────┘              └─────────┬─────────────┘
          │                                      │
   [Load CSV Button]                       [URL/Query Entry]
          │                                      │
   parse_exportify_csv()                  resolve_youtube_url()
          │                                      │
   Tracks loaded into list                ┌───────────────┐
          │                              │ is_playlist?   │
   [Start Button]                         └───────┬───────┘
          │                                      │
   download_tracks()                      get_playlist_items()
          │                                      │
   ┌──────┴─────────┐                          [Download Button]
   │ Pipeline Loop  │                                │
   │  - yt-dlp      │                        download_audio()
   │  - metadata    │                                │
   │  - captions    │                                │
   └──────┬─────────┘                                │
          │                                          │
   Progress + Status updated                 Progress + Status updated
          │                                          │
   Failed tracks saved (JSON)                Log auto-saved (per run)
          │                                          │
   Log auto-saved (per run)                  └─────────────────────────


==========================
 Key Connections
==========================


    Spotify Tab

        CSV → parsed into track list → pipeline downloads each track → metadata, thumbnails, captions embedded → failed tracks persisted → logs auto‑saved.

    YouTube Tab

        Input (URL or query) → resolved to video(s) or playlist → each item downloaded sequentially → progress updates → logs auto‑saved.

    Shared Components

        Controller: manages pause/resume/cancel and progress reporting.

        Logger: writes to GUI, console, and disk.

        Status Bar: global, always visible, updated every second.

==========================
 Log Outcome Taxonomy
==========================

Track-Level Outcomes
--------------------
SUCCESS
  - Prefix: [SUCCESS]
  - Meaning: Track fully downloaded, converted to FLAC, tagged, thumbnail + captions embedded if available.
  - Example: [SUCCESS] Downloaded and tagged: Thomas Bergersen - Elysium

FAILED
  - Prefix: [ERROR]
  - Meaning: Track could not be resolved, download failed, or conversion/tagging crashed.
  - Example: [ERROR] Failed to download: Audiomachine - Guardians at the Gate (no YouTube match)

SKIPPED
  - Prefix: [WARNING]
  - Meaning: Track intentionally skipped (already exists, user cancelled, or unsupported format like Shorts).
  - Example: [WARNING] File already exists: Two Steps From Hell - Victory.flac. Skipping.


Batch-Level Outcomes
--------------------
- Always log a summary line at the end of a batch:
  [INFO] Finished: X succeeded, Y failed, Z skipped

- If user selects "Retry failed only":
  [INFO] User selected: Retry failed only
  [INFO] Retrying N failed track(s)...
  ...
  [INFO] Retry finished: A succeeded, B skipped (already exists)


==========================
 GUI Representations
==========================
------------------
- Color coding:
  INFO    → Grey/Blue
  SUCCESS → Green
  WARNING → Orange
  ERROR   → Red

- Progress bar:
  Advances on SUCCESS or FAILED
  Skipped tracks log instantly but don’t advance the bar

- Status line:
  Shows current track outcome in real time
  e.g. "Downloading (3/10): Two Steps From Hell - Victory"
       then updates to "✅ Success" or "⚠️ Skipped"
