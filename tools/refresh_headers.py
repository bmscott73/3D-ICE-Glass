#!/usr/bin/env python3
"""Generate one consistent native-input header from active numeric statements."""
import argparse
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from iceglass.inputs import refresh

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('paths',nargs='*',type=Path);a=ap.parse_args()
    files=a.paths or [p for folder in ('models','validation','transient/inputs') for p in (ROOT/folder).rglob('*') if p.suffix in ('.stk','.flp') and 'provenance' not in p.parts]
    for p in files:refresh(p)
    print(f'Refreshed {len(files)} input headers')
if __name__=='__main__':main()
