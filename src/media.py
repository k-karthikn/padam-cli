"""Safe filenames and optional external playback/download commands."""

import base64
import binascii
import shutil
import subprocess
import webbrowser
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit

from rich.console import Console


console = Console()


class Media:
    def __init__(self, url: str, title: str | None = None,
                 download_dir: str = "~/Downloads/", headers: dict | None = None):
        self.url = url
        self.title = title or "Movie"
        self.download_dir = Path(download_dir).expanduser()
        self.headers = headers or {}
        self.filename = self._generate_filename()
        self.output_path = self._available_path(self.download_dir / self.filename)

    @staticmethod
    def _safe_name(value: str) -> str:
        name = "".join(char if char.isalnum() or char in " ._-()" else "_" for char in value)
        return name.strip(" ._")[:120] or "Movie"

    def _generate_filename(self) -> str:
        url = urlsplit(self.url)
        query = parse_qs(url.query)
        candidate = query.get("path", [None])[0]
        if not candidate and query.get("dl"):
            try:
                raw = query["dl"][0]
                decoded = base64.urlsafe_b64decode(raw + "=" * (-len(raw) % 4)).decode("utf-8")
                candidate = parse_qs(decoded).get("path", [None])[0]
            except (ValueError, UnicodeError, binascii.Error):
                pass
        candidate = candidate or unquote(Path(url.path).name)
        suffix = Path(candidate).suffix.lower()
        if suffix not in {".mp4", ".mkv", ".webm", ".avi", ".mov", ".m4v"}:
            candidate = self._safe_name(self.title) + ".mp4"
        return self._safe_name(Path(candidate).stem) + Path(candidate).suffix.lower()

    @staticmethod
    def _available_path(path: Path) -> Path:
        number = 2
        original = path
        while path.exists():
            path = original.with_name(f"{original.stem} ({number}){original.suffix}")
            number += 1
        return path

    def _header_lines(self) -> list[str]:
        return [f"{key}: {value}" for key, value in self.headers.items()
                if "\r" not in key + value and "\n" not in key + value]

    def download(self) -> bool:
        options = [("yt-dlp", "yt-dlp"), ("ffmpeg", "ffmpeg"), ("Browser", None)]
        console.print("[cyan]Download with: 1) yt-dlp  2) ffmpeg  3) Browser[/cyan]")
        selection = console.input("Choose 1–3: ").strip()
        if selection not in {"1", "2", "3"}:
            console.print("[yellow]Invalid choice; no download started.[/yellow]")
            return False
        if selection == "3":
            if webbrowser.open(self.url):
                console.print("[green]Opened the media link in your browser.[/green]")
                return True
            console.print("[red]Could not open a browser. Copy this URL instead:[/red]")
            console.print(self.url)
            return False
        tool = options[int(selection) - 1][1]
        if not shutil.which(tool):
            console.print(f"[red]{tool} is not installed. Choose another method.[/red]")
            return False
        self.download_dir.mkdir(parents=True, exist_ok=True)
        if tool == "yt-dlp":
            command = [tool, self.url, "-o", str(self.output_path)]
            for header in self._header_lines():
                command.extend(["--add-header", header])
        else:
            command = [tool]
            if self.headers:
                command.extend(["-headers", "\r\n".join(self._header_lines()) + "\r\n"])
            command.extend(["-i", self.url, "-c", "copy", str(self.output_path)])
        try:
            subprocess.run(command, check=True)
            console.print(f"[green]Saved: {self.output_path}[/green]")
            return True
        except (OSError, subprocess.CalledProcessError) as exc:
            console.print(f"[red]Download failed:[/red] {exc}")
            return False

    def stream(self) -> bool:
        if not shutil.which("mpv"):
            console.print("[red]mpv is not installed. Copy this URL into a player:[/red]")
            console.print(self.url)
            return False
        command = ["mpv"]
        if self.headers:
            command.append("--http-header-fields=" + ",".join(self._header_lines()))
        command.append(self.url)
        try:
            subprocess.run(command, check=True)
            return True
        except (OSError, subprocess.CalledProcessError) as exc:
            console.print(f"[red]Playback failed:[/red] {exc}")
            return False

    def process(self, should_download: bool) -> bool:
        return self.download() if should_download else self.stream()
