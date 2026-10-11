#!/usr/bin/env python3
"""
extract_R.py -- H100-scale two-phase TTV benchmark post-processing.

Reports:
  R_case-sat    = (T_case,surface - T_sat)/Q   <- the calibrated boundary
  R_TCproxy-sat = (T_TCproxy      - T_sat)/Q   <- transparency only, NOT an
                  independent check (the experiment derives T_case from T_TC by
                  the same 1-D conduction, so this identity holds by construction)
  R_Cu          = difference, compared to the CELL-CENTRE analytic value

Corrections applied (not merely documented):
  * probe cell centre sits 5 um below the case surface -> surface correction
  * the compared span is source-centre to surface = 1.9975 mm, NOT the
    nominal 2.000 mm (probe-centre to source-centre would be 1.9925 mm)

Held-out validation:
  With a FIXED h, this model's R_case-sat is exactly 1/(hA) at EVERY power --
  constant by construction. The validation number is therefore how far the
  MEASURED R departs from that constant over held-out points. Supply digitized
  Fig. 4 data as a CSV of "power_W,R_K_per_W" and this computes held-out MAE
  and max error over 300-900 W, EXCLUDING the 700 W calibration point.

Usage: python3 extract_R.py [outputs_dir] [digitized_fig4.csv]
"""
import os, sys
import numpy as np

K = 273.15
T_SAT = 47.5                 # INFERRED from the 700 W pair; 700 W closure only
A = 0.026 * 0.035            # 910 mm^2 -- the exact A_applied for h_eff
K_CU = 400.0
H_EFF = 1.0 / (0.025 * A)
G = H_EFF * A
T_PROBE_HALF = 5e-6          # probe centre below surface
# After correcting the probe to the SURFACE, the span between T_TCproxy and
# T_case,surface is source-centre-to-surface = 1.9975 mm (NOT the nominal 2.000,
# and NOT the 1.9925 probe-centre-to-source-centre spacing).
L_SRC_TO_SURF = 1.9975e-3
R_CU_CC = L_SRC_TO_SURF / (K_CU * A)
CAL_POWER = 700

d = sys.argv[1] if len(sys.argv) > 1 else "outputs"
csv = sys.argv[2] if len(sys.argv) > 2 else None

def scalar(p):
    for line in open(p):
        if line.startswith('%'):
            continue
        q = line.split()
        if len(q) >= 2:
            return float(q[1])
    raise ValueError(p)

def case_probe(power):
    ctr = os.path.join(d, f"ttv_{power}W_case_ctr.txt")
    if os.path.exists(ctr):
        return scalar(ctr), "T() point probe"
    tm = os.path.join(d, f"ttv_{power}W_case_tmap.txt")
    if os.path.exists(tm):
        T = np.loadtxt(tm, comments='%')
        return float(T.mean()), f"Tmap mean (spatial spread {T.max()-T.min():.4f} K)"
    return None, None

print(f"h_eff = {H_EFF:,.1f} W/m2K over A_applied = {A*1e6:.0f} mm2   "
      f"G = hA = {G:.3f} W/K   1/G = {1/G:.5f} K/W")
print(f"analytic R_Cu (source-centre to surface, {L_SRC_TO_SURF*1e3:.4f} mm) = {R_CU_CC:.6f} K/W\n")

hdr = (f"{'Q [W]':>6} {'T_case':>8} {'T_TCpx':>8} {'R_case-sat':>11} "
       f"{'R_TCpx-sat':>11} {'R_Cu':>9} {'chk':>6}")
print(hdr)
print("-" * len(hdr))
for power in (500, 665, 700, 900, 1350):
    sp = os.path.join(d, f"ttv_{power}W_tcproxy_avg.txt")
    if not os.path.exists(sp):
        continue
    t_tc = scalar(sp) - K
    t_pr, how = case_probe(power)
    if t_pr is None:
        continue
    t_case = (t_pr - K) - power * T_PROBE_HALF / (K_CU * A)     # -> surface
    r_cs = (t_case - T_SAT) / power
    r_tc = (t_tc - T_SAT) / power
    r_cu = r_tc - r_cs
    ok = "OK" if abs(r_cu - R_CU_CC) < 3e-5 else "CHECK"
    tag = " (parasitic 5% sens.)" if power == 665 else ""
    print(f"{power:6d} {t_case:8.3f} {t_tc:8.3f} {r_cs:11.5f} "
          f"{r_tc:11.5f} {r_cu:9.6f} {ok:>6}{tag}")
    if power == CAL_POWER:
        print(f"{'':6} {'measured:':>8} {65.0:8.2f} {'':8} {0.025:11.5f}"
              f"   <- closure target (T_sat inferred)")
        print(f"{'':6} {'delta:':>8} {t_case-65.0:+8.3f} K {'':5} {r_cs-0.025:+11.5f}")
    if how and how != "T() point probe":
        print(f"{'':6} (case from {how})")

if csv and os.path.exists(csv):
    data = np.loadtxt(csv, delimiter=',', comments='#')
    p, r = data[:, 0], data[:, 1]
    m = (p >= 300) & (p <= 900) & (p != CAL_POWER)
    if m.any():
        pred = 1.0 / G
        err = np.abs(r[m] - pred)
        print(f"\nHELD-OUT VALIDATION (digitized Fig. 4, 300-900 W, "
              f"{CAL_POWER} W excluded, n={m.sum()}):")
        print(f"  model R_case-sat (constant) = {pred:.5f} K/W")
        print(f"  MAE  = {err.mean():.5f} K/W   ({err.mean()*700:.2f} K at 700 W)")
        print(f"  max  = {err.max():.5f} K/W   ({err.max()*700:.2f} K at 700 W)")
        print("  ^ THIS is the validation-table metric for this row.")
    lim = (p > 900)
    if lim.any():
        print(f"\nAPPLICABILITY LIMIT (>900 W): measured R rises to "
              f"{r[lim].max():.4f} K/W vs model {1/G:.5f}. The constant-h")
        print("  approximation degrades as two-phase resistance increases; the")
        print("  experiment reports NO dryout in this range.")
else:
    print("\nNo digitized Fig. 4 supplied -- held-out MAE not computed.")
    print("  Digitize per-GPU R vs power to 'fig4.csv' (power_W,R_K_per_W) and rerun.")
    print("  Only the 700 W point (65 C, 0.025 K/W) is stated numerically in the text.")

print("\nScope reminders:")
print(" * R_TCproxy-sat is NOT independent: the experiment derives T_case from")
print("   T_TC by the same 1-D conduction, so the identity holds by construction.")
print(" * T_sat = 47.5 C is inferred from the 700 W pair. Do NOT use absolute")
print("   temperatures at other powers; local saturation varies with power.")
print(" * Non-uniform-heating case (R -> 0.028 K/W, 9% flow imbalance) is a")
print("   hydraulic-imbalance sensitivity, not held-out validation: a single-TTV")
print("   conduction model has no inter-branch hydraulics.")
