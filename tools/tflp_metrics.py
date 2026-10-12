#!/usr/bin/env python3
"""
tflp_metrics.py - compare one 3D-ICE transient run against static runs, for every die at once.

  python tflp_metrics.py --transient pan-tdp-735_1000-1001s_5ms.stk --warmup 200 \
         --mean pan-tdp-735_mean_1000-1010s_5ms.stk \
         --peak pan-tdp-735_peak_1000-1010s_5ms.stk \
         --tdp  pan-tdp-735.stk

It reads each .stk to find every Tflp output (die, file, maximum/average/minimum) and the
die's .flp (for element names, in floorplan order), matching dynamic run suffixes automatically.

Per die and element (default: the 'maximum' outputs, FILL elements skipped):
  Tmin / Tmax / swing   transient range over the window (after warm-up), degC
  dT/dt                 largest rate of change, K/s
  >mean %  / by         % of time above the static average-power result, and the max excess (K)
  peak gap              static peak-power result minus the transient max (K) = over-design
  tdp gap               static TDP result minus the transient max (K)
Writes metrics_<tag>.csv and metrics_<tag>.png (hottest element per die vs time + static lines).
"""
import argparse, os, re
import numpy as np

TFLP = re.compile(r'Tflp\s*\(\s*(\w+)\s*,\s*"([^"]+)"\s*,\s*(maximum|average|minimum)\s*,\s*(\w+)\s*\)')
DIE_FLP = re.compile(r'die\s+(\w+)\s+\w+\s+floorplan\s+"([^"]+)"')
HDR = re.compile(r"^[ \t]*([A-Za-z_][\w.\-]*)[ \t]*:", re.M)
SKIP = re.compile(r"^FILL", re.I)
STAT_MAP = {"maximum": "max", "average": "ave", "minimum": "min"}


def get_out_dir(stk_path):
    """Map .stk filename to its designated output directory."""
    fname = os.path.basename(stk_path)
    if "mean" in fname:
        return "outputs-pan-mean"
    elif "peak" in fname:
        return "outputs-pan-peak"
    elif "1000-1010s" in fname:
        return "outputs-pan-10"
    return "outputs-pan"


def resolve_output_file(base_dir, out_dir, raw_fn, die, stat):
    """Find the output file matching die and statistic regardless of case or run suffixes."""
    target_dir = os.path.join(base_dir, out_dir) if out_dir else base_dir
    file_only = os.path.basename(raw_fn)

    # 1. Direct path check (exact filename match)
    for c in [os.path.join(target_dir, file_only), os.path.join(base_dir, file_only), os.path.join(base_dir, raw_fn)]:
        if os.path.exists(c):
            return c

    d_lower = die.lower()
    s_lower = STAT_MAP.get(stat.lower(), stat[:3].lower())

    # 2. Case-insensitive pattern match inside target_dir
    if os.path.exists(target_dir):
        files = os.listdir(target_dir)
        matches = [f for f in files if d_lower in f.lower() and f"_{s_lower}_" in f.lower()]
        
        if d_lower == "die_pic":
            matches = [f for f in matches if "pic_plane" not in f.lower()]

        if matches:
            return os.path.join(target_dir, sorted(matches)[0])

    # 3. Case-insensitive recursive fallback search
    for root, _, files in os.walk(base_dir):
        m = [f for f in files if d_lower in f.lower() and f"_{s_lower}_" in f.lower()]
        if d_lower == "die_pic":
            m = [f for f in m if "pic_plane" not in f.lower()]
        if m:
            return os.path.join(root, sorted(m)[0])

    return None


def outputs(stk):
    """{(die, stat): (file, [element names])} for every Tflp line in a .stk."""
    base = os.path.dirname(os.path.abspath(stk))
    txt = open(stk).read()
    flp = {d: os.path.join(base, f) for d, f in DIE_FLP.findall(txt)}
    out_dir = get_out_dir(stk)
    res = {}
    
    for die, fn, stat, _ in TFLP.findall(txt):
        names = [n for n in HDR.findall(open(flp[die]).read())] if die in flp else None
        full_path = resolve_output_file(base, out_dir, fn, die, stat)
        
        if not full_path:
            stk_name = os.path.basename(stk)
            raise SystemExit(
                f"\n[Error] No output file matching die '{die}' ({stat}) "
                f"was found in '{os.path.join(base, out_dir)}' for '{stk_name}'."
            )
            
        res[(die, stat)] = (full_path, names)
    return res


