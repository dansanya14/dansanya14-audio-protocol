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

Run the launcher script:
python run.py

🖱️ Usage

git clone https://github.com/dansanya14/dansanya14-audio-protocol.git
cd dansanya14-audio-protocol

🧠 Architecture

dansanya14-audio-protocol/
├── config.py
├── downloader/
│   └── _init_.py
│   ├── spotify.py
│   ├── youtube.py
│   ├── metadata.py
│   ├── logger.py
│   ├── lyrics.py
│   ├── thumbnails.py
│   ├── organizer.py
│   ├── retry.py
│   ├── cache.py
│   └── config.py
│   └── controller.py
│   └── debug.py
├── gui/
│   └── _init_.py
│   └── cache_cleaner.py
│   └── controller.py
│   └── interface.py
│   ├── main.py
│   └── logger.py
├── LICENSE.py
├── Requirements.py
├── setup.py
├── startup_check.py
├── run.py
├── README.md

    Modular design: Each feature lives in its own focused module.

    Fallback-first: Works even without API keys or manual setup.

    Installer-grade polish: Setup script checks dependencies and guides the user.

Demo

Here’s what the Dansanya14 Audio Protocol GUI looks like in action:

+-------------------------------------------------------------+
| Dansanya14 Audio Protocol                                   |
+-------------------------------------------------------------+
| Platform: [ Spotify ▼ ]   Playlist/Video URL: [__________]  |
+-------------------------------------------------------------+
| [ Start ] [ Pause ] [ Resume ] [ Cancel ]                   |
+-------------------------------------------------------------+

+-------------------------------------------------------------+

+-------------------------------------------------------------+


### What you see:
- **Progress bar** with percentage complete  
- **Status label** (Idle, Downloading, Paused, Cancelled, Complete, Error)  
- **Elapsed time, ETA, and Speed** (MB/s for YouTube, tracks/minute for Spotify)  
- **Real‑time logs** with color‑coded messages (blue INFO, green SUCCESS, orange WARNING, red ERROR)  

---

### 🎥 Typical Workflow
1. Paste a Spotify playlist or YouTube link.  
2. Hit **Start** — the GUI stays responsive while downloads run in the background.  
3. Watch logs update in real time with thumbnails, metadata, and lyrics embedding.  
4. Pause, resume, or cancel anytime.  
5. Enjoy clean, tagged FLAC files with embedded cover art and captions.  

