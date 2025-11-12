from __future__ import annotations
from typing import Dict, Iterable
from PIL import Image, ExifTags
import piexif
NAME2ID={v:k for k,v in ExifTags.TAGS.items()}

def _ensure_jpeg_tiff(path:str):
 fmt=None
 try:
  with Image.open(path) as im:
   fmt=(im.format or '').upper()
 except Exception: pass
 if fmt not in ('JPEG','TIFF'):
  raise ValueError('Only JPEG/TIFF are supported for EXIF write operations')

def set_tags(path:str, kv:Dict[str,str])->None:
 _ensure_jpeg_tiff(path); exif_dict=piexif.load(path)
 for name,val in kv.items():
  tag_id=NAME2ID.get(name)
  if tag_id is None: raise ValueError(f'Unknown EXIF tag name: {name}')
  target_ifd='0th' if tag_id in piexif.TAGS['0th'] else 'Exif'
  exif_dict[target_ifd][tag_id]=val.encode('utf-8','ignore') if isinstance(val,str) else val
 exif_bytes=piexif.dump(exif_dict); piexif.insert(exif_bytes, path)

def delete_tags(path:str, keys:Iterable[str])->None:
 _ensure_jpeg_tiff(path); exif_dict=piexif.load(path)
 for k in keys:
  tid=NAME2ID.get(k)
  if tid is None: continue
  for ifd in ('0th','Exif','GPS','1st'):
   if tid in exif_dict.get(ifd, {}): del exif_dict[ifd][tid]
 exif_bytes=piexif.dump(exif_dict); piexif.insert(exif_bytes, path)

def wipe_all_metadata(path:str)->None:
 _ensure_jpeg_tiff(path); exif_dict=piexif.load(path)
 for ifd in ('0th','Exif','GPS','1st'): exif_dict[ifd]={}
 exif_bytes=piexif.dump(exif_dict); piexif.insert(exif_bytes, path)
