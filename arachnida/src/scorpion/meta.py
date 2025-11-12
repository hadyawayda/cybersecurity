from __future__ import annotations
from typing import Dict, Any
from PIL import Image, ExifTags
import os, time
EXIF_TAGS={v:k for k,v in ExifTags.TAGS.items()}

def basic_file_info(path:str)->Dict[str,Any]:
 st=os.stat(path); info={'size_bytes':st.st_size,'mtime':time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(st.st_mtime)),'ctime':time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(st.st_ctime))}
 try:
  with Image.open(path) as im:
   info['format']=im.format; info['mode']=im.mode; info['width'],info['height']=im.size; info['info_keys']=sorted(list(im.info.keys()))
 except Exception: pass
 return info

def read_exif_dict(path:str)->Dict[int,Any]:
 try:
  with Image.open(path) as im:
   exif=im.getexif(); return dict(exif) if exif else {}
 except Exception: return {}

def read_exif_human(path:str)->Dict[str,Any]:
 out={}
 for tag_id,val in read_exif_dict(path).items():
  name=ExifTags.TAGS.get(tag_id,f'Tag_{tag_id}')
  if isinstance(val,bytes):
   try: val=val.decode('utf-8','ignore')
   except Exception: pass
  out[name]=val
 return out
