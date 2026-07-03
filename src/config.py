import json
import urllib.request
import urllib.error
from pathlib import Path
from rich.console import Console

console = Console()

class Config:
    def __init__(self):
        self.config_url = "https://raw.githubusercontent.com/e-Zephyr/padam-cli/refs/heads/master/config/config.json"
        self.config_path = "config/config.json"
        
        self.default_config = {
            "domains": {
                "moviesda": "https://moviesda33.com",
                "isaidub": "https://isaidub.ceo"
            },
            "config_url": self.config_url,
            "download_path": "~/Downloads/",
            "endpoints": {
                "moviesda_home": "/home.html",
                "dubbed_movies": "/tamil-dubbed-movies/"
            },
            "headers": {
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"
            },
            "junk_titles": [
                    "moviesda33.com",
                    "Tamil A to Z Movies",
                    "Tamil Movies Collection",
                    "Tamil Single Parts Movies",
                    "Tamil HD Mobile Movies",
                    "Tamil Dubbed Movies",
                    "Tamil Daily Movies",
                    "Request a Movie",
                    "Latest Tamil Web Series",
                    "Latest Tamil Web Serie",
                    "Download Now",
                    "Latest Movies Updates",
                    "»",
                    "«",
                    "Check out our Latest Updates",
                    "Tamil A-Z Dubbed Movies",
                    "Tamil Yearly Dubbed Movies",
                    "Tamil Dubbed Collections",
                    "Tamil Genres Dubbed Movies",
                    "Tamil HD Dubbed Movies",
                    "Tamil Dubbed Web Series",
                    "Tamil Chinese Dubbed Movies"
                ]
        }

        # moviesda
        self.moviesda = None
        self.moviesda_home_endpoint = None
        self.moviesda_dubbed_movies_endpoint = None
        
        # isaidub
        self.isaidub = None

        # paths
        self.download_path = None
        self.headers = None
        self.junks = None

    def fetch_config(self):
        with console.status("[bold cyan]Fetching latest configuration...", spinner="dots"):
            try:
                Path(self.config_path).parent.mkdir(parents=True, exist_ok=True)
                
                with urllib.request.urlopen(self.config_url) as response:
                    with open(self.config_path, 'wb') as out_file:
                        out_file.write(response.read())
                        
                console.print("[bold green]✔[/] Configuration updated successfully!")
                
            except urllib.error.URLError as e:
                console.print(f"[bold red]✖ Error downloading config:[/] {e}")
            except OSError as e:
                console.print(f"[bold red]✖ Error saving config file:[/] {e}")
                
    def load_config(self):
        config_file = Path(self.config_path)

        # 1. Check and create default config if missing
        if not config_file.exists():
            console.print("[yellow]Configuration file not found. Creating default...[/]")
            try:
                config_file.parent.mkdir(parents=True, exist_ok=True)
                with open(config_file, 'w') as file:
                    json.dump(self.default_config, file, indent=4)
            except OSError as e:
                console.print(f"[bold red]✖ Error creating default config:[/] {e}")
                return

        # 2. Load the configuration
        try:
            with open(config_file, 'r') as file:
                config_data = json.load(file)

                self.moviesda = config_data["domains"]["moviesda"]
                self.moviesda_home_endpoint = config_data["domains"]["moviesda"] + config_data["endpoints"]["moviesda_home"]
                self.moviesda_dubbed_movies_endpoint = config_data["domains"]["moviesda"] + config_data["endpoints"]["dubbed_movies"]

                self.isaidub = config_data["domains"]["isaidub"]

                self.download_path = config_data["download_path"]
                self.headers = config_data.get("headers", {})
                self.junks = config_data.get("junk_titles", [])
                
        except (OSError, json.JSONDecodeError) as e:
            console.print(f"[bold red]✖ Error loading config:[/] {e}")