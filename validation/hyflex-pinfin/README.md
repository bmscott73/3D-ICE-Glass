# HyFlexPIM Cu-pillar pin-fin

140.7 W duty-weighted floorplan; 26.1 x 17.4 mm; pin-fin Darcy velocity 1e6 um/s. Pin-fin declaration precedes dimensions in native 3D-ICE grammar. Legacy absolute paths are removed. No source, geometry or boundary coefficient was fitted during reorganization.

```bash
python3 tools/reproduce.py --case hyflex-pinfin
```

Expected **52.17 C**, numerical tolerance **+/- 0.10 K**, at the **die peak** plane. The reference is **55.80 C**; this is a CFD cross-validation. The numerical tolerance checks model reproducibility, not agreement with experiment.

[Input](inputs/hfp_chiplet_pinfin.stk) · [Reference and assumptions](reference.json) · [Expected metric](expected.json) · [Academic source](../../docs/references.md#hyflex)
