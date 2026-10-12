#!/usr/bin/env python3
"""Five-minute reference walkthrough, short live smoke run, or complete transient solve."""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT/'transient'
sys.path.insert(0,str(ROOT/'tools'))
from run_case import prepare, uncomment, validate_outputs
TAG = 'pan-tdp-735_1000-1010s_5ms'
STACKS = [TAG+'.stk','pan-tdp-735_mean_1000-1010s_5ms.stk',
          'pan-tdp-735_peak_1000-1010s_5ms.stk','pan-tdp-735.stk']

def verify():
    for entry in json.loads((ROOT/'provenance/transient-files.json').read_text()):
        p=ROOT/entry['path']
        if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=entry['sha256']:
            raise SystemExit(f'Demo asset changed or missing: {p}')

def analyze(work):
    slots=list(csv.DictReader((work/'slots_1000-1010s_5ms.csv').open()))
    warmup=sum(int(row['warmup']) for row in slots)
    env=os.environ.copy();env['MPLBACKEND']='Agg';env['MPLCONFIGDIR']=str(work/'.matplotlib')
    common=['--transient',STACKS[0],'--mean',STACKS[1],'--peak',STACKS[2]]
    subprocess.run([sys.executable,str(ROOT/'tools/tflp_metrics.py'),*common,
                    '--tdp',STACKS[3],'--warmup',str(warmup)],cwd=work,env=env,check=True)
    subprocess.run([sys.executable,str(DEMO/'analysis/demo_figure.py'),*common,
                    '--slots','slots_1000-1010s_5ms.csv'],cwd=work,env=env,check=True)
    generated=list(csv.DictReader((work/f'metrics_{TAG}.csv').open()))
    reference={(x['die'],x['element']):x for x in csv.DictReader((DEMO/'reference'/f'metrics_{TAG}.csv').open())}
    worst=0.
    for row in generated:
        ref=reference[(row['die'],row['element'])]
        for col in ('Tmin','Tmax','swing','dTdt','above_mean_pct','above_mean_by','peak_gap','tdp_gap'):
            worst=max(worst,abs(float(row[col])-float(ref[col])))
    (work/'analysis-check.json').write_text(json.dumps({'maximum_absolute_metric_difference':worst,
        'comparison':'against archived metrics CSV; generated from saved Tflp traces or fresh solve',
        'warmup_slots':warmup,'total_slots':len(slots)},indent=2)+'\n')
    print(f'Analysis complete; maximum metric difference vs archive: {worst:.6g}')
    if worst>0.02:
        raise SystemExit('Metrics exceed the archived-result tolerance; inspect analysis-check.json')

def solve(stk,work,emulator,cores):
    target=prepare(DEMO/'inputs'/stk,work,cores)
    env=os.environ.copy();env['OPENBLAS_NUM_THREADS']='1'
    start=time.monotonic()
    with (work/'simulator.log').open('w') as log:
        subprocess.run([str(emulator),target.name],cwd=work,env=env,stdout=log,
                       stderr=subprocess.STDOUT,check=True)
    validate_outputs(target)
    print(f'{stk}: {time.monotonic()-start:.1f} wall seconds',flush=True)
    return target

