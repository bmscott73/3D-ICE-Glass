#!/usr/bin/env python3
"""
demo_figure.py - "one serving trace, two temperature histories" figure for the transient demo.

Three stacked panels on ONE shared time axis (no dual y-axis):
  (a) decode-node power from the trace, KV-reload windows shaded
  (b) temperature of the embedded PIC and of the waveguide-plane coupler (same degC axis),
      with the PIC's steady-state results at average and peak power as dashed references
  (c) |dT/dt| of both, log scale, with a reference thermo-optic tracking rate

Run from the folder you ran 3D-ICE in (needs tflp_metrics.py next to this script):
  python ../demo_figure.py --slots slots_1000-1010s_5ms.csv \
      --transient pan-tdp-735_1000-1010s_5ms.stk \
      --mean pan-tdp-735_mean_1000-1010s_5ms.stk --peak pan-tdp-735_peak_1000-1010s_5ms.stk
Options: --pic DIE_PIC:PIC_A  --plane PIC_PLANE:CPL_A  --zoom auto|none|t0,t1  --track-rate 62.5
Writes demo_<tag>_full.(png|pdf) and demo_<tag>_zoom.(png|pdf).
"""
import argparse, os, sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tflp_metrics import outputs, load          # reuse the .stk/.flp/Tflp parsing

INK, INK2, GRID, SHADE, SURF = "#0b0b0b", "#52514e", "#e6e5e1", "#ecebe7", "#ffffff"
C_PIC, C_CPL, C_POW = "#2a78d6", "#eb6834", "#52514e"


