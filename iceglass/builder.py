"""Build native stacks from library primitives, or create checked case variants."""
import json
import math
from pathlib import Path
import re
import shutil
from .inputs import active,blocks,dimensions,floorplans,resolve,geometry,refresh

ROOT=Path(__file__).resolve().parents[1]

def identifier(value):
    result=value.upper().replace('-','_')
    if not re.fullmatch(r'[A-Z][A-Z0-9_]*',result):raise ValueError(f'invalid native identifier: {value}')
    return result

def build(config,output):
    config=json.loads(json.dumps(config))
    name=config['name'];identifier(name)
    chip=config['chip_um'];cell=config['cell_um']
    if len(chip)!=2 or len(cell)!=2 or any(not math.isfinite(v) or v<=0 for v in [*chip,*cell]):raise ValueError('dimensions must be two finite positive values')
    if any(abs(c/g-round(c/g))>1e-8 for c,g in zip(chip,cell)):raise ValueError('uniform cell dimensions must divide the canvas')
    mode=config.get('solver',{});slot=mode.get('slot_s')
    die_blocks=[b for layer in config['layers'] if layer.get('kind')=='die' for b in layer['blocks']]
    counts={len(b['power_W']) for b in die_blocks}
    if not die_blocks or 0 in counts:raise ValueError('stack needs an active die with nonempty power queues')
    if slot is not None:
        step=mode.get('step_s',slot)
        if any(not math.isfinite(v) or v<=0 for v in [slot,step]) or step>slot or abs(slot/step-round(slot/step))>1e-8:raise ValueError('positive step must divide slot time')
        if len(counts-{1})>1:raise ValueError('transient power queues must have consistent lengths')
        samples=max(counts)
        for b in die_blocks:
            if len(b['power_W'])==1:b['power_W']=b['power_W']*samples
    elif counts!={1}:raise ValueError('steady builder blocks require one power value')
    materials=json.loads((ROOT/'library/materials.json').read_text())['materials']
    primitives=json.loads((ROOT/'library/primitives.json').read_text())['primitives']
    cooling=config.get('cooling',{});top=primitives[cooling['top']] if cooling.get('top') else None
    channel=primitives[cooling['channel']] if cooling.get('channel') else None
    if top and top['kind'] not in ('robin','conductance'):raise ValueError('top primitive must be a surface boundary')
    if channel and channel['kind']!='4rm':raise ValueError('channel primitive must be 4rm')
    if not top and not channel:raise ValueError('at least one heat-removal primitive is required')
    used={l['material'] for l in config['layers'] if l.get('kind')!='channel'}
    if channel:used.add(channel['wall_material'])
    if top and top.get('lumped_interface') and 'tim' in used:raise ValueError('lumped case boundary already includes TIM; choose a convective plate primitive for an explicit TIM')
    output=Path(output);output.mkdir(parents=True,exist_ok=False)
    sections=[]
    for key in sorted(used):
        m=materials[key];k=[v*1e-6 for v in m['conductivity_W_mK']];cv=m['volumetric_capacity_J_m3K']*1e-18
        values=[k[0]] if k[0]==k[1]==k[2] else k
        sections.append(f'material {identifier(key)} :\n    thermal conductivity '+', '.join(f'{v:.12g}' for v in values)+f' ;\n    volumetric heat capacity {cv:.12g} ;\n')
    inlet=cooling.get('reference_K',(top or channel)['reference_K'])
    if not math.isfinite(inlet) or inlet<=0:raise ValueError('reference must be finite positive kelvin')
    if top:
        h=(top['h_W_m2K']*1e-12 if top['kind']=='robin' else 1/(top['resistance_K_W']*chip[0]*chip[1]))
        sections.append(f'top heat sink :\n    heat transfer coefficient {h:.12g} ;\n    temperature {inlet:g} ;\n')
    channel_info=None
    if channel:
        w=channel['wall_um'];c=channel['channel_um'];first=channel['first_wall_um'];last=channel['last_wall_um']
        ratio=(chip[0]-first-last-c)/(w+c)
        if ratio<0 or abs(ratio-round(ratio))>1e-8:raise ValueError('4rm channel/fin/edge widths do not fit the canvas')
        n=int(round(ratio))+1;flow=channel['anchor_flow_ml_min']*n/channel['anchor_channels']
        channel_info={'channels':n,'flow_ml_min':flow,'velocity_matches_anchor':True}
        h=channel['h_native']
        sections.append(f'microchannel 4rm :\n    height {channel["height_um"]} ;\n    channel length {c} ;\n    wall length {w} ;\n    first wall length {first} ;\n    last wall length {last} ;\n    wall material {identifier(channel["wall_material"])} ;\n    coolant flow rate {flow:.12g} ;\n    coolant heat transfer coefficient side {h}, top {h}, bottom {h} ;\n    coolant volumetric heat capacity {channel["coolant_capacity_native"]} ;\n    coolant incoming temperature {inlet:g} ;\n')
    sections.append(f'dimensions :\n    chip length {chip[0]:g}, width {chip[1]:g} ;\n    cell length {cell[0]:g}, width {cell[1]:g} ;\n    non-uniform false ;\n')
    layer_defs=[];die_defs=[];stack=[];outputs=[];area_checks=[];ids=set();nchannel=0
    for layer in config['layers']:
        ident=identifier(layer['id'])
        if ident in ids:raise ValueError(f'duplicate stack ID {ident}')
        ids.add(ident);kind=layer.get('kind','layer')
        if kind not in ('layer','die','channel'):raise ValueError(f'unknown layer kind: {kind}')
        if kind=='channel':
            if not channel:raise ValueError('channel layer requires a cooling primitive')
            stack.append(f'    channel {ident} ;');nchannel+=1;continue
        material=identifier(layer['material'])
        if kind=='die':
            items=layer['blocks'];check=geometry(items,chip);area_checks.append({'die':ident,**check})
            if len({identifier(b['name']) for b in items})!=len(items):raise ValueError('block names collide after native identifier conversion')
            source=layer['source_um'];above=layer.get('passive_above_um',0);below=layer.get('passive_below_um',0)
            if any(not math.isfinite(v) for v in [source,above,below]) or source<=0 or min(above,below)<0:raise ValueError('die sublayer heights must be finite; source positive, passive nonnegative')
            lines=[f'die {ident}_D :']
            if above:lines.append(f'    layer {above:g} {material} ;')
            lines.append(f'    source {source:g} {material} ;')
            if below:lines.append(f'    layer {below:g} {material} ;')
            die_defs.append('\n'.join(lines)+'\n')
            fp=output/(ident.lower()+'.flp');data=[]
            for b in items:
                x,y=b['position_um'];w,h=b['size_um']
                data.append(f'{identifier(b["name"])} :\n    position {x:g}, {y:g} ;\n    dimension {w:g}, {h:g} ;\n    power values '+', '.join(f'{v:.12g}' for v in b['power_W'])+' ;\n')
            fp.write_text('\n'.join(data));refresh(fp)
            stack.append(f'    die {ident} {ident}_D floorplan "{fp.name}" ;')
            outputs.append(f'    Tflp( {ident}, "outputs/{ident.lower()}_max.txt", maximum, final ) ;')
        else:
            height=layer['height_um']
            if not math.isfinite(height) or height<=0:raise ValueError('layer height must be finite positive')
            layer_defs.append(f'layer {ident}_L :\n    height {height:g} ;\n    material {material} ;\n')
            stack.append(f'    layer {ident} {ident}_L ;')
    if channel and nchannel!=1:raise ValueError('a 4rm builder case must contain one channel layer')
    if not outputs:raise ValueError('stack needs an active die')
    if slot is not None:
        statement=f'transient step {step:g}, slot {slot:g} ;'
        outputs=[v.replace('final','slot') for v in outputs]
    else:
        statement='steady ;'
    text='\n'.join(sections+layer_defs+die_defs)+ '\nstack :\n'+'\n'.join(stack)+f'\n\nsolver :\n    {statement}\n    initial temperature {inlet:g} ;\n    numofcores 2 ;\n\noutput :\n'+'\n'.join(outputs)+'\n'
    target=output/(name+'.stk');target.write_text(text);refresh(target)
    (output/'model.json').write_text(json.dumps({'configuration':config,'area_checks':area_checks,'channel':channel_info,
        'calibration_status':'illustrative constructed case; confirm primitive transfer domain before claiming validation',
        'library_materials':sorted(used)},indent=2)+'\n')
    return target

