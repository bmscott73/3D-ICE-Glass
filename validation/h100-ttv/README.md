# H100-scale copper TTV

Coefficient fitted once at 510 W (4.4186e-8 W/um2K), frozen for 720 and 920 W. Local saturation references differ by power. The probe centre is 5 um below the surface; remove its conduction offset. Copper case, not GPU junction.

```bash
python3 tools/reproduce.py --case h100-ttv
```

Expected **64.83 C**, numerical tolerance **+/- 0.10 K**, at the **case surface** plane. The reference is **64.90 C**; this is a held-out power prediction. The numerical tolerance checks model reproducibility, not agreement with experiment.

[Input](inputs/ttv_pred_720W.stk) · [Reference and assumptions](reference.json) · [Expected metric](expected.json) · [Academic source](../../docs/references.md#ttv)
