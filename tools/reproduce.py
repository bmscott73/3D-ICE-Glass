#!/usr/bin/env python3
"""Run/check paper Table II and print its eight-checkpoint percentage aggregate."""
import argparse
import csv
import hashlib
import json
import math
import os
import re
from datetime import datetime
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from iceglass.inputs import active,blocks,floorplans,resolve,numeric_signature
from run_case import prepare,validate_outputs

def rows(path):
    for line in path.read_text().splitlines():
        if not line.strip() or line.lstrip().startswith('%'):continue
        values=list(map(float,line.split()))
        if not all(math.isfinite(v) for v in values):raise ValueError(f'{path}: non-finite result')
        yield values

def measure(case,work):
    values=[]
    for name in case['outputs']:
        path=work/'outputs'/name;data=list(rows(path))
        if not data:raise ValueError(f'{path}: empty output')
        if case['kind']=='map':values.extend(v for row in data for v in row)
        elif case['kind']=='probe':values.append(data[-1][-1])
        else:
            if len(data)!=1:raise ValueError(f'{path}: expected one steady final row')
            if case.get('elements_prefix'):
                raw=active((ROOT/case['stack']).read_text())
                output=re.search(r'Tflp\s*\(\s*(\w+)\s*,\s*"[^\"]*'+re.escape(name)+'"',raw)
                flp=re.search(r'die\s+'+output[1]+r'\s+\w+\s+floorplan\s+"([^\"]+)"',raw)
                names=[b['name'] for b in blocks(resolve(ROOT/case['stack'],flp[1]))]
                values.extend(data[0][i+1] for i,n in enumerate(names) if n.startswith(case['elements_prefix']))
            else:values.extend(data[0][1:])
    if not values:raise ValueError(f'{case["id"]}: no measured temperatures')
    return max(values)-273.15+case.get('correction_K',0)

def verify_inputs(case,work):
    source=ROOT/case['stack'];staged=work/source.name
    a=numeric_signature(source.read_text()).split('output:')[0]
    b=numeric_signature(staged.read_text()).split('output:')[0]
    if a!=b:raise ValueError(f'{case["id"]}: staged physics differs from active input')
    for ref in floorplans(source):
        original=resolve(source,ref);copy=work/original.name
        if numeric_signature(original.read_text())!=numeric_signature(copy.read_text()):
            raise ValueError(f'{case["id"]}: floorplan differs: {original.name}')
    validate_outputs(staged)

def show(result):
    print(f'{"Checkpoint":38} {"Model C":>8} {"Ref. C":>8} {"Delta K":>8} {"Tol. K":>7} Status')
    for r in result:
        if r['status']=='ERROR':print(f'{r["name"]:38} ERROR: {r["error"]}');continue
        print(f'{r["name"]:38} {r["actual_C"]:8.2f} {r["reference_C"]:8.2f} {r["delta_C"]:+8.2f} {r["tolerance_C"]:7.2f} {r["status"]}')
    eligible=[r for r in result if r['aggregate']]
    if len(eligible)==8 and all(r['status']=='PASS' for r in eligible):
        mape=sum(abs(r['delta_C'])/abs(r['reference_C']) for r in eligible)/8*100
        print(f'\nEight-checkpoint mean absolute percentage error: {mape:.3f}% (paper rounding: {mape:.1f}%)')
        print('Convention: reported Celsius reference values; H200 specification and PIC range rows excluded.')
        return mape
    if len(eligible)==8:print('\nAggregate unavailable: one or more scalar rows failed reproduction.')
    return None

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--case',nargs='+',help='checkpoint IDs; default: all ten paper rows')
    ap.add_argument('--results',type=Path,help='verify an existing isolated result directory')
    ap.add_argument('--recorded',action='store_true',help='print published release-check results; no new solve')
    ap.add_argument('--run-dir',type=Path)
    ap.add_argument('--cores',type=int,default=2)
    ap.add_argument('--emulator',type=Path,default=ROOT/'build/3d-ice/bin/3D-ICE-Emulator')
    a=ap.parse_args();cases=json.loads((ROOT/'validation/checkpoints.json').read_text())
    if a.cores<1:ap.error('--cores must be positive')
    if a.case:
        unknown=set(a.case)-{c['id'] for c in cases}
        if unknown:ap.error('unknown checkpoint: '+', '.join(sorted(unknown)))
        cases=[c for c in cases if c['id'] in a.case]
    if a.recorded:
        saved=json.loads((ROOT/'validation/verified-results.json').read_text())
        print('Recorded release checks (not a new simulation): '+saved['date'])
        show([r for r in saved['results'] if r['id'] in {c['id'] for c in cases}]);return
    base=(a.results or a.run_dir or ROOT/'runs'/('validation-'+time.strftime('%Y%m%d-%H%M%S'))).resolve()
    if not a.results:
        if not a.emulator.resolve().is_file():raise SystemExit('Build the emulator: bash tools/build.sh')
        base.mkdir(parents=True,exist_ok=False)
    result=[]
    for case in cases:
        work=base/case['id'];r={**case}
        try:
            if not a.results:
                target=prepare(ROOT/case['stack'],work,a.cores)
                with (work/'simulator.log').open('w') as log:
                    subprocess.run([str(a.emulator.resolve()),target.name],cwd=work,
                       env={**os.environ,'OPENBLAS_NUM_THREADS':'1'},stdout=log,stderr=subprocess.STDOUT,check=True)
            verify_inputs(case,work);value=measure(case,work)
            r.update(actual_C=value,delta_C=value-case['reference_C'],
                     model_error_C=value-case['expected_C'],
                     status='PASS' if abs(value-case['expected_C'])<=case['tolerance_C'] else 'FAIL')
        except (OSError,ValueError,subprocess.CalledProcessError) as e:r.update(status='ERROR',error=str(e))
        result.append(r)
    mape=show(result)
    record={'date':datetime.now().astimezone().date().isoformat(),'results_directory':str(base),'aggregate_percent':mape,'results':result}
    (base/'validation-table.json').write_text(json.dumps(record,indent=2)+'\n')
    with (base/'validation-table.csv').open('w',newline='') as f:
        columns=['id','name','metric','expected_C','actual_C','reference_C','delta_C','tolerance_C','status','aggregate']
        writer=csv.DictWriter(f,fieldnames=columns,extrasaction='ignore',lineterminator='\n');writer.writeheader();writer.writerows(result)
    print(f'\nResults: {base}')
    if any(r['status']!='PASS' for r in result):raise SystemExit(1)

if __name__=='__main__':main()
