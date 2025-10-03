# 🎧 Dansanya14's Audio Protocol

A powerful, user-friendly media automation tool that downloads and organizes Spotify and YouTube playlists with rich metadata, FLAC conversion, lyrics embedding, and a polished GUI.

---

## 🚀 Features

- 🎵 **Unified Downloader**: Supports Spotify playlists (via YouTube fallback) and direct YouTube links  
- 🎛️ **GUI with Real-Time Feedback**: Color-coded logs, progress bars, pause/resume/cancel controls  
- 🏷️ **Metadata Tagging**: FLAC conversion with full ID3 tags, album art, and genre detection   
- 📁 **Smart Organizer**: Auto-sorts files into artist/album folders with cleanup logic  
- 🧠 **Fallback-Ready**: Works even without API keys using search-based matching  
- 🧹 **Cache Cleaner**: Removes temp files and failed downloads  
- 🧪 **Robust Error Handling**: Retry logic, transparent logs, and graceful failure recovery  
- 🛠️ **Installer-Grade Setup**: Auto-installs packages, downloads tools, checks file integrity, and confirms success visually

---

## 📦 Requirements

### Python
- Python 3.9 or higher

### Python Packages
Installed automatically via `setup.py`:
- `spotipy`
- `yt-dlp`
- `mutagen`
- `lyricsgenius`
- `pygame`
- `requests`
-  'colorama'

### External Tools
Downloaded automatically if missing:
- `yt-dlp.exe`
- `ffmpeg` (Windows build from [gyan.dev](https://www.gyan.dev/ffmpeg))

---

## 🛠️ Setup Instructions 

1. **Clone the repo**  
   ```bash
   git clone https://github.com/dansanya14/dansanya14-audio-protocol.git
   cd dansanya14-audio-protocol

2. Run the setup script

	python setup.py

		This will:

			Download yt-dlp.exe and ffmpeg

			Install all required packages
			Check for critical source files

			Show a visual summary of what was installed

3. Launch the appAfter setup, you’ll be prompted to run the app:

python main.py

## 📁 Project Structure

dansanya14_audio_protocol/
├── main.py
├── setup.py
├── startup_check.py
├── gui/
│   ├── interface.py
│   ├── controller.py
│   ├── logger.py
│   ├── cache_cleaner.py
├── downloader/
│   ├── spotify.py
│   ├── youtube.py
│   ├── metadata.py
│   ├── lyrics.py
│   ├── organizer.py
│   ├── retry.py
├── assets/
│   └── temp/

## 🧠 How It Works

	Spotify Mode: Parses playlist → searches YouTube → downloads audio → tags + lyrics

	YouTube Mode: Direct link → downloads → tags + lyrics

	GUI: Shows live logs, progress, and lets you pause/resume/cancel

	Setup: Handles everything from package installs to tool downloads and file checks

## 💡 Tips

	Run main.py from the root folder — not inside gui/

	If you get ModuleNotFoundError, re-run setup.py to fix missing files

	Customize metadata logic in downloader/metadata.py

	Add your Genius API key in lyrics.py for full lyrics support