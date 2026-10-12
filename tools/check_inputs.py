#!/usr/bin/env python3
"""Verify project hashes, pinned source, stack dependencies, and native power queues."""
import hashlib
import json
from pathlib import Path
import re
import sys
from run_case import ROOT, floorplans, resolve_floorplan, uncomment

def check():
    errors = []
    manifest = json.loads((ROOT/'provenance/files.json').read_text())
    for x in manifest:
        p = ROOT/x['path']
        if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest() != x['sha256']:
            errors.append(f"Project asset changed or missing: {x['path']}")
    upstream = json.loads((ROOT/'provenance/upstream.json').read_text())
    for x in upstream['files']:
        p = ROOT/'vendor/3d-ice'/x['path']
        if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest() != x['sha256']:
            errors.append(f"Pinned upstream asset changed or missing: {x['path']}")
    stacks = sorted(p for folder in ('models','validation','transient/inputs')
                    for p in (ROOT/folder).rglob('*.stk') if 'provenance' not in p.parts)
    for stack in stacks:
        counts = set()
        for reference in floorplans(stack):
            try:
                flp = resolve_floorplan(stack, reference)
                text = uncomment(flp.read_text())
                names = re.findall(r'^\s*([\w.\-]+)\s*:', text, re.M)
                if len(names) != len(set(names)):
                    errors.append(f'{flp}: duplicate block names')
                queues = re.findall(r'power values\s+([^;]+);', text)
                if len(queues) != len(names):
                    errors.append(f'{flp}: {len(names)} blocks but {len(queues)} power queues')
                for queue in queues:
                    values = [float(x) for x in queue.replace(',',' ').split()]
                    if not values:
                        errors.append(f'{flp}: empty power queue')
                    counts.add(len(values))
            except (FileNotFoundError,ValueError) as ex:
                errors.append(str(ex))
        if len(counts)>1:
            errors.append(f'{stack}: inconsistent transient power queue lengths {counts}')
    if errors:
        print('\n'.join(errors), file=sys.stderr)
        return 1
    print(f'PASS: {len(manifest)} project assets, {len(upstream["files"])} upstream assets, '
          f'{len(stacks)} stack dependency/power checks')
    return 0

if __name__ == '__main__':
    raise SystemExit(check())
