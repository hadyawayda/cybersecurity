from __future__ import annotations
from dataclasses import dataclass
from urllib.parse import urlsplit, urlunsplit, urljoin
from typing import Set

IMG_EXTS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}

def normalize_url(url: str) -> str:
    u = urlsplit(url)
    return urlunsplit((u.scheme.lower(), u.netloc.lower(), u.path, u.query, ''))

def is_same_host(a: str, b: str) -> bool:
    return urlsplit(a).netloc.lower() == urlsplit(b).netloc.lower()

def is_image_url(url: str) -> bool:
    import os
    _, ext = os.path.splitext(urlsplit(url).path)
    return ext.lower() in IMG_EXTS

def safe_join(base: str, link: str) -> str:
    return normalize_url(urljoin(base, link))

def ensure_dir(path: str) -> None:
    import os
    os.makedirs(path, exist_ok=True)

def sanitize_filename(name: str) -> str:
    import re
    name = name.replace('/', '_').replace('\\', '_')
    return re.sub(r'[^A-Za-z0-9._-]+', '_', name) or 'file'

@dataclass
class CrawlConfig:
    base_url: str
    recursive: bool = False
    max_depth: int = 5
    out_dir: str = 'data'
    same_host_only: bool = True
