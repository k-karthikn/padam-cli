"""Small source-independent validation helpers."""

import re
import httpx
from urllib.parse import urljoin, urlsplit


def canonical_url(value: str) -> str | None:
    if not isinstance(value, str) or not value or any(ord(c) < 32 for c in value):
        return None
    try:
        parts = urlsplit(value)
        if parts.scheme != "https" or not parts.hostname or parts.username or parts.password:
            return None
        _ = parts.port
        path_query = re.sub(r"%(?![0-9A-Fa-f]{2})", "%25", parts.path + ("?" + parts.query if "?" in value.split("#",1)[0] else ""))
        return str(httpx.URL(parts._replace(path=path_query.split("?",1)[0], query=path_query.split("?",1)[1] if "?" in path_query else "", fragment="").geturl()))
    except (ValueError, httpx.InvalidURL):
        return None

def is_secure_url(url: str) -> bool:
    return canonical_url(url) is not None

def secure_url(base: str, href: str) -> str | None:
    if not isinstance(href, str) or not href or href.startswith("#") or any(ord(char) < 32 for char in href):
        return None
    try:
        return canonical_url(urljoin(base, href))
    except ValueError:
        return None


def normalized(text: str) -> str:
    return " ".join(re.findall(r"[^\W_]+", text.casefold(), re.UNICODE))


def is_valid(text: str, href: str, junk_titles=()) -> bool:
    if not text.strip() or href in {"", "/", "#"} or text.strip() in junk_titles:
        return False
    if re.fullmatch(r"[A-Za-z]|\d+|Tamil \d{4}(?: Dubbed)? Movies", text.strip(), re.I):
        return False
    return True
