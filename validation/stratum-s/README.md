# Stratum-S cold plate

100 um grid; explicit 2 mm copper base, 20 um TIM, hybrid bond and orthotropic Cu-TGV composite. Reference is the project matched Icepak comparison. Coolant 300 K and plate h=4.08e-8 are frozen.

```bash
python3 tools/reproduce.py --case stratum-s
```

Expected **55.47 C**, numerical tolerance **+/- 0.10 K**, at the **die peak** plane. The reference is **55.18 C**; this is a matched CFD cross-validation. The numerical tolerance checks model reproducibility, not agreement with experiment.

[Input](inputs/stratum_S_v2_liquid.stk) · [Reference and assumptions](reference.json) · [Expected metric](expected.json) · [Academic source](../../docs/references.md#stratum)
