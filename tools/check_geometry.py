#!/usr/bin/env python3
"""Verify rectangle bounds, overlap, area, and power for each active stack."""
import argparse
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from iceglass.inputs import active,blocks,dimensions,floorplans,resolve,geometry

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('paths',nargs='*',type=Path);a=ap.parse_args()
    stacks=a.paths or [p for f in ('models','validation','transient/inputs') for p in (ROOT/f).rglob('*.stk') if 'provenance' not in p.parts]
    errors=[];count=0
    for s in stacks:
        try:
            chip,_=dimensions(s.read_text())
            for ref in floorplans(s):geometry(blocks(resolve(s,ref)),chip);count+=1
        except (ValueError,FileNotFoundError) as e:errors.append(str(e))
    if errors:raise SystemExit('\n'.join(errors))
    print(f'PASS: {len(stacks)} stacks; {count} floorplan bounds/overlap/area checks')
if __name__=='__main__':main()
