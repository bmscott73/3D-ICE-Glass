#!/usr/bin/env python3
"""Build a library-based glass stack or create an area-preserving seed variant."""
import argparse
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from iceglass.builder import build,variant

def main():
    ap=argparse.ArgumentParser(description=__doc__);group=ap.add_mutually_exclusive_group(required=True)
    group.add_argument('--config',type=Path);group.add_argument('--from-stack',type=Path)
    ap.add_argument('--output',type=Path,required=True);ap.add_argument('--plate-factor',type=float);ap.add_argument('--cavity-factor',type=float);ap.add_argument('--reference-k',type=float);ap.add_argument('--power-scale',type=float,default=1)
    a=ap.parse_args()
    try:
        target=build(json.loads(a.config.read_text()),a.output) if a.config else variant(a.from_stack,a.output,a.plate_factor,a.cavity_factor,a.reference_k,a.power_scale)
    except (ValueError,KeyError) as e:ap.error(str(e))
    print(f'Built {target}; geometry and area checks are in {target.parent/"model.json"}')
if __name__=='__main__':main()
