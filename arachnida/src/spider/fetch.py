from __future__ import annotations
import os, hashlib, requests
from urllib.parse import urlsplit
from .util import ensure_dir, sanitize_filename
HEADERS={'User-Agent':'arachnida-spider/1.0'}; TIMEOUT=10

def fetch_text(url:str):
 try:
  r=requests.get(url, headers=HEADERS, timeout=TIMEOUT)
  if r.status_code==200 and 'text/html' in r.headers.get('content-type','').lower():
   r.encoding=r.encoding or 'utf-8'; return r.text
 except Exception: return None
 return None

def download_file(url:str, out_root:str):
 try:
  r=requests.get(url, headers=HEADERS, timeout=TIMEOUT, stream=True)
  if r.status_code!=200: return None
  u=urlsplit(url); host_dir=os.path.join(out_root,u.netloc)
  d,fn=os.path.split(u.path)
  if not fn: fn=f"index_{hashlib.sha1(url.encode()).hexdigest()[:12]}"
  fn=sanitize_filename(fn); dest_dir=os.path.join(host_dir,d.lstrip('/'))
  ensure_dir(dest_dir); dest=os.path.join(dest_dir,fn)
  base,ext=os.path.splitext(dest); i=1; final=dest
  while os.path.exists(final): final=f"{base}_{i}{ext}"; i+=1
  with open(final,'wb') as f:
   for chunk in r.iter_content(65536):
    if chunk: f.write(chunk)
  return final
 except Exception: return None
