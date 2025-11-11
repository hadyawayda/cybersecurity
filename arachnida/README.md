# Arachnida (Spider + Scorpion)

Implements the **Spider** and **Scorpion** programs:
- `spider` downloads images from a URL, optionally recursively (depth & path options).
- `scorpion` prints EXIF and basic metadata for image files.

## Install
```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
```

## spider
```
./spider [-r] [-l N] [-p PATH] URL
```
- `-r` recursive; `-l N` depth (default 5) for recursive; `-p PATH` output dir (default `./data`).
- Downloads: `.jpg/.jpeg/.png/.gif/.bmp`.
- Saves under `PATH/<host>/<url-path>/filename`.
- Only follows links on the **same host**.

## scorpion
```
./scorpion FILE1 [FILE2 ...]
# add --json for JSON lines
```

Prints size, timestamps, WxH, format, Pillow info keys, EXIF (decoded), and GPS in decimal if present.

## Notes
- No `wget`/`scrapy`; only HTTP/parsing helpers. Crawling logic is custom.
- Use responsibly; consider rate limiting and website policies.
