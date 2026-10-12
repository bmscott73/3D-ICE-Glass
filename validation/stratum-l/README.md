# Stratum-L cold plate

300 W GPU plus six 40 W logic and six 102 W memory blocks: 1152 W over 46.6 x 34.5 mm. Top h=2.78e-8 at 300 K, insulated bottom, 125 um cells. Compare the hottest logic or memory die with the 86 C PINN reference. The original transient and nonuniform inputs are unchanged in provenance/. The uniform engine truncates 46600/125 to 372 x-cells; the exact supplied grid is retained.

```bash
python3 tools/reproduce.py --case stratum-l
```

Expected **80.97 C**, numerical tolerance **+/- 0.10 K**, at the **die peak** plane. The reference is **86.00 C**; this is a architecture cross-validation. The numerical tolerance checks model reproducibility, not agreement with experiment.

[Input](inputs/stratum_L_steady_125.stk) · [Reference and assumptions](reference.json) · [Expected metric](expected.json) · [Academic source](../../docs/references.md#pic)
