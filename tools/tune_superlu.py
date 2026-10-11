#!/usr/bin/env python3
"""Set only SuperLU MT's U-factor allocation multiplier in a generated build tree."""
import argparse
from pathlib import Path
import re

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('source',type=Path)
    ap.add_argument('--u-fill',type=int,default=100)
    a=ap.parse_args()
    if not 50<=a.u_fill<=500:ap.error('--u-fill must be between 50 and 500')
    text,n=re.subn(r'case 7:\s*return\s*\(\s*-\d+\s*\);',
                   f'case 7: return (-{a.u_fill});',a.source.read_text())
    if n!=1:raise SystemExit('Expected exactly one SuperLU case-7 allocation setting')
    a.source.write_text(text)
    print(f'SuperLU U-factor allocation multiplier: {a.u_fill} (upstream default: 50)')

if __name__=='__main__':main()
