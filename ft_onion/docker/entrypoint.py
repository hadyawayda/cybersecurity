#!/usr/bin/env python3
from __future__ import annotations
import os, subprocess, time, sys, pathlib, pwd, grp

HS_DIR = "/var/lib/tor/hidden_service"
def ensure_dirs():
    os.makedirs("/var/run/sshd", exist_ok=True)
    os.makedirs("/var/www/html", exist_ok=True)
    os.makedirs(HS_DIR, exist_ok=True)
    try:
        uid = pwd.getpwnam('debian-tor').pw_uid
        gid = grp.getgrnam('debian-tor').gr_gid
        os.chown(HS_DIR, uid, gid)
        os.chmod(HS_DIR, 0o700)
    except Exception:
        pass

def start(cmd, name):
    print(f"[entrypoint] start {name}: {' '.join(cmd)}", flush=True)
    return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

def read_onion():
    p = pathlib.Path(HS_DIR) / "hostname"
    for _ in range(120):
        if p.exists():
            return p.read_text(encoding="utf-8").strip()
        time.sleep(1)
    return None

def main():
    ensure_dirs()
    procs = []
    procs.append(start(["nginx","-g","daemon off;","-c","/etc/nginx/nginx.conf"], "nginx"))
    procs.append(start(["/usr/sbin/sshd","-D","-e","-f","/etc/ssh/sshd_config","-p","4242"], "sshd"))
    procs.append(start(["tor","-f","/etc/tor/torrc"], "tor"))
    onion = read_onion()
    if onion:
        print(f"[entrypoint] Hidden service: {onion}", flush=True)
        print(f"[entrypoint] HTTP: http://{onion}", flush=True)
        print(f"[entrypoint] SSH: ssh -p 4242 appuser@{onion}", flush=True)
    else:
        print("[entrypoint] hidden service hostname not found yet", file=sys.stderr)
    # keep container alive while children run
    try:
        while any(p.poll() is None for p in procs):
            time.sleep(1)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