def series(stk, die_el, stat="maximum"):
    die, el = die_el.split(":")
    fn, names = outputs(stk)[(die, stat)]
    if el not in names:
        raise SystemExit(f"{el} not in {die} floorplan: {names}")
    t, T = load(fn, len(names))
    return T[:, names.index(el)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slots", required=True); ap.add_argument("--transient", required=True)
    ap.add_argument("--mean"); ap.add_argument("--peak")
    ap.add_argument("--pic", default="DIE_PIC:PIC_A"); ap.add_argument("--plane", default="PIC_PLANE:CPL_A")
    ap.add_argument("--zoom", default="auto"); ap.add_argument("--track-rate", type=float, default=62.5)
    ap.add_argument("--label-pic", default="Embedded PIC (beneath logic)")
    ap.add_argument("--label-plane", default="Coupler, glass waveguide plane")
    a = ap.parse_args()

    S = pd.read_csv(a.slots)
    slot = float(S.t_start_s.values[1] - S.t_start_s.values[0])
    nw = int(S.warmup.sum())
    W = S[S.warmup == 0].reset_index(drop=True)
    t_pow = W.t_start_s.values - W.t_start_s.values[0]
    p = W.total.values                                   # per decode node, W

    Tp, Tc = series(a.transient, a.pic), series(a.transient, a.plane)
    if len(Tp) == len(S) + 1:                            # tolerate an initial-state row
        Tp, Tc = Tp[1:], Tc[1:]
    if len(Tp) != len(S):
        raise SystemExit(f"{len(Tp)} temperature rows vs {len(S)} slots; check --slots matches the run")
    Tp, Tc = Tp[nw:], Tc[nw:]
    t_T = (np.arange(len(Tp)) + 1) * slot                # temperature at the END of each slot
    ref = {}
    for k in ("mean", "peak"):
        if getattr(a, k):
            ref[k] = series(getattr(a, k), a.pic)[-1]

    reload = W.reload_frac.values > 0.5                   # KV-reload slots
    edges = np.flatnonzero(np.diff(np.r_[0, reload.astype(int), 0]))
    spans = [(t_pow[s], t_pow[min(e, len(t_pow) - 1)] + slot) for s, e in zip(edges[::2], edges[1::2])]

    tag = os.path.splitext(os.path.basename(a.transient))[0]
    dur = round(len(W) * slot, 3)
    views = [("full", (0, t_pow[-1] + slot))]
    if a.zoom != "none":
        if a.zoom == "auto":                              # 2 s around the hottest PIC moment
            tc = t_T[np.argmax(Tp)]; z0 = min(max(tc - 1.2, 0), t_pow[-1] + slot - 2)
            views.append(("zoom", (z0, z0 + 2)))
        else:
            z = [float(x) for x in a.zoom.split(",")]; views.append(("zoom", tuple(z)))

    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 9, "axes.edgecolor": INK2, "axes.labelcolor": INK2,
                         "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False,
                         "axes.spines.right": False, "axes.grid": True, "grid.color": GRID,
                         "grid.linewidth": 0.8, "figure.facecolor": SURF, "axes.facecolor": SURF})
    for name, (x0, x1) in views:
        fig, ax = plt.subplots(3, 1, figsize=(7.2, 6.4), sharex=True,
                               gridspec_kw={"height_ratios": [1, 1.5, 1.2]})
        for axi in ax:
            for s0, s1 in spans:
                if s1 > x0 and s0 < x1:
                    axi.axvspan(s0, s1, color=SHADE, lw=0, zorder=0)
        # (a) power
        ax[0].step(t_pow, p, where="post", color=C_POW, lw=1.4)
        ax[0].set_ylabel("Decode-node\npower (W)"); ax[0].set_ylim(0, max(p) * 1.12)
        ax[0].set_title("(a) Serving trace: decode steps vs. KV-cache reloads (shaded)",
                        loc="left", fontsize=9, color=INK)
        # (b) temperatures
        m = (t_T >= x0) & (t_T <= x1)
        ax[1].plot(t_T, Tp, color=C_PIC, lw=1.8)
        ax[1].plot(t_T, Tc, color=C_CPL, lw=1.8)
        for k, ls in (("peak", (0, (4, 3))), ("mean", (0, (1, 2)))):
            if k in ref:
                ax[1].axhline(ref[k], color=INK2, lw=1, ls=ls)
                ax[1].text(x0 + 0.01 * (x1 - x0), ref[k], f"PIC steady state, {k} power",
                           va="bottom", fontsize=7.5, color=INK2, zorder=5,
                           bbox=dict(facecolor=SURF, edgecolor="none", pad=1.2, alpha=0.9))
        lo = min(Tp[m].min(), Tc[m].min()); hi = max(Tp[m].max(), ref.get("peak", -1e9))
        ax[1].set_ylim(lo - 2, hi + 3)
        xe = t_T[m][-1]
        ax[1].text(xe, Tp[m][-1], "  PIC", color=INK, fontsize=8, va="center")
        ax[1].text(xe, Tc[m][-1], "  coupler", color=INK, fontsize=8, va="center")
        ax[1].set_ylabel("Temperature (°C)")
        ax[1].set_title(f"(b) Same workload, two temperature histories  "
                        f"({dur:g} s swing: {np.ptp(Tp):.1f} K vs {np.ptp(Tc):.1f} K)",
                        loc="left", fontsize=9, color=INK)
        # (c) rates
        tr = t_T[1:] - slot / 2
        rp = np.clip(np.abs(np.diff(Tp)) / slot, 0.1, None)
        rc = np.clip(np.abs(np.diff(Tc)) / slot, 0.1, None)
        ax[2].plot(tr, rp, color=C_PIC, lw=1.3); ax[2].plot(tr, rc, color=C_CPL, lw=1.3)
        ax[2].set_yscale("log")
        ax[2].axhline(a.track_rate, color=INK2, lw=1, ls=(0, (4, 3)))
        ax[2].text(x1 - 0.01 * (x1 - x0), a.track_rate * 0.8, f"reported thermo-optic tracking "
                   f"rate, {a.track_rate:g} K/s", ha="right", va="top", fontsize=7.5, color=INK2,
                   bbox=dict(facecolor=SURF, edgecolor="none", pad=1.5, alpha=0.9), zorder=5)
        ax[2].set_ylabel("|dT/dt| (K/s)"); ax[2].set_xlabel("Time in window (s)")
        ax[2].set_title(f"(c) Rate of change over 5 ms  ({dur:g} s max: {rp.max():.0f} K/s vs {rc.max():.0f} K/s)",
                        loc="left", fontsize=9, color=INK)
        ax[2].set_xlim(x0, x1)
        from matplotlib.lines import Line2D
        fig.legend(handles=[Line2D([], [], color=C_PIC, lw=2, label=a.label_pic),
                            Line2D([], [], color=C_CPL, lw=2, label=a.label_plane)],
                   loc="lower center", ncol=2, frameon=False, fontsize=8.5, bbox_to_anchor=(0.5, 0))
        fig.tight_layout(rect=(0, 0.04, 1, 1))
        for ext in ("png", "pdf"):
            fig.savefig(f"demo_{tag}_{name}.{ext}", dpi=200)
        plt.close(fig)
        print(f"wrote demo_{tag}_{name}.png/.pdf  ({x0:.2f}-{x1:.2f} s)")


if __name__ == "__main__":
    main()
