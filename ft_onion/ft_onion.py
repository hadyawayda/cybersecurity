#!/usr/bin/env python3
from __future__ import annotations
import argparse, sys, getpass
from src.ft_onion.layers import seal, peel
from src.ft_onion.io import read_bytes, write_bytes

def parse_pw_list(arg: str) -> list[str]:
    if arg == '-':
        pws=[]; i=1
        while True:
            pw = getpass.getpass(f'passphrase {i} (empty to finish): ')
            if not pw: break
            pws.append(pw); i+=1
        if not pws: raise SystemExit("ft_onion: no passphrases given")
        return pws
    return [p for p in (s.strip() for s in arg.split(',')) if p]

def make_parser():
    p = argparse.ArgumentParser(prog='ft_onion', add_help=False, description='Layered onion encryption/decryption (AES-256-GCM).')
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument('-e','--encrypt', action='store_true', help='encrypt mode')
    g.add_argument('-d','--decrypt', action='store_true', help='decrypt mode')
    p.add_argument('-k','--keys', metavar='K1,K2,... or -', required=True, help='comma-separated passphrases; or "-" to prompt securely')
    p.add_argument('-i','--in', dest='inp', required=True, help='input file')
    p.add_argument('-o','--out', dest='out', required=True, help='output file')
    p.add_argument('-h','--help', action='help', help='show help and exit')
    return p

def main(argv=None)->int:
    a = make_parser().parse_args(argv)
    pws = parse_pw_list(a.keys)
    try:
        data = read_bytes(a.inp)
        if a.encrypt: write_bytes(a.out, seal(data, pws))
        else: write_bytes(a.out, peel(data, pws))
        return 0
    except KeyboardInterrupt: return 130
    except Exception as e:
        print(f'ft_onion: error: {e}', file=sys.stderr); return 1

if __name__=='__main__':
    raise SystemExit(main())