def load(fn, n_el):
    d = np.loadtxt(fn, comments="%", ndmin=2)
    if d.shape[1] == n_el + 1:
        t, T = d[:, 0], d[:, 1:]
    elif d.shape[1] == n_el:
        t, T = np.arange(len(d), dtype=float), d
    else:
        raise SystemExit(f"{fn}: {d.shape[1]} columns but {n_el} floorplan elements.")
    if np.nanmax(T) > 200:
        T = T - 273.15
    return t, T


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--transient", required=True)
    ap.add_argument("--warmup", type=int, required=True, help="rows to discard")
    ap.add_argument("--mean"); ap.add_argument("--peak"); ap.add_argument("--tdp")
    ap.add_argument("--stat", default="maximum", choices=["maximum", "average", "minimum"])
    ap.add_argument("--all", action="store_true", help="include FILL elements")
    a = ap.parse_args()

    tr = outputs(a.transient)
    refs = {k: outputs(getattr(a, k)) for k in ("mean", "peak", "tdp") if getattr(a, k)}
    tag = os.path.splitext(os.path.basename(a.transient))[0]
    rows, curves = [], []
    
    for (die, stat), (fn, names) in tr.items():
        if stat != a.stat:
            continue
        t, T = load(fn, len(names))
        t, T = t[a.warmup:], T[a.warmup:]
        dt = np.median(np.diff(t)) if len(t) > 1 and np.median(np.diff(t)) > 0 else 0.005
        
        ref = {}
        for k, o in refs.items():
            if (die, stat) in o:
                ref[k] = load(o[(die, stat)][0], len(names))[1][-1]
                
        keep = [i for i, n in enumerate(names) if a.all or not SKIP.match(n)]
        for i in keep:
            y = T[:, i]
            r = dict(die=die, element=names[i], Tmin=y.min(), Tmax=y.max(), swing=np.ptp(y),
                     dTdt=np.abs(np.diff(y)).max() / dt if len(y) > 1 else np.nan)
            if "mean" in ref:
                r["above_mean_pct"] = 100 * (y > ref["mean"][i]).mean()
                r["above_mean_by"] = (y - ref["mean"][i]).max()
                r["T_mean_static"] = ref["mean"][i]
            if "peak" in ref:
                r["T_peak_static"] = ref["peak"][i]; r["peak_gap"] = ref["peak"][i] - y.max()
            if "tdp" in ref:
                r["T_tdp_static"] = ref["tdp"][i]; r["tdp_gap"] = ref["tdp"][i] - y.max()
            rows.append(r)
        if not keep:
            continue
        j = max(keep, key=lambda i: T[:, i].max())
        curves.append((die, names[j], t - t[0], T[:, j], {k: v[j] for k, v in ref.items()}))

    # ---- print + csv
    cols = ["die", "element", "Tmin", "Tmax", "swing", "dTdt", "above_mean_pct", "above_mean_by",
            "peak_gap", "tdp_gap"]
    cols = [c for c in cols if any(c in r for r in rows)]
    head = {"Tmin": "Tmin C", "Tmax": "Tmax C", "swing": "swing K", "dTdt": "dT/dt K/s",
            "above_mean_pct": ">mean %", "above_mean_by": "by K", "peak_gap": "peak gap K",
            "tdp_gap": "tdp gap K"}
    print(f"{'die':<11}{'element':<13}" + "".join(f"{head[c]:>11}" for c in cols[2:]))
    for r in rows:
        print(f"{r['die']:<11}{r['element']:<13}" +
              "".join(f"{r.get(c, np.nan):11.2f}" for c in cols[2:]))
    import csv
    with open(f"metrics_{tag}.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=sorted({k for r in rows for k in r}, key=str))
        w.writeheader(); w.writerows(rows)
    print(f"\nwrote metrics_{tag}.csv")

    # ---- plot: hottest element per die vs static reference lines
    try:
        import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
        n = len(curves)
        fig, axs = plt.subplots(n, 1, figsize=(9, 2.2 * n), sharex=True, squeeze=False)
        style = {"peak": ("#e34948", "static, window peak power"),
                 "mean": ("#1baf7a", "static, window average power"),
                 "tdp": ("#52514e", "static, TDP")}
        for ax, (die, el, tt, y, ref) in zip(axs[:, 0], curves):
            ax.plot(tt, y, color="#2a78d6", lw=1.6, label="transient, 5 ms trace")
            for k, v in ref.items():
                ax.axhline(v, color=style[k][0], lw=1.2, ls="--", label=style[k][1])
            ax.set_ylabel("°C"); ax.set_title(f"{die}: {el} ({a.stat})", loc="left", fontsize=9)
            ax.spines[["top", "right"]].set_visible(False); ax.grid(alpha=0.3)
        axs[0, 0].legend(fontsize=7, ncol=2, frameon=False, loc="lower right")
        axs[-1, 0].set_xlabel("time in window (s)")
        fig.tight_layout(); fig.savefig(f"metrics_{tag}.png", dpi=150)
        print(f"wrote metrics_{tag}.png")
    except Exception as ex:
        print("(plot skipped:", ex, ")")


if __name__ == "__main__":
    main()
