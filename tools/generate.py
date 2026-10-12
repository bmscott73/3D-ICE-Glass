#!/usr/bin/env python3
"""Regenerate architecture floorplans and stacks in a new isolated workspace."""
import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from iceglass.inputs import active,blocks,dimensions,floorplans,geometry,refresh,resolve
SCRIPTS={'co-planar':['gen_bridge_flps.py','build_bridge_stks.py'],
         'dual-side':['gen_dual.py','build_dual_stks.py'],
         'interlayer':['gen_embedded.py','build_embedded_stks.py'],
         'panel':['gen_pan_flps.py','build_pan_stks.py','gen_prov.py'],
         'photonic':['gen_cpo_flps.py'], 'matrix':['build_matrix.py']}

def generate(family,work):
    work.mkdir(parents=True,exist_ok=False)
    if family=='co-planar':
        for p in (ROOT/'validation/stratum-s/inputs').glob('*.flp'):shutil.copy2(p,work)
    if family=='interlayer':shutil.copy2(ROOT/'validation/hyflex-microchannel/inputs/hfp_chiplet_duty.flp',work)
    if family=='interlayer':
        for name in ('die_top_bridge.flp','die_bot_bridge.flp','pic_plane_bridge.flp'):
            shutil.copy2(ROOT/'models/interlayer/water'/name,work)
    if family=='panel':shutil.copy2(ROOT/'models/panel/trace-floor/pan-std.stk',work)
    if family=='matrix':
        for folder in ('models/co-planar/warm-loop','models/dual-side/water'):
            for p in (ROOT/folder).glob('*.flp'):shutil.copy2(p,work)
    commands=[]
    for name in SCRIPTS[family]:
        script=ROOT/'generators'/('shared' if family=='matrix' else family)/name;commands.append(str(script.relative_to(ROOT)))
        subprocess.run([sys.executable,str(script)],cwd=work,check=True)
    if family=='panel':
        # Keep one generated water seed, rather than a copied and generated duplicate.
        (work/'pan-std.stk').unlink();shutil.copy2(work/'runs/pan-std.stk',work/'pan-std.stk')
    checks=[]
    for stk in sorted(work.rglob('*.stk')):
        text=active(stk.read_text())
        for ref in floorplans(stk):
            try:source=resolve(stk,ref)
            except FileNotFoundError:source=work/Path(ref).name
            if not source.is_file():raise ValueError(f'{stk}: generator dependency missing: {ref}')
            destination=stk.parent/source.name
            if source.resolve()!=destination.resolve():shutil.copy2(source,destination)
            text=text.replace('"'+ref+'"','"'+destination.name+'"')
        a,sep,b=text.partition('output :');b=re.sub(r'"([^\"]+)"',lambda m:'"outputs/'+Path(m[1]).name+'"',b)
        stk.write_text(a+sep+b);chip,_=dimensions(text)
        for ref in floorplans(stk):checks.append({'stack':str(stk.relative_to(work)),'floorplan':ref,**geometry(blocks(resolve(stk,ref)),chip)})
        refresh(stk)
    for flp in work.rglob('*.flp'):refresh(flp)
    if not checks:
        for flp in work.glob('*.flp'):checks.append({'floorplan':flp.name,**geometry(blocks(flp),[40000,30000])})
    (work/'generation.json').write_text(json.dumps({'family':family,'scripts':commands,'geometry_checks':checks,'scope':'generated exploration variants; paper checkpoint inputs remain in validation/'},indent=2)+'\n')
    print(f'{family}: generated and checked {len(checks)} floorplan uses in {work}')

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('family',choices=[*SCRIPTS,'all']);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    if a.family=='all':
        if a.output.exists():raise SystemExit('Choose a new output directory')
        a.output.mkdir(parents=True)
        for family in SCRIPTS:generate(family,a.output/family)
    else:generate(a.family,a.output)
if __name__=='__main__':main()