def smoke(work,emulator,cores,research_grid=False):
    # Preserve the package footprint/layers; coarsen only this synthetic demo's grid.
    target=prepare(DEMO/'inputs'/STACKS[0],work,cores)
    cell=(200,200) if research_grid else (898,400)
    shape=(449,122) if research_grid else (100,61)
    grid=f'cell length {cell[0]}, width {cell[1]} ;'
    text,n=re.subn(r'cell length\s+[\d.]+\s*,\s*width\s+[\d.]+\s*;',grid,target.read_text())
    if n!=1:raise SystemExit('Expected one rectangular grid in the panel stack')
    target.write_text(text)
    metadata=json.loads((work/'run.json').read_text())
    metadata['changes'] += ['synthetic 40-slot power queues',f'smoke grid: {cell[0]} x {cell[1]} um ({shape[0]} x {shape[1]} cells)']
    (work/'run.json').write_text(json.dumps(metadata,indent=2)+'\n')
    count=40
    names=[]
    for flp in sorted(work.glob('*.flp')):
        def queue(match):
            values=[float(x) for x in match[1].replace(',',' ').split()]
            # Two levels from the supplied trace, followed by a return to the first.
            base=values[0];high=max(values)
            sample=[base]*10+[high]*20+[base]*10
            return 'power values '+', '.join(f'{x:.9g}' for x in sample)+' ;'
        flp.write_text(re.sub(r'power values\s+([^;]+);',queue,flp.read_text()))
    env=os.environ.copy();env['OPENBLAS_NUM_THREADS']='1'
    start=time.monotonic()
    with (work/'simulator.log').open('w') as log:
        subprocess.run([str(emulator),target.name],cwd=work,env=env,
                       stdout=log,stderr=subprocess.STDOUT,check=True)
    validate_outputs(target)
    import numpy as np
    output=next((work/'outputs').glob('*die_pic_max*'))
    data=np.loadtxt(output,comments='%',ndmin=2)
    if len(data)!=count or abs(data[-1,0]-0.2)>1e-8:
        raise SystemExit(f'Unexpected smoke trace: shape={data.shape}, end={data[-1,0]}')
    if not np.isfinite(data).all() or not (data[:,1:].max()>data[0,1:].min()):
        raise SystemExit('Invalid smoke temperatures')
    (work/'smoke-check.json').write_text(json.dumps({'slots':count,'slot_s':0.005,
        'simulated_duration_s':0.2,'wall_seconds':time.monotonic()-start,
        'cell_um':cell,'grid_cells':shape,
        'purpose':'synthetic two-level solver smoke check; no paper/serving claim'},indent=2)+'\n')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    sys.path.insert(0,str(DEMO/'analysis'))
    from tflp_metrics import outputs, load
    out=outputs(target)
    curves={}
    for key,element in ((('DIE_PIC','maximum'),'PIC_A'),(('PIC_PLANE','maximum'),'CPL_A')):
        filename,names=out[key]; t,T=load(filename,len(names));curves[element]=(t,T[:,names.index(element)])
    fig,ax=plt.subplots(figsize=(7,3.5))
    ax.axvspan(0.05,0.15,color='0.92',label='High-power phase')
    for label,(t,y) in curves.items():ax.plot(t,y,label=label)
    title='Live panel smoke run: two-level power, '+('research grid' if research_grid else 'coarse demo grid')
    ax.set(xlabel='Simulation time (s)',ylabel='Temperature (°C)',title=title)
    ax.legend();ax.grid(alpha=.2);fig.tight_layout();fig.savefig(work/'smoke.png',dpi=170)
    plt.close(fig)
    print(f'PASS: {count} live transient slots; results: {work}')

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('mode',choices=['reference','smoke','simulate'],nargs='?',default='reference')
    ap.add_argument('--run-dir',type=Path)
    ap.add_argument('--emulator',type=Path,default=ROOT/'build/3d-ice/bin/3D-ICE-Emulator')
    ap.add_argument('--cores',type=int,default=12)
    ap.add_argument('--research-grid',action='store_true',help='smoke only: retain original 200 x 200 um grid; needs more memory')
    a=ap.parse_args()
    if a.cores<1:ap.error('--cores must be positive')
    if a.research_grid and a.mode!='smoke':ap.error('--research-grid is only for smoke mode')
    verify()
    work=(a.run_dir or ROOT/'runs'/('transient-'+a.mode)).resolve()
    if work.exists():raise SystemExit(f'Choose a new --run-dir; {work} already exists')
    if a.mode=='reference':
        shutil.copytree(DEMO/'inputs',work)
        (work/'outputs').mkdir()
        for folder in (DEMO/'reference/outputs').iterdir():
            for result in folder.glob('*.txt'):
                shutil.copy2(result,work/'outputs'/result.name)
        analyze(work)
    elif a.mode=='smoke':
        emulator=a.emulator.resolve()
        if not emulator.is_file():raise SystemExit('Build the solver first: bash tools/build.sh')
        os.environ['MPLCONFIGDIR']=str(work/'.matplotlib')
        smoke(work,emulator,a.cores,a.research_grid)
    else:
        emulator=a.emulator.resolve()
        if not emulator.is_file():raise SystemExit('Build the solver first: bash tools/build.sh')
        work.mkdir(parents=True)
        # Collect the actual fresh outputs into the original declared paths for analysis.
        for stk in STACKS:
            casework=work/Path(stk).stem
            staged=solve(stk,casework,emulator,a.cores)
            shutil.copy2(DEMO/'inputs'/stk,work/stk)
            raw=uncomment((DEMO/'inputs'/stk).read_text())
            for output in re.findall(r'"([^"]+\.txt)"',raw):
                source=casework/'outputs'/Path(output).name
                dest=work/output;dest.parent.mkdir(parents=True,exist_ok=True)
                shutil.copy2(source,dest)
        for src in (DEMO/'inputs').glob('*.flp'):shutil.copy2(src,work/src.name)
        shutil.copy2(DEMO/'inputs/slots_1000-1010s_5ms.csv',work/'slots_1000-1010s_5ms.csv')
        analyze(work)
    print(f'Demo files: {work}')

if __name__=='__main__':main()
