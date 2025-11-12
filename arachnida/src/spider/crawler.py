from __future__ import annotations
from collections import deque
from .util import CrawlConfig, normalize_url, is_same_host, is_image_url
from .parse import extract_links_and_images
from .fetch import fetch_text, download_file

def crawl_and_download(cfg:CrawlConfig)->int:
 start=normalize_url(cfg.base_url); visited=set(); q=deque([(start,0)]); downloaded=set(); count=0
 while q:
  url,depth=q.popleft()
  if url in visited: continue
  visited.add(url)
  html=fetch_text(url)
  if html is None: continue
  links,imgs=extract_links_and_images(url,html)
  for img in imgs:
   if img in downloaded: continue
   if not is_image_url(img): continue
   dest=download_file(img,cfg.out_dir)
   if dest:
    print(dest, flush=True); downloaded.add(img); count+=1
  if cfg.recursive and depth<cfg.max_depth:
   for link in links:
    if cfg.same_host_only and not is_same_host(start,link): continue
    if link not in visited: q.append((link,depth+1))
 return count
