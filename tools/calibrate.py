#!/usr/bin/env python3
"""Stage 1: extract CFD effective h, fit a copper TTV boundary, or convert sink R."""
import argparse
import csv
import json
import math
from pathlib import Path

def finite_positive(value,name):
    if not math.isfinite(value) or value<=0:raise ValueError(f'{name} must be finite and positive')
    return value

def cfd(path,projected_area_um2=None):
    with path.open() as f:patches=list(csv.DictReader(f))
    if not patches:raise ValueError('CFD CSV has no patches')
    q=0.;area=0.;denominator=0.
    for p in patches:
        a=finite_positive(float(p['area_um2']),'wall patch area')
        dt=float(p['wall_K'])-float(p['bulk_K']);power=float(p['heat_W'])
        if not math.isfinite(dt) or not math.isfinite(power):raise ValueError('CFD heat and temperature differences must be finite')
        if power*dt<0:raise ValueError('CFD heat convention must be positive into coolant when wall is hotter')
        q+=power;area+=a;denominator+=a*dt
    finite_positive(q,'net removed heat');finite_positive(denominator,'integrated wall-to-bulk difference')
    projected=finite_positive(area if projected_area_um2 is None else projected_area_um2,'projected area')
    delta=denominator/area;h=q/(projected*delta)
    return {'h_native_W_um2K':h,'h_W_m2K':h*1e12,'heat_W':q,'wetted_area_um2':area,
            'projected_area_um2':projected,'area_weighted_delta_K':delta,
            'method':'sum wall heat / (projected area * area-weighted wall-to-local-bulk delta)',
            'source':str(path),'reanchor_conditions':['coolant','flow regime','wall material','channel geometry']}

def ttv(path,area_mm2):
    a=finite_positive(area_mm2,'applied area')*1e6
    with path.open() as f:points=list(csv.DictReader(f))
    if not points:raise ValueError('TTV calibration CSV has no points')
    powers=[];deltas=[]
    for p in points:
        q=finite_positive(float(p['power_W']),'power')
        delta=finite_positive(float(p['case_C'])-float(p['saturation_C']),'case-to-saturation delta')
        powers.append(q);deltas.append(delta)
    resistance=sum(q*d for q,d in zip(powers,deltas))/sum(q*q for q in powers)
    h=1/(resistance*a)
    return {'h_native_W_um2K':h,'h_W_m2K':h*1e12,'R_case_sat_K_W':resistance,
            'G_W_K':1/resistance,'applied_area_mm2':area_mm2,'calibration_power_W':powers,
            'residual_K':[d-resistance*q for q,d in zip(powers,deltas)],
            'source':str(path),'scope':'case-to-local-saturation boundary; freeze before held-out powers'}

def air(resistance,area_mm2,sink_base_mm2=None):
    r=finite_positive(resistance,'sink resistance');a=finite_positive(area_mm2,'applied area')
    if sink_base_mm2 is not None:finite_positive(sink_base_mm2,'sink base area')
    g=1/r;h=g/(a*1e6)
    return {'G_W_K':g,'h_native_W_um2K':h,'h_W_m2K':h*1e12,'applied_area_mm2':a,
            'sink_base_area_mm2':sink_base_mm2,'base_overhang_ratio':sink_base_mm2/a if sink_base_mm2 else None,
            'scope':'measured sink-to-air R at declared ducted velocity, normalized to engine applied area'}

def main():
    ap=argparse.ArgumentParser(description=__doc__);sub=ap.add_subparsers(dest='kind',required=True)
    p=sub.add_parser('cfd');p.add_argument('csv',type=Path);p.add_argument('--projected-area-um2',type=float)
    p=sub.add_parser('ttv');p.add_argument('csv',type=Path);p.add_argument('--area-mm2',required=True,type=float)
    p=sub.add_parser('air');p.add_argument('--resistance-k-w',required=True,type=float);p.add_argument('--area-mm2',required=True,type=float);p.add_argument('--sink-base-mm2',type=float)
    for parser in sub.choices.values():parser.add_argument('--output',type=Path)
    a=ap.parse_args()
    try:
        data=cfd(a.csv,a.projected_area_um2) if a.kind=='cfd' else ttv(a.csv,a.area_mm2) if a.kind=='ttv' else air(a.resistance_k_w,a.area_mm2,a.sink_base_mm2)
    except (ValueError,KeyError) as e:ap.error(str(e))
    text=json.dumps(data,indent=2)+'\n';print(text,end='')
    if a.output:a.output.write_text(text)
if __name__=='__main__':main()
