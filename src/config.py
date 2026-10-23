"""Validated configuration with a last-known-good remote domain cache."""

import json
import os
import tempfile
import sys
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlsplit

from src.logger import Logger


REMOTE_CONFIG_URL = "https://raw.githubusercontent.com/k-karthikn/padam-cli/refs/heads/master/config/config.json"
DEFAULT_CONFIG = {
    "domains": {"moviesda": "https://moviesda.ski", "isaidub": "https://isaiidub.com"},
    "download_path": "~/Downloads/",
    "endpoints": {"moviesda_home": "/home.html", "dubbed_movies": "/tamil-dubbed-movies/"},
    "headers": {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"},
    "junk_titles": [],
}


class ConfigError(ValueError):
    pass


def validate_domain(value: object) -> str:
    if not isinstance(value, str):
        raise ConfigError("Source domain must be a string")
    url = urlsplit(value)
    if (url.scheme != "https" or not url.hostname or url.username or url.password
            or url.port not in (None, 443) or url.path not in ("", "/")
            or url.query or url.fragment or "." not in url.hostname):
        raise ConfigError(f"Invalid HTTPS source domain: {value}")
    return f"https://{url.hostname}"


def validate_domains(data: object) -> dict[str, str]:
    if not isinstance(data, dict):
        raise ConfigError("Config must contain a domains object")
    try:
        return {name: validate_domain(data[name]) for name in ("moviesda", "isaidub")}
    except KeyError as exc:
        raise ConfigError(f"Missing source domain: {exc.args[0]}") from exc


class Config:
    def __init__(self, config_path: Path | None = None, cache_path: Path | None = None,
                 fetcher=None):
        config_root = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
        if os.name == "nt":
            config_root = Path(os.environ.get("APPDATA", config_root))
        repo_path = Path(__file__).resolve().parents[1] / "config/config.json"
        default_path = (repo_path if not getattr(sys, "frozen", False) and repo_path.exists()
                        else config_root / "padam-cli/config.json")
        self.config_path = config_path or default_path
        cache_root = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))
        if os.name == "nt":
            cache_root = Path(os.environ.get("LOCALAPPDATA", cache_root))
        self.cache_path = cache_path or cache_root / "padam-cli/config.json"
        self.fetcher = fetcher or self._download
        self.config_url = REMOTE_CONFIG_URL
        self.load_config()

    @staticmethod
    def _download(url: str) -> bytes:
        request = urllib.request.Request(url, headers={"User-Agent": "padam-cli/0.6.1"})
        with urllib.request.urlopen(request, timeout=8) as response:
            if urlsplit(response.url).scheme != "https":
                raise ConfigError("Remote config redirected to an insecure URL")
            data = response.read(64_001)
        if len(data) > 64_000:
            raise ConfigError("Remote config is too large")
        return data

    def load_config(self) -> None:
        config = dict(DEFAULT_CONFIG)
        try:
            local = json.loads(self.config_path.read_text(encoding="utf-8"))
            if not isinstance(local, dict):
                raise ConfigError("Local config must be an object")
            config.update({key: value for key, value in local.items() if key != "domains"})
            if "domains" in local:
                try:
                    config["domains"] = validate_domains(local["domains"])
                except ConfigError as exc:
                    Logger.log(f"Ignoring invalid local domains: {exc}")
        except FileNotFoundError:
            pass
        except (OSError, ValueError) as exc:
            Logger.log(f"Ignoring invalid local config: {exc}")
            config = dict(DEFAULT_CONFIG)

        try:
            cached = json.loads(self.cache_path.read_text(encoding="utf-8"))
            config["domains"] = validate_domains(cached.get("domains"))
        except FileNotFoundError:
            pass
        except (OSError, ValueError) as exc:
            Logger.log(f"Ignoring invalid cached config: {exc}")

        self._apply(config)

    def _apply(self, config: dict) -> None:
        self.domains = validate_domains(config["domains"])
        self.moviesda = self.domains["moviesda"]
        self.isaidub = self.domains["isaidub"]
        endpoints = config.get("endpoints") if isinstance(config.get("endpoints"), dict) else {}
        home_path = endpoints.get("moviesda_home", "/home.html")
        dubbed_path = endpoints.get("dubbed_movies", "/tamil-dubbed-movies/")
        if not isinstance(home_path, str) or not home_path.startswith("/"):
            home_path = "/home.html"
        if not isinstance(dubbed_path, str) or not dubbed_path.startswith("/"):
            dubbed_path = "/tamil-dubbed-movies/"
        self.moviesda_home_endpoint = self.moviesda + home_path
        self.moviesda_dubbed_movies_endpoint = self.moviesda + dubbed_path
        download_path = config.get("download_path")
        self.download_path = download_path if isinstance(download_path, str) and download_path else "~/Downloads/"
        headers = config.get("headers")
        self.headers = ({str(key): value for key, value in headers.items()
                         if isinstance(key, str) and isinstance(value, str)
                         and "\r" not in key + value and "\n" not in key + value}
                        if isinstance(headers, dict) else {})
        junk_titles = config.get("junk_titles")
        self.junks = [title for title in junk_titles if isinstance(title, str)] if isinstance(junk_titles, list) else []

    def fetch_config(self) -> bool:
        """Refresh domains from the trusted repository, retaining prior values on failure."""
        temporary = None
        try:
            remote = json.loads(self.fetcher(self.config_url))
            domains = validate_domains(remote["domains"])
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=self.cache_path.parent,
                                             delete=False) as stream:
                json.dump({"domains": domains}, stream)
                temporary = Path(stream.name)
            temporary.replace(self.cache_path)
            self.load_config()
            return True
        except (OSError, ValueError, KeyError, urllib.error.URLError) as exc:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
            Logger.log(f"Config refresh failed; using last known domains: {exc}")
            return False
