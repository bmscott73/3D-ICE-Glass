"""Read native rectangular 3D-ICE inputs without depending on the emulator."""
import math
from pathlib import Path
import re

NUMBER=r'[-+\d.eE]+'

def active(text):
    return re.sub(r'//[^\n]*','',text)

def blocks(path):
    text=active(Path(path).read_text())
    parts=re.split(r'^\s*([\w.\-]+)\s*:',text,flags=re.M)
    result=[]
    for name,body in zip(parts[1::2],parts[2::2]):
        pos=re.search(r'position\s+('+NUMBER+r')\s*,\s*('+NUMBER+r')\s*;',body)
        dim=re.search(r'dimension\s+('+NUMBER+r')\s*,\s*('+NUMBER+r')\s*;',body)
        q=re.search(r'power values\s+([^;]+);',body)
        if not (pos and dim and q):raise ValueError(f'{path}: incomplete rectangle {name}')
        result.append({'name':name,'position_um':list(map(float,pos.groups())),
            'size_um':list(map(float,dim.groups())),
            'power_W':[float(v) for v in q[1].replace(',',' ').split()]})
    if not result:raise ValueError(f'{path}: no rectangular power blocks')
    return result

def geometry(items,chip_um,check_overlap=True):
    names=set(); area=0.;powered=0.
    for b in items:
        name=b['name'];x,y=b['position_um'];w,h=b['size_um'];powers=b['power_W']
        if name in names:raise ValueError(f'duplicate block {name}')
        names.add(name)
        if not all(math.isfinite(v) for v in [x,y,w,h,*powers]):raise ValueError(f'{name}: non-finite value')
        if min(x,y)<0 or min(w,h)<=0 or x+w>chip_um[0]+1e-6 or y+h>chip_um[1]+1e-6:
            raise ValueError(f'{name}: rectangle outside {chip_um} um canvas')
        if not powers or min(powers)<0:raise ValueError(f'{name}: empty or negative power queue')
        area+=w*h
        if max(powers)>0:powered+=w*h
    if check_overlap:
        for i,a in enumerate(items):
            x,y=a['position_um'];w,h=a['size_um']
            for b in items[i+1:]:
                xx,yy=b['position_um'];ww,hh=b['size_um']
                if min(x+w,xx+ww)-max(x,xx)>1e-6 and min(y+h,yy+hh)-max(y,yy)>1e-6:
                    raise ValueError(f'overlapping blocks {a["name"]} / {b["name"]}')
    return {'blocks':len(items),'covered_area_um2':area,'powered_area_um2':powered,
            'first_sample_power_W':sum(b['power_W'][0] for b in items)}

def dimensions(text):
    text=active(text)
    def pair(keyword):
        m=re.search(keyword+r' length\s+('+NUMBER+r')\s*,\s*width\s+('+NUMBER+r')',text)
        if not m:raise ValueError(f'missing {keyword} dimensions')
        return list(map(float,m.groups()))
    return pair('chip'),pair('cell')

def floorplans(stack):
    return re.findall(r'floorplan\s+"([^"]+)"',active(Path(stack).read_text()))

def resolve(stack,ref):
    p=Path(stack).parent/ref
    if p.is_file():return p
    p=Path(stack).parent/Path(ref).name
    if p.is_file():return p
    raise FileNotFoundError(f'{stack}: unresolved floorplan {ref}')

