#!/usr/bin/env python3
"""Plot a native steady Tmap and check its expected Celsius peak."""
import argparse
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('map',type=Path);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--expected-c',type=float);ap.add_argument('--tolerance-k',type=float,default=.1);a=ap.parse_args()
    T=np.loadtxt(a.map,comments='%',ndmin=2)
    if not np.isfinite(T).all() or T.min()<=0:raise SystemExit('Map must contain finite absolute temperatures in kelvin')
    T=T-273.15;peak=float(T.max());y,x=np.unravel_index(np.argmax(T),T.shape)
    if a.expected_c is not None and abs(peak-a.expected_c)>a.tolerance_k:raise SystemExit(f'Peak {peak:.3f} C differs from expected {a.expected_c:.3f} C')
    fig,ax=plt.subplots(figsize=(10,3.8));im=ax.imshow(T,origin='lower',cmap='inferno',aspect='auto',interpolation='nearest')
    ax.plot(x,y,'o',ms=10,mfc='none',mec='white',mew=1.5);ax.set(xlabel='x cell index',ylabel='y cell index',title=f'Memory-tier temperature | peak {peak:.3f} °C | {T.shape[1]} × {T.shape[0]} cells')
    fig.colorbar(im,ax=ax,label='Temperature (°C)');fig.tight_layout();a.output.parent.mkdir(parents=True,exist_ok=True);fig.savefig(a.output,dpi=200);plt.close(fig)
    a.output.with_suffix('.json').write_text(json.dumps({'source':str(a.map),'peak_C':peak,'shape':list(T.shape),'hottest_cell_xy':[int(x),int(y)]},indent=2)+'\n')
    print(f'Peak {peak:.3f} C; plotted {a.output}')
if __name__=='__main__':main()
