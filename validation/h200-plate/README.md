# H200-scale plate boundary

700 W; 38 C inlet; frozen 40,800 W/m2K boundary over 1259.28 mm2. Contact-plane map, not source/junction. Active inlet is 311.15 K. This is an exact 11.15 K reference shift of the archived constant-property model, with no HTC refit. A 65 C upper limit is not a measured temperature.

```bash
python3 tools/reproduce.py --case h200-plate
```

Expected **61.73 C**, numerical tolerance **+/- 0.10 K**, at the **max plate contact** plane. The reference is **65.00 C**; this is a specification consistency. The numerical tolerance checks model reproducibility, not agreement with experiment.

[Input](inputs/h200_stratum_htc_probe.stk) · [Reference and assumptions](reference.json) · [Expected metric](expected.json) · [Academic source](../../docs/references.md#plate)
