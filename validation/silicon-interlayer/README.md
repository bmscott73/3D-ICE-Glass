# Silicon interlayer microchannels

The reported 86.51 C is the original 22 mL/min/layer input (archived output 359.656 K). Lid h=1.292e-8 is calibrated at a separate cold-plate baseline. Reference 0.3 g/s corresponds to about 18 mL/min; the selected flow is 22% higher and conditional on the flow convention/fit. The 18-22 mL/min inputs are included, and the 18 mL/min result is approximately 94.89 C. This row must not be described as a held-out test at nominal 18 mL/min.

```bash
python3 tools/reproduce.py --case silicon-interlayer
```

Expected **86.51 C**, numerical tolerance **+/- 0.10 K**, at the **bottom-die peak** plane. The reference is **84.70 C**; this is a flow-conditioned CFD comparison. The numerical tolerance checks model reproducibility, not agreement with experiment.

[Input](inputs/ibm_intra_q22.stk) · [Reference and assumptions](reference.json) · [Expected metric](expected.json) · [Academic source](../../docs/references.md#silicon-cooling)
