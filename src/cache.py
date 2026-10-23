"""Short-lived, best-effort cache for complete catalogue listings."""

import hashlib
import json
import tempfile
import time
from pathlib import Path

from src.scraper import Link
from src.utils import secure_url


class CatalogueCache:
    TTL_SECONDS = 15 * 60
    MAX_BYTES = 2_000_000

    def __init__(self, directory: Path):
        self.directory = directory

    def _path(self, url: str) -> Path:
        return self.directory / f"{hashlib.sha256(url.encode()).hexdigest()}.json"

    def load(self, url: str) -> list[Link] | None:
        try:
            path = self._path(url)
            if path.stat().st_size > self.MAX_BYTES:
                return None
            data = json.loads(path.read_text(encoding="utf-8"))
            if data["url"] != url or not 0 <= time.time() - data["saved_at"] < self.TTL_SECONDS:
                return None
            links = [Link(**item) for item in data["links"]]
            if any(secure_url(link.url, link.url) != link.url or
                   (link.referer and secure_url(link.referer, link.referer) != link.referer)
                   for link in links):
                return None
            return links
        except (OSError, ValueError, KeyError, TypeError):
            return None

    def save(self, url: str, links: list[Link]) -> None:
        temporary = None
        try:
            self.directory.mkdir(parents=True, exist_ok=True)
            payload = json.dumps({"url": url, "saved_at": time.time(),
                                  "links": [link.__dict__ for link in links]})
            if len(payload.encode("utf-8")) > self.MAX_BYTES:
                return
            with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=self.directory,
                                             delete=False) as stream:
                stream.write(payload)
                temporary = Path(stream.name)
            temporary.replace(self._path(url))
        except OSError:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
