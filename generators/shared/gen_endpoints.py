#!/usr/bin/env python3
"""Generate current warm-loop endpoints from frozen water-case inputs."""
import argparse
import json
from pathlib import Path
import re
import sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from iceglass.builder import variant
from iceglass.inputs import active,refresh

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    a.output.mkdir(parents=True,exist_ok=False)
    seeds={'co-planar':ROOT/'models/co-planar/water/static-standard.stk',
           'dual-side':ROOT/'models/dual-side/warm-loop/d2air-4ms-735.stk',
           'interlayer':ROOT/'models/interlayer/water/emb-E4-std.stk',
           'panel-tdp':ROOT/'models/panel/provisioning/pan-tdp.stk',
           'panel-workload':ROOT/'models/panel/provisioning/pan-wl.stk'}
    for family,seed in seeds.items():
        text=active(seed.read_text());h=float(re.search(r'top heat sink\s*:\s*heat transfer coefficient\s+([-+\d.eE]+)',text)[1])
        for label,factor in [('735',.735),('575',.575)]:
            target=variant(seed,a.output/(family+'-'+label),plate_factor=4.08e-8*factor/h,
                           cavity_factor=.735 if family=='interlayer' else None,reference_K=308)
            if family=='interlayer':
                s=re.sub(r'(coolant volumetric heat capacity\s+)[-+\d.eE]+',r'\g<1>3.95e-12',target.read_text());target.write_text(s);refresh(target)
            meta=target.parent/'model.json';record=json.loads(meta.read_text())
            record['water_plate_factor']=factor;record['property_envelope']=True
            if family=='interlayer':record['coolant_volumetric_capacity_native']=3.95e-12
            meta.write_text(json.dumps(record,indent=2)+'\n')
    print(f'Built ten property-envelope endpoints in {a.output}')
if __name__=='__main__':main()
