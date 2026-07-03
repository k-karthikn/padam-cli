import json
import urllib.request
import urllib.error
from rich.console import Console

console = Console()
class Config:
    def __init__(self):
        self.config_url = "https://raw.githubusercontent.com/e-Zephyr/padam-cli/refs/heads/master/config/config.json"
        
        # moviesda
        self.moviesda = None
        self.moviesda_home_endpoint = None
        self.moviesda_dubbed_movies_endpoint = None
        # isaidub
        self.isaidub = None

        #paths
        self.download_path = None
        self.config_path = "config/config.json"

        self.headers = None

        self.junks = None

    def fetch_config(self):
            with console.status("[bold cyan]Fetching latest configuration...", spinner="dots"):
                try:
                    with urllib.request.urlopen(self.config_url) as response:
                        with open(self.config_path, 'wb') as out_file:
                            out_file.write(response.read())
                    console.print("[bold green]✔[/] Configuration updated successfully!")
                except urllib.error.URLError as e:
                    console.print(f"[bold red]✖ Error downloading config:[/] {e}")

    def load_config(self):
        with open('config/config.json', 'r') as file:
            config_data = json.load(file)

            self.moviesda = config_data["domains"]["moviesda"]
            self.moviesda_home_endpoint = config_data["domains"]["moviesda"] + config_data["endpoints"]["moviesda_home"]
            self.moviesda_dubbed_movies_endpoint = config_data["domains"]["moviesda"] + config_data["endpoints"]["dubbed_movies"]

            self.isaidub = config_data["domains"]["isaidub"]

            self.download_path = config_data["download_path"]
            self.headers = config_data.get("headers", {})
            self.junks = config_data.get("junk_titles", [])