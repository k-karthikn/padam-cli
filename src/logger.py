from datetime import datetime
import os
from pathlib import Path


class Logger:
    FILE = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / "padam-cli/logs.txt"

    @classmethod
    def log(cls, message: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            cls.FILE.parent.mkdir(parents=True, exist_ok=True)
            with cls.FILE.open("a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] {message}\n")
        except OSError:
            pass
