from __future__ import annotations
from bs4 import BeautifulSoup
from typing import List, Tuple
from .util import is_image_url, safe_join

def extract_links_and_images(base_url: str, html: str) -> Tuple[List[str], List[str]]:
    soup = BeautifulSoup(html, 'html.parser')
    links: List[str] = []
    imgs: List[str] = []
    for tag in soup.find_all(['a','img']):
        if tag.name == 'a':
            href = tag.get('href')
            if not href: continue
            u = safe_join(base_url, href)
            links.append(u)
            if is_image_url(u): imgs.append(u)
        else:
            src = tag.get('src')
            if not src: continue
            u = safe_join(base_url, src)
            if is_image_url(u): imgs.append(u)
    seen=set(); dedup_links=[]; dedup_imgs=[]
    for u in links:
        if u not in seen: seen.add(u); dedup_links.append(u)
    seen=set()
    for u in imgs:
        if u not in seen: seen.add(u); dedup_imgs.append(u)
    return dedup_links, dedup_imgs
