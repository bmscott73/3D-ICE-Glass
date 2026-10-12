# HyFlexPIM microchannel + Cu-TGV

130 channels, 156.5 mL/min, 300 K inlet, h_eff=1.27e-8. Geometry, power and flow are frozen; circular Hausen and square-duct alternatives remain as controlled coefficient comparisons. Raw CFD wall-flux patches are not bundled; tools/calibrate.py accepts them for a new anchor.

```bash
python3 tools/reproduce.py --case hyflex-microchannel
```

Expected **97.51 C**, numerical tolerance **+/- 0.10 K**, at the **die peak** plane. The reference is **98.20 C**; this is a anchored CFD comparison. The numerical tolerance checks model reproducibility, not agreement with experiment.

[Input](inputs/hfp_tgv_E1c_anchored.stk) · [Reference and assumptions](reference.json) · [Expected metric](expected.json) · [Academic source](../../docs/references.md#hyflex)
