import subprocess
import webbrowser
import base64
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from rich.console import Console
from src.config import Config


console = Console()
config = Config()
config.load_config()

class Media:
    def __init__(self, url: str, title: str | None = None, download_dir: str = config.download_path):
        self.url = url
        self.title = title
        self.download_dir = Path(download_dir).expanduser()
        self.filename = self._generate_filename()
        self.output_path = self.download_dir / self.filename

    def _generate_filename(self) -> str:
            try:
                query = parse_qs(urlparse(self.url).query)
                
                if "dl" in query:
                    decoded_dl = base64.b64decode(query["dl"][0] + '==').decode('utf-8', errors='ignore')
                    dl_query = parse_qs(decoded_dl)
                    if "path" in dl_query:
                        return Path(dl_query["path"][0]).name

                if "path" in query:
                    return Path(query["path"][0]).name
            except Exception:
                pass

            name = Path(urlparse(self.url).path).name
            if "." in name and not name.endswith(('.php', '.html', '.aspx')): 
                return name
                
            if self.title: return f"{self.title}.mp4"
            return "movie.mp4"
    
    def download(self):
        self.download_dir.mkdir(parents=True, exist_ok=True)
        yt_dlp_cmd = ["yt-dlp",self.url,"-o", str(self.output_path)]
        ffmpeg_cmd = [ "ffmpeg", "-i", self.url, "-c", "copy", "-y", str(self.output_path) ]
        console.print(
            "[cyan]"
            "[1] yt-dlp     - Fast startup, slow download speed\n"
            "[2] ffmpeg     - Slow startup, fast download speed\n"
            "[3] webbrowser - Fast startup, standard download speed"
            "[/cyan]"
        )
        choise = int(console.input(f"[yellow]Choose the dowloader: [/yellow]"))

        console.print(f"[bold cyan]Download started. Downloading in path {self.output_path}[/bold cyan]")
        try:
            subprocess.run(yt_dlp_cmd, check=True) if choise == 1 else subprocess.run(ffmpeg_cmd, check=True) if choise == 2 else webbrowser.open(self.url)
            if choise!=3 : console.print(f"[bold green]✓ Complete:[/bold green] {self.output_path}")
        except Exception as e:
            console.print(f"[bold red]✗ Download failed.[/bold red] :\n{e}")
            
    def stream(self):
        console.print("[bold cyan]Starting stream with mpv...[/bold cyan]")
        subprocess.run(["mpv", self.url], check=True)

    def process(self, should_download: bool):
        if should_download:
            self.download()
        else:
            self.stream()