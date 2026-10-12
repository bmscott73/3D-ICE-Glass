# Cu-pillar pin-fin vehicle

Corrected 1 mm active-region model and 111 um pitch variant. Use the die/source-plane maximum; RDL map is a separate observation plane. See active stack for flow and material assumptions.

```bash
python3 tools/reproduce.py --case cu-pillar
```

Expected **77.63 C**, numerical tolerance **+/- 0.10 K**, at the **die peak** plane. The reference is **78.60 C**; this is a experimental comparison. The numerical tolerance checks model reproducibility, not agreement with experiment.

[Input](inputs/estc_cupillar_pinfin_active1mm_p111.stk) · [Reference and assumptions](reference.json) · [Expected metric](expected.json) · [Academic source](../../docs/references.md#glass-cooling)
