"""Bounded HTTP fetching and HTML traversal for the supported catalogues."""

import asyncio
import html
import re
from dataclasses import dataclass
from urllib.parse import parse_qs, unquote, urlencode, urlsplit

import httpx
from bs4 import BeautifulSoup

from src.logger import Logger
from src.utils import is_valid, secure_url


class ScrapeError(RuntimeError):
    def __init__(self, url: str, reason: str):
        self.url = url
        super().__init__(f"Could not load {url}: {reason}")


@dataclass(frozen=True)
class Link:
    title: str
    url: str
    referer: str = ""


@dataclass
class Page:
    url: str
    soup: BeautifulSoup | None
    media_type: str = ""
    disposition: str = ""

    @property
    def is_media(self) -> bool:
        if self.media_type in {"text/html", "application/xhtml+xml"}:
            return False
        path = unquote(urlsplit(self.url).path).lower()
        return self.media_type.startswith("video/") or self.media_type in {
            "application/octet-stream", "application/mp4", "application/vnd.apple.mpegurl",
            "application/x-mpegurl",
        } or path.endswith((".mp4", ".mkv", ".webm", ".avi", ".mov", ".m4v", ".m3u8"))


class Scraper:
    PAGE_LIMIT = 2_000_000
    REDIRECT_LIMIT = 10
    TRANSIENT_STATUS = {429, 500, 502, 503, 504, 520, 521, 522, 523, 524}

    async def fetch_page(self, client: httpx.AsyncClient, url: str, referer: str = "") -> Page:
        if secure_url(url, url) != url:
            raise ScrapeError(url, "only HTTPS source links are supported")
        for attempt in range(2):
            try:
                return await self._fetch_once(client, url, referer)
            except (httpx.HTTPError, UnicodeError) as exc:
                retryable = isinstance(exc, httpx.TransportError) or (
                    isinstance(exc, httpx.HTTPStatusError) and
                    exc.response.status_code in self.TRANSIENT_STATUS)
                if retryable and attempt == 0:
                    await asyncio.sleep(0.4)
                    continue
                reason = str(exc).strip() or type(exc).__name__
                Logger.log(f"Fetch failed: {url}: {reason}")
                raise ScrapeError(url, reason) from exc
        raise AssertionError("unreachable")

    async def _fetch_once(self, client: httpx.AsyncClient, url: str, referer: str) -> Page:
        headers = {"Referer": referer} if referer else None
        current = url
        for _ in range(self.REDIRECT_LIMIT):
            async with client.stream("GET", current, headers=headers,
                                     follow_redirects=False) as response:
                if response.is_redirect:
                    target = secure_url(str(response.url), response.headers.get("location", ""))
                    if target is None:
                        raise ScrapeError(current, "source redirected to an insecure or missing URL")
                    # The gateway's Location is already the usable media URL. Opening a
                    # large CDN response here can time out before playback/download starts.
                    if Page(target, None).is_media:
                        return Page(target, None)
                    current = target
                    continue
                response.raise_for_status()
                final_url = str(response.url)
                if secure_url(final_url, final_url) != final_url:
                    raise ScrapeError(url, "source redirected to an insecure URL")
                media_type = response.headers.get("content-type", "").split(";", 1)[0].lower()
                page = Page(final_url, None, media_type,
                            response.headers.get("content-disposition", ""))
                if page.is_media:
                    return page
                chunks = bytearray()
                async for chunk in response.aiter_bytes():
                    chunks.extend(chunk)
                    if len(chunks) > self.PAGE_LIMIT:
                        raise ScrapeError(url, "page exceeds 2 MB")
                encoding = response.encoding or "utf-8"
                page.soup = BeautifulSoup(chunks.decode(encoding, errors="replace"), "lxml")
                return page
        raise ScrapeError(url, "too many HTTP redirects")

    @staticmethod
    def links(page: Page, selector: str, junk_titles=()) -> list[Link]:
        if page.soup is None:
            return []
        found = {}
        for anchor in page.soup.select(selector):
            url = secure_url(page.url, anchor.get("href", ""))
            title = anchor.get_text(" ", strip=True)
            if url and url != page.url and is_valid(title, anchor.get("href", ""), junk_titles):
                found.setdefault(url, Link(title, url, page.url))
        return list(found.values())

    def entries(self, page: Page, junk_titles=()) -> list[Link]:
        return [link for link in self.links(page, ".f a[href], .folder a[href]", junk_titles)
                if link.title.casefold() not in {"sms", "facebook", "twitter", "whatsapp", "share"}]

    def pages(self, page: Page) -> list[str]:
        if page.soup is None:
            return []
        host = urlsplit(page.url).hostname
        found = {}
        for anchor in page.soup.select(".pagination a[href], .pagecontent a[href], a[rel=next]"):
            url = secure_url(page.url, anchor.get("href", ""))
            title = anchor.get_text(" ", strip=True).casefold()
            query = parse_qs(urlsplit(url).query) if url else {}
            is_page = (title.isdigit() or title in {"next", "previous", "prev", "»", "«"}
                       or "next" in anchor.get("rel", []) or "page" in query)
            if url and is_page and urlsplit(url).hostname == host:
                found[url] = None
        return list(found)

    def choices(self, page: Page, junk_titles=()) -> list[Link]:
        downloads = [link for link in self.links(page, ".dlink a[href], a.coral[href]")
                     if "watch" not in link.title.casefold() and
                     "play online" not in link.title.casefold()]
        if downloads:
            return downloads
        folders = self.entries(page, junk_titles)
        if folders:
            return folders
        if page.soup is None:
            return []

        found: dict[str, Link] = {}

        def add(raw: str | None, title: str) -> None:
            url = secure_url(page.url, html.unescape(raw or ""))
            if url and url != page.url:
                found.setdefault(url, Link(title.strip() or "Download link", url, page.url))

        # Other common templates use a button, a bare download anchor, or a media tag.
        for anchor in page.soup.select(
            "a[download][href], a.download[href], a[class*='download'][href], "
            "a[class*='server'][href], .download a[href], .server a[href], "
            "a.btn[href], a.button[href]"):
            add(anchor.get("href"), anchor.get_text(" ", strip=True) or anchor.get("aria-label", ""))
        for anchor in page.soup.select("a[href]"):
            title = anchor.get_text(" ", strip=True)
            href = anchor.get("href", "")
            if re.search(r"download|server|quality|get link|get url|continue|click here|720p|1080p|360p|\.mp4|\.mkv|\.m3u8|/file/", title + " " + href, re.I):
                add(href, title or anchor.get("aria-label", ""))
        if found:
            return list(found.values())

        for media in page.soup.select("video[src], source[src]"):
            add(media.get("src"), "Video stream")
        for meta in page.soup.select("meta[property='og:video'][content], meta[property='og:video:url'][content]"):
            add(meta.get("content"), "Video stream")
        for form in page.soup.select("form[action]"):
            label = form.get_text(" ", strip=True)
            action = form.get("action", "")
            if (form.get("method", "get").casefold() == "get" and
                    re.search(r"download|server|file|continue|get link", label + " " + action, re.I)):
                fields = [(item.get("name"), item.get("value", ""))
                          for item in form.select("input[type='hidden'][name]")]
                query = urlencode(fields)
                add(action + (("&" if "?" in action else "?") + query if query else ""),
                    label or "Continue")
        for element in page.soup.select("[data-url], [data-href], [onclick]"):
            add(element.get("data-url") or element.get("data-href"),
                element.get_text(" ", strip=True) or "Continue")
            onclick = element.get("onclick", "")
            match = re.search(r"(?:location(?:\.href)?\s*=|location\.(?:assign|replace)\(|window\.open\()\s*['\"]([^'\"]+)", onclick)
            if match:
                add(match.group(1), element.get_text(" ", strip=True) or "Continue")
        for meta in page.soup.select("meta[http-equiv]"):
            if meta.get("http-equiv", "").casefold() == "refresh":
                match = re.search(r"url\s*=\s*['\"]?([^'\";]+)", meta.get("content", ""), re.I)
                if match:
                    add(match.group(1).strip(), "Continue")
        for script in page.soup.select("script:not([src])"):
            source = script.string or ""
            for match in re.finditer(r"(?:location(?:\.href)?\s*=|location\.(?:assign|replace)\(|window\.open\()\s*['\"]([^'\"]+)", source[:100_000]):
                add(match.group(1), "Continue")
        if found:
            return list(found.values())

        for frame in page.soup.select("iframe[src]"):
            add(frame.get("src"), "Embedded player")
        return list(found.values())

    def latest(self, page: Page) -> list[Link]:
        if page.soup is None:
            return []
        found = {}
        for card in page.soup.select("div.latest"):
            strong = card.find("strong")
            anchor = card.find("a", string="Download Now") or card.find("a", class_="green")
            if strong is None or anchor is None:
                continue
            url = secure_url(page.url, anchor.get("href", ""))
            if url:
                found.setdefault(url, Link(strong.get_text(" ", strip=True), url, page.url))
        return list(found.values())
