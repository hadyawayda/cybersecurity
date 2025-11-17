# ft_onion (mandatory + bonus)

## Mandatory: layered file encryption (AES‑256‑GCM)

CLI: `ft_onion.py`

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt

# encrypt (3 layers)
./ft_onion.py -e -k "pw1,pw2,pw3" -i secret.pdf -o secret.oni

# decrypt (same order)
./ft_onion.py -d -k "pw1,pw2,pw3" -i secret.oni -o secret.pdf

# prompt securely for keys
./ft_onion.py -e -k - -i photo.jpg -o photo.oni
```

Format: `MAGIC | meta_len | meta_json | ciphertext`, meta stores per-layer salt & nonce.

## Bonus: Tor hidden service (nginx + sshd) — Docker

Folder: `docker/`

```
docker/
  Dockerfile      # Debian + nginx + openssh + tor + tini
  entrypoint.py   # starts services, prints .onion hostname
  nginx.conf      # serves /var/www/html/index.html (+ /healthz)
  sshd_config     # key‑auth only, no root/passwords
  torrc           # v3 hidden service exposing ports 80 and 22
  index.html      # landing page
```

### Build & run

```bash
cd docker
docker build -t ft_onion .
docker run --rm -it --name ft_onion ft_onion
# entrypoint prints the .onion hostname when ready
# Access via Tor network only (no port forwarding)
```

**Persist the onion address:**

```bash
mkdir -p hsdata && chmod 700 hsdata
docker run --rm -it --name ft_onion -v "$(pwd)/hsdata:/var/lib/tor/hidden_service" ft_onion
# hostname is in hsdata/hostname
```

**SSH over Tor:**

```bash
# (after adding your pubkey to /home/appuser/.ssh/authorized_keys inside the container)
torsocks ssh appuser@<your-onion-hostname>
```

## Tests

```bash
pip install pytest
pytest -q
```

## Makefile targets

- `make install` — create venv & install deps
- `make test` — run pytest
- `make clean` — remove venv, caches

```bash
make install
make test
```
