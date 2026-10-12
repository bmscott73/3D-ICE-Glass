# Glass microchannel + Cu-TGV

16.252928 W on a 2.56 x 2.56 mm heater (248 W/cm2), 2.8 mm domain, water 25.46 mL/min at 295.15 K. 10 physical glass channels with copper TGVs. The 2RM pitch approximation rounds its effective channel count to 9; this finite-width approximation is part of the supplied case. HTC 50,000 W/m2K, 10 um interface, die source depth and effective TGV conductivity are modeling assumptions, not author-supplied or independently fitted values.

```bash
python3 tools/reproduce.py --case glass-microchannel
```

Expected **86.41 C**, numerical tolerance **+/- 0.10 K**, at the **die peak** plane. The reference is **83.30 C**; this is a experimental comparison with assumed HTC. The numerical tolerance checks model reproducibility, not agreement with experiment.

[Input](inputs/estc_microchannel_author_inputs_v2.stk) · [Reference and assumptions](reference.json) · [Expected metric](expected.json) · [Academic source](../../docs/references.md#glass-cooling)
