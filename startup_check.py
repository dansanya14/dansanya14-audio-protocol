import importlib.util
import subprocess
import sys
import os
import shutil

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
except ImportError:
    print("\n⚠️ 'colorama' not found. Output will be plain text.")
    class Fore:
        RED = ""
        GREEN = ""
        YELLOW = ""
        CYAN = ""
    class Style:
        RESET_ALL = ""

REQUIRED_MODULES = [
    "spotipy", "yt_dlp", "mutagen", "lyricsgenius", "pygame", "requests", "colorama"
]

REQUIRED_TOOLS = {
    "yt-dlp": "yt-dlp.exe",
    "ffmpeg": os.path.join("ffmpeg", "ffmpeg-8.0-essentials_build", "bin", "ffmpeg.exe"),
    "ffprobe": os.path.join("ffmpeg", "ffmpeg-8.0-essentials_build", "bin", "ffprobe.exe")
}

REQUIRED_FILES = [
    "gui/controller.py",
    "gui/interface.py",
    "downloader/spotify.py",
    "downloader/youtube.py",
    "downloader/metadata.py",
    "downloader/lyrics.py",
    "downloader/organizer.py",
    "startup_check.py",
    "main.py"
]

def missing_modules():
    return [mod for mod in REQUIRED_MODULES if importlib.util.find_spec(mod.replace("-", "_")) is None]

def missing_tools():
    missing = []
    for tool, local_path in REQUIRED_TOOLS.items():
        if not shutil.which(tool) and not os.path.exists(local_path):
            missing.append(tool)
    return missing

def check_files():
    return [f for f in REQUIRED_FILES if not os.path.isfile(f)]

def get_ffmpeg_location():
    if shutil.which("ffmpeg") and shutil.which("ffprobe"):
        return None  # Global install
    local_bin = os.path.dirname(REQUIRED_TOOLS["ffmpeg"])
    if os.path.exists(REQUIRED_TOOLS["ffmpeg"]) and os.path.exists(REQUIRED_TOOLS["ffprobe"]):
        return local_bin
    return None

def offer_setup(missing_modules, missing_tools, missing_files):
    print(Fore.RED + "\n❌ Missing dependencies detected:" + Style.RESET_ALL)
    if missing_modules:
        print(Fore.YELLOW + f" - Python packages: {', '.join(missing_modules)}")
    if missing_tools:
        print(Fore.YELLOW + f" - Tools: {', '.join(missing_tools)}")
    if missing_files:
        print(Fore.YELLOW + f" - Source files: {', '.join(missing_files)}")
    print(Fore.CYAN + "\nYou can run setup.py to install and fix everything.")
    choice = input(Fore.GREEN + "Run setup.py now? (y/n): ").strip().lower()
    if choice == "y":
        subprocess.run([sys.executable, "setup.py"])
        print(Fore.GREEN + "\n✅ Setup complete. Relaunching main.py...\n")
        if os.path.exists("main.py"):
            subprocess.run([sys.executable, "main.py"])
        else:
            print(Fore.RED + "main.py not found. Cannot relaunch.")
        sys.exit()

def run_startup_check(auto=False):
    missing_mods = missing_modules()
    missing_tools_list = missing_tools()
    missing_files_list = check_files()

    if missing_mods or missing_tools_list or missing_files_list:
        if auto:
            subprocess.run([sys.executable, "setup.py"])
            subprocess.run([sys.executable, "main.py"])
            sys.exit()
        else:
            offer_setup(missing_mods, missing_tools_list, missing_files_list)

if __name__ == "__main__":
    run_startup_check()
