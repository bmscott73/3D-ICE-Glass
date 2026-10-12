#!/usr/bin/env python3
"""Stage a native case in an isolated directory and run stock 3D-ICE."""
import argparse
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]

def uncomment(text):
    return re.sub(r'//[^\n]*', '', text)

def floorplans(stack):
    return re.findall(r'floorplan\s+"([^"]+)"', uncomment(stack.read_text()))

def resolve_floorplan(stack, reference):
    # Old /workspace paths are relocated by basename, never read from that host.
    candidate = stack.parent / Path(reference).name
    if not Path(reference).is_absolute():
        exact = stack.parent / reference
        if exact.is_file():
            return exact
    if candidate.is_file():
        return candidate
    raise FileNotFoundError(f'{stack}: missing floorplan {reference}')

def prepare(stack, work, cores=None):
    work.mkdir(parents=True, exist_ok=False)
    text = stack.read_text()
    for reference in floorplans(stack):
        source = resolve_floorplan(stack, reference)
        shutil.copy2(source, work / source.name)
        text = text.replace('"'+reference+'"', '"'+source.name+'"')
    # Preserve output filenames, put every generated result in this run's outputs.
    before, marker, output = text.partition('output :')
    if not marker:
        before, marker, output = text.partition('output:')
    if not marker:
        raise ValueError(f'{stack}: missing output section')
    output = re.sub(r'"([^"]+)"', lambda m: '"outputs/'+Path(m[1]).name+'"', output)
    text = before + marker + output
    if cores is not None:
        text = re.sub(r'numofcores\s+\d+\s*;', f'numofcores {cores} ;', text)
    (work / 'outputs').mkdir()
    target = work / stack.name
    target.write_text(text)
    (work / 'run.json').write_text(json.dumps({'source_stack':str(stack.relative_to(ROOT)),
        'floorplans':[str(resolve_floorplan(stack, r).relative_to(ROOT)) for r in floorplans(stack)],
        'changes':['relocated floorplan paths','relocated output paths'] +
        ([f'numofcores={cores}'] if cores is not None else [])}, indent=2)+'\n')
    return target

def validate_outputs(stack):
    """Reject empty, non-finite, or truncated Tflp traces even if C returns zero."""
    text = uncomment(stack.read_text())
    die_files = dict(re.findall(r'die\s+(\w+)\s+\w+\s+floorplan\s+"([^"]+)"', text))
    maximum_slots = 1
    elements = {}
    for die, filename in die_files.items():
        flp = uncomment((stack.parent / filename).read_text())
        elements[die] = len(re.findall(r'^\s*([\w.\-]+)\s*:', flp, re.M))
        for q in re.findall(r'power values\s+([^;]+);', flp):
            maximum_slots = max(maximum_slots, len(q.replace(',', ' ').split()))
    checked = 0
    for die, filename, instant in re.findall(
            r'Tflp\s*\(\s*(\w+)\s*,\s*"([^"]+)"\s*,\s*\w+\s*,\s*(\w+)\s*\)', text):
        path = stack.parent / filename
        rows = [[float(v) for v in line.split()] for line in path.read_text().splitlines()
                if line.strip() and not line.lstrip().startswith('%')]
        if not rows or any(len(row) not in (elements[die], elements[die]+1) for row in rows):
            raise ValueError(f'{path}: empty or incorrect number of output columns')
        if not all(math.isfinite(value) for row in rows for value in row):
            raise ValueError(f'{path}: non-finite temperatures')
        if instant == 'slot' and len(rows) != maximum_slots:
            raise ValueError(f'{path}: {len(rows)} solved slots, expected {maximum_slots}')
        if instant == 'final' and len(rows) != 1:
            raise ValueError(f'{path}: expected one final output row')
        checked += 1
    if not checked:
        raise ValueError(f'{stack}: no Tflp outputs checked')
    return checked

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('stack', type=Path, help='path from repository root (or absolute)')
    ap.add_argument('--run-dir', type=Path)
    ap.add_argument('--emulator', type=Path, default=ROOT/'build/3d-ice/bin/3D-ICE-Emulator')
    ap.add_argument('--cores', type=int)
    ap.add_argument('--prepare-only', action='store_true')
    a = ap.parse_args()
    if a.cores is not None and a.cores < 1:
        ap.error('--cores must be positive')
    stack = a.stack.resolve() if a.stack.is_absolute() else (ROOT/a.stack).resolve()
    stack.relative_to(ROOT)
    work = (a.run_dir or ROOT/'runs'/stack.stem).resolve()
    target = prepare(stack, work, a.cores)
    print(f'Prepared {target}', flush=True)
    if a.prepare_only:
        return
    emulator = a.emulator.resolve()
    if not emulator.is_file():
        raise SystemExit('Build the emulator first: bash tools/build.sh')
    env = os.environ.copy()
    env['OPENBLAS_NUM_THREADS'] = '1'
    with (work/'simulator.log').open('w') as log:
        result = subprocess.run([str(emulator),target.name], cwd=work, env=env,
                                stdout=log, stderr=subprocess.STDOUT)
    print(f'Exit {result.returncode}; log: {work / "simulator.log"}', flush=True)
    if result.returncode:
        raise SystemExit(result.returncode)
    checked = validate_outputs(target)
    print(f'Validated {checked} numeric Tflp outputs', flush=True)

if __name__ == '__main__':
    main()
