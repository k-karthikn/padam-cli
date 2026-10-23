"""Small source-independent validation helpers."""

import re
from urllib.parse import urljoin, urlsplit


def secure_url(base: str, href: str) -> str | None:
    if not isinstance(href, str) or not href or href.startswith("#") or any(ord(char) < 32 for char in href):
        return None
    try:
        url = urljoin(base, href)
        parts = urlsplit(url)
        if parts.scheme != "https" or not parts.hostname or parts.username or parts.password:
            return None
        _ = parts.port
    except ValueError:
        return None
    return parts._replace(fragment="").geturl()


def normalized(text: str) -> str:
    return " ".join(re.findall(r"[^\W_]+", text.casefold(), re.UNICODE))


def is_valid(text: str, href: str, junk_titles=()) -> bool:
    if not text.strip() or href in {"", "/", "#"} or text.strip() in junk_titles:
        return False
    if re.fullmatch(r"[A-Za-z]|\d+|Tamil \d{4}(?: Dubbed)? Movies", text.strip(), re.I):
        return False
    return True
