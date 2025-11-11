from __future__ import annotations
from typing import Dict, Any, Optional, Tuple
from PIL import Image, ExifTags
import os, time

EXIF_TAGS = {v: k for k, v in ExifTags.TAGS.items()}

def basic_file_info(path: str) -> Dict[str, Any]:
    st = os.stat(path)
    info = {'size_bytes': st.st_size,
            'mtime': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(st.st_mtime)),
            'ctime': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(st.st_ctime))}
    try:
        with Image.open(path) as im:
            info['format'] = im.format; info['mode'] = im.mode
            info['width'], info['height'] = im.size
            info['info_keys'] = sorted(list(im.info.keys()))
    except Exception:
        pass
    return info

def read_exif(path: str) -> Dict[str, Any]:
    data: Dict[str, Any] = {}
    try:
        with Image.open(path) as im:
            exif = im.getexif()
            if not exif: return {}
            for tag_id, value in exif.items():
                tag = ExifTags.TAGS.get(tag_id, f'Tag_{tag_id}')
                if isinstance(value, bytes):
                    try: value = value.decode('utf-8','ignore')
                    except Exception: pass
                data[tag] = value
            gps = exif.get(EXIF_TAGS.get('GPSInfo', -1))
            if isinstance(gps, dict):
                dec = _gps_to_decimal(gps)
                if dec: data['GPSDecimal'] = dec
    except Exception:
        return {}
    return data

def _gps_to_decimal(gps: dict) -> Optional[Tuple[float,float]]:
    def r2f(x):
        try: return float(x.numerator)/float(x.denominator)
        except Exception:
            try: a,b = x; return a/b
            except Exception: return float(x)
    try:
        lat_ref = gps.get(1); lat = gps.get(2)
        lon_ref = gps.get(3); lon = gps.get(4)
        if not (lat_ref and lon_ref and lat and lon): return None
        def dms(dms): 
            d,m,s = [r2f(v) for v in dms]; return d + m/60 + s/3600
        lat_deg = dms(lat); lon_deg = dms(lon)
        if str(lat_ref).upper().startswith('S'): lat_deg = -lat_deg
        if str(lon_ref).upper().startswith('W'): lon_deg = -lon_deg
        return (round(lat_deg,6), round(lon_deg,6))
    except Exception:
        return None
