# 🎧 Dansanya14's Audio Protocol

A powerful, user-friendly media automation tool that downloads and organizes Spotify and YouTube playlists with rich metadata, FLAC conversion, lyrics embedding, and a polished GUI.

---

🚀 Features
Feature	Status	Description
🎶 Spotify & YouTube Downloads	✅	Download full playlists using yt-dlp
🎧 FLAC Conversion	✅	Converts audio to lossless FLAC format
🏷️ Metadata Tagging	✅	Tags title, artist, album from source
📝 Lyrics Embedding	✅	Extracts and embeds YouTube captions
🖼️ Thumbnail Embedding	✅	Uses YouTube thumbnail as cover art
📊 Progress Bar	✅	Real-time visual feedback during download
⏸ Pause/Resume/Cancel	✅	Full control over batch downloads
🧼 Cache Cleaning	✅	Removes leftover temp files automatically
🧠 Fallback Logic	✅	Works without API keys using yt-dlp search
🪟 GUI with Logs	✅	Color-coded logs and status updates
🧪 Debug Overlay	✅	Shows resolved URLs, subtitle status, lyrics preview
🔁 Batch Support	✅	Handles full playlists with progress tracking

🖥️ Installation
Requirements

    Python 3.10+

    ffmpeg

    yt-dlp

    Spotify API credentials (optional)

Dependencies

pip install spotipy mutagen pillow requests

Setup

python setup.py

🖱️ Usage

    Launch the GUI:

    python gui/main.py

    Paste a Spotify playlist or YouTube video/playlist URL.

    Click Start to begin downloading.

    Watch the progress bar, logs, and cover art preview update in real time.

🧠 Architecture

dansanya14-audio-protocol/
├── config.py
├── downloader/
│   ├── spotify.py
│   ├── youtube.py
│   ├── metadata.py
│   ├── lyrics.py
│   ├── thumbnails.py
│   ├── retry.py
│   ├── cache.py
│   └── debug.py
├── gui/
│   ├── main.py
│   └── logger.py
├── setup.py
├── README.md

    Modular design: Each feature lives in its own focused module.

    Fallback-first: Works even without API keys or manual setup.

    Installer-grade polish: Setup script checks dependencies and guides the user.
