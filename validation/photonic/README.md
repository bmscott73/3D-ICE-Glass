# Photonic PIC map

Compare named PIC footprints in the 2.5D package. The reference 40 C is a field/colorbar bound rather than a matched measured scalar peak. Excluded from the eight-point percentage aggregate. The 3D package variant is included for a stacking trend check.

```bash
python3 tools/reproduce.py --case photonic
```

Expected **41.84 C**, numerical tolerance **+/- 0.10 K**, at the **PIC peak** plane. The reference is **40.00 C**; this is a range / topology comparison. The numerical tolerance checks model reproducibility, not agreement with experiment.

[Input](inputs/cpo_2p5d.stk) · [Reference and assumptions](reference.json) · [Expected metric](expected.json) · [Academic source](../../docs/references.md#pic)