def variant(source,output,plate_factor=None,cavity_factor=None,reference_K=None,power_scale=1.0):
    source=Path(source);output=Path(output)
    if not math.isfinite(power_scale) or power_scale<0:raise ValueError('power scale must be finite and nonnegative')
    output.mkdir(parents=True,exist_ok=False);text=active(source.read_text());chip,_=dimensions(text);checks=[]
    for ref in floorplans(source):
        src=resolve(source,ref);dest=output/src.name;items=blocks(src);before=geometry(items,chip)
        data=active(src.read_text())
        def scale(m):return 'power values '+', '.join(f'{float(v)*power_scale:.12g}' for v in m[1].replace(',',' ').split())+' ;'
        dest.write_text(re.sub(r'power values\s+([^;]+);',scale,data));after=geometry(blocks(dest),chip)
        if before['covered_area_um2']!=after['covered_area_um2']:raise ValueError('variant changed floorplan area')
        checks.append({'floorplan':dest.name,'area_preserved':True,**after});refresh(dest)
        text=text.replace('"'+ref+'"','"'+dest.name+'"')
    if plate_factor is not None:
        if not math.isfinite(plate_factor) or plate_factor<=0:raise ValueError('plate factor must be positive')
        text,n=re.subn(r'(top heat sink\s*:\s*heat transfer coefficient\s+)([-+\d.eE]+)',lambda m:m[1]+f'{float(m[2])*plate_factor:.12g}',text)
        if n!=1:raise ValueError('variant requires one top Robin boundary')
    if cavity_factor is not None:
        if not math.isfinite(cavity_factor) or cavity_factor<=0:raise ValueError('cavity factor must be positive')
        def cavity(m):return m[1]+re.sub(r'(side|top|bottom)(\s+)([-+\d.eE]+)',lambda v:v[1]+v[2]+f'{float(v[3])*cavity_factor:.12g}',m[2])+';'
        text,n=re.subn(r'(coolant heat transfer coefficient\s+)([^;]+);',cavity,text)
        if not n:raise ValueError('no prescribed cavity coefficient in seed')
    if reference_K is not None:
        if not math.isfinite(reference_K) or reference_K<=0:raise ValueError('reference must be positive kelvin')
        text=re.sub(r'((?:incoming |initial )?temperature\s+)[-+\d.eE]+',lambda m:m[1]+f'{reference_K:g}',text)
    a,sep,b=text.partition('output :');b=re.sub(r'"([^\"]+)"',lambda m:'"outputs/'+Path(m[1]).name+'"',b)
    target=output/source.name;target.write_text(a+sep+b);refresh(target)
    (output/'model.json').write_text(json.dumps({'seed':str(source),'plate_factor':plate_factor,'cavity_factor':cavity_factor,'reference_K':reference_K,'power_scale':power_scale,'checks':checks,'calibration_status':'coefficient/power sensitivity; verify anchor transfer domain'},indent=2)+'\n')
    return target