def describe(stack):
    text=active(Path(stack).read_text());chip,cell=dimensions(text)
    flps=[resolve(stack,r) for r in floorplans(stack)]
    queues=[b['power_W'] for f in flps for b in blocks(f)]
    count=max(map(len,queues))
    if any(len(q)!=count for q in queues):raise ValueError(f'{stack}: inconsistent native power queues')
    totals=[sum(q[i] for q in queues) for i in range(count)]
    sinks=[]
    for side,body in re.findall(r'((?:top|bottom) heat sink)\s*:\s*(.*?)(?=dimensions\s*:|material\s+|(?:top|bottom) heat sink\s*:|microchannel|layer\s+)',text,re.S):
        h=re.search(r'heat transfer coefficient\s+('+NUMBER+r')',body);t=re.search(r'\btemperature\s+('+NUMBER+r')',body)
        if h and t:sinks.append({'side':side.split()[0],'h_native':float(h[1]),'reference_K':float(t[1])})
    channels=[]
    for kind,body in re.findall(r'(microchannel\s+\w+|pinfin)\s*:\s*(.*?)(?=dimensions\s*:|layer\s+)',text,re.S):
        model=kind.split()[-1]
        flow=re.search(r'(?:coolant flow rate|darcy velocity)\s+('+NUMBER+r')',body)
        inlet=re.search(r'coolant incoming temperature\s+('+NUMBER+r')',body)
        h=re.search(r'coolant heat transfer coefficient\s+(.*?);',body,re.S)
        channels.append({'model':model,'flow_or_velocity':float(flow[1]) if flow else None,
                         'flow_unit':'mL/min' if 'coolant flow rate' in body else 'um/s',
                         'inlet_K':float(inlet[1]) if inlet else None,
                         'htc_statement':' '.join(h[1].split()) if h else None})
    return {'chip_um':chip,'cell_um':cell,'power_samples':count,'power_first_W':totals[0],
            'power_range_W':[min(totals),max(totals)],'boundaries':sinks,'channels':channels}

def numeric_signature(text):
    text=active(text)
    text=re.sub(r'numofcores\s+\d+\s*;','numofcores N;',text)
    text=re.sub(r'"[^"]*"','"PATH"',text)
    return re.sub(r'\s+','',text)

def refresh(path):
    """Replace all historical comments with one header derived from active data."""
    path=Path(path);body='\n'.join(line.rstrip() for line in active(path.read_text()).splitlines()).strip()
    body=re.sub(r'\n\s*\n+', '\n\n',body)
    if path.suffix=='.stk':
        info=describe(path);c=info['chip_um'];g=info['cell_um']
        lines=[f'// 3D-ICE-Glass | {path.name} | generated from active statements',
          '// SPDX-License-Identifier: CC-BY-4.0',
          f'// Canvas {c[0]:g} x {c[1]:g} um; grid {g[0]:g} x {g[1]:g} um.',
          f'// Source power: first {info["power_first_W"]:.6g} W; range {info["power_range_W"][0]:.6g}..{info["power_range_W"][1]:.6g} W; {info["power_samples"]} sample(s).']
        for s in info['boundaries']:lines.append(f'// {s["side"].capitalize()} boundary: h={s["h_native"]:.9g} W/um2K ({s["h_native"]*1e12:.9g} W/m2K), reference={s["reference_K"]:g} K.')
        if not info['boundaries']:lines.append('// External faces: adiabatic; coolant channel is the heat-removal boundary.')
        for ch in info['channels']:lines.append(f'// Embedded cooling {ch["model"]}: flow/velocity={ch["flow_or_velocity"]} {ch["flow_unit"]}; inlet={ch["inlet_K"]} K; h={ch["htc_statement"] or "engine correlation"}.')
        lines+=['// Temperatures in emulator outputs are kelvin; time is seconds.','// Model data: CC-BY-4.0. References and observation planes: checkpoint README / docs/case-index.md.']
    else:
        bs=blocks(path);power=sum(b['power_W'][0] for b in bs);count=max(len(b['power_W']) for b in bs)
        area=sum(b['size_um'][0]*b['size_um'][1] for b in bs if max(b['power_W'])>0)
        lines=[f'// 3D-ICE-Glass | {path.name} | generated from active statements',
               '// SPDX-License-Identifier: CC-BY-4.0',
               f'// {len(bs)} rectangles; first-sample power {power:.6g} W; {count} power sample(s); powered footprint {area/1e6:.6g} mm2.',
               '// Positions/dimensions: um. Power: W. Model data: CC-BY-4.0.']
    path.write_text('\n'.join(lines)+'\n\n'+body+'\n')
