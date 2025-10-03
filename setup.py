import subprocess
import sys
import os
import urllib.request
import zipfile
import importlib.metadata

REQUIRED_PACKAGES = [
    "spotipy", "yt-dlp", "mutagen", "lyricsgenius", "pygame", "requests", "colorama"
]

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

INSTALL_RESULTS = []

def install_packages():
    print("\n📦 Installing required Python packages...")
    for package in REQUIRED_PACKAGES:
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)
            version = importlib.metadata.version(package)
            INSTALL_RESULTS.append((package, version, "✅"))
        except Exception as e:
            INSTALL_RESULTS.append((package, "—", f"❌ {str(e).splitlines()[0]}"))

def try_colorama():
    try:
        from colorama import Fore, Style, init
        init(autoreset=True)
        return Fore, Style
    except ImportError:
        class Dummy:
            RED = GREEN = YELLOW = CYAN = RESET_ALL = ""
        return Dummy(), Dummy()

Fore, Style = try_colorama()

def download_yt_dlp():
    if not os.path.exists("yt-dlp.exe"):
        print(Fore.CYAN + "\n⬇️ Downloading yt-dlp.exe...")
        try:
            urllib.request.urlretrieve(
                "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe",
                "yt-dlp.exe"
            )
            INSTALL_RESULTS.append(("yt-dlp.exe", "latest", Fore.GREEN + "✅"))
        except Exception as e:
            INSTALL_RESULTS.append(("yt-dlp.exe", "—", Fore.RED + f"❌ {str(e).splitlines()[0]}"))
    else:
        INSTALL_RESULTS.append(("yt-dlp.exe", "already exists", Fore.GREEN + "✅"))

def download_ffmpeg():
    if not os.path.exists("ffmpeg"):
        print(Fore.CYAN + "\n⬇️ Downloading ffmpeg...")
        try:
            urllib.request.urlretrieve(
                "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip",
                "ffmpeg.zip"
            )
            with zipfile.ZipFile("ffmpeg.zip", "r") as zip_ref:
                zip_ref.extractall("ffmpeg")
            os.remove("ffmpeg.zip")
            INSTALL_RESULTS.append(("ffmpeg", "latest", Fore.GREEN + "✅"))
        except Exception as e:
            INSTALL_RESULTS.append(("ffmpeg", "—", Fore.RED + f"❌ {str(e).splitlines()[0]}"))
    else:
        INSTALL_RESULTS.append(("ffmpeg", "already exists", Fore.GREEN + "✅"))

def check_required_files():
    print(Fore.CYAN + "\n📁 Checking required source files...")
    missing = [f for f in REQUIRED_FILES if not os.path.isfile(f)]
    if missing:
        print(Fore.RED + "\n❌ Missing source files:")
        for f in missing:
            print(Fore.RED + f" - {f}")
        print(Fore.YELLOW + "\nPlease restore these files before running the app.")
        sys.exit(1)
    else:
        print(Fore.GREEN + "✅ All source files found.")

def show_summary():
    print(Fore.CYAN + "\n📊 Installation Summary:\n")
    print(Fore.YELLOW + f"{'Component':<20} {'Version':<15} {'Status'}")
    print(Fore.YELLOW + "-" * 50)
    for name, version, status in INSTALL_RESULTS:
        print(f"{name:<20} {version:<15} {status}")
    print(Fore.YELLOW + "-" * 50)

def prompt_relaunch():
    print(Fore.CYAN + "\n🎉 Setup complete.")
    choice = input("Do you want to launch the app now? (y/n): ").strip().lower()
    if choice == "y":
        print(Fore.GREEN + "\n🚀 Launching main.py...\n")
        subprocess.run([sys.executable, "main.py"])
    else:
        print(Fore.YELLOW + "\n👋 Setup finished. You can run main.py later.")
        sys.exit()

def main():
    install_packages()
    download_yt_dlp()
    download_ffmpeg()
    check_required_files()
    show_summary()
    prompt_relaunch()

if __name__ == "__main__":
    main()
