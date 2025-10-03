# gui/logger.py
import datetime

from colorama import Fore, Style, init
init(autoreset=True)

COLOR_MAP = {
    "INFO": Fore.CYAN,
    "WARNING": Fore.YELLOW,
    "ERROR": Fore.RED,
    "SUCCESS": Fore.GREEN
}

def log_message(message: str, level: str = "INFO", color: str = None):
    timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    prefix = f"[{level}]"
    formatted = f"{timestamp} {prefix} {message}"
    color_code = COLOR_MAP.get(level.upper(), "")
    print(f"{color_code}{formatted}{Style.RESET_ALL}")
