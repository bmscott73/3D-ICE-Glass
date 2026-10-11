#!/usr/bin/env python3
"""
tflp_metrics.py - the three abstract numbers from 3D-ICE Tflp outputs.

  python tflp_metrics.py --transient xpu_flp.txt --warmup 4000 --slot-ms 5 \
         --static-mean mean/xpu_flp.txt --static-peak peak/xpu_flp.txt

Per floorplan element it reports:
  swing      : max - min temperature during the window (K)
  max dT/dt  : largest temperature change rate (K/s)
  >static-avg: % of time ABOVE what a static run at average power predicts, and by how much
  peak gap   : static-at-peak temperature minus the real transient maximum (K) = over-design
Temperatures are read in K (3D-ICE default) and reported in degC.
"""
import argparse
import numpy as np


def load(fn):
    names = None
    for line in open(fn):
        if line.lstrip().startswith("%"):
            toks = line.strip().lstrip("%").split()
            if toks:
                names = toks
    d = np.loadtxt(fn, comments="%", ndmin=2)
    if d.max() > 200:
        d = d.copy(); d[:, 1:] -= 273.15 if d.shape[1] > 1 else 0
    return d, names


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--transient", required=True)
    ap.add_argument("--warmup", type=int, default=0)
    ap.add_argument("--slot-ms", type=float, default=5)
    ap.add_argument("--static-mean"); ap.add_argument("--static-peak")
    a = ap.parse_args()
    d, names = load(a.transient)
    T = d[a.warmup:, 1:]                 # column 0 = time
    ncol = T.shape[1]
    if not names or len(names) < ncol:
        names = [f"col{i}" for i in range(ncol)]
    names = names[-ncol:]
    Tm = load(a.static_mean)[0][-1, 1:] if a.static_mean else None
    Tp = load(a.static_peak)[0][-1, 1:] if a.static_peak else None
    dt = a.slot_ms / 1e3
    hdr = f"{'element':<22}{'Tmin':>7}{'Tmax':>7}{'swing':>7}{'dT/dt max':>11}"
    hdr += f"{'>static-avg':>13}{'by up to':>10}" if Tm is not None else ""
    hdr += f"{'peak gap':>10}" if Tp is not None else ""
    print(hdr + "\n" + "-" * len(hdr))
    for i in range(ncol):
        y = T[:, i]
        row = f"{names[i]:<22}{y.min():7.1f}{y.max():7.1f}{np.ptp(y):7.2f}" \
              f"{np.abs(np.diff(y)).max() / dt:9.0f} K/s"
        if Tm is not None:
            row += f"{100 * (y > Tm[i]).mean():11.1f} %{(y - Tm[i]).max():8.2f} K"
        if Tp is not None:
            row += f"{Tp[i] - y.max():8.2f} K"
        print(row)


if __name__ == "__main__":
    main()
