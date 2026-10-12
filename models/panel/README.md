# Panel models

One prefill and two decode nodes. Static trace-floor, workload-mean and TDP maps total 942.03 / 1119.63 / 1361.01 W; each node has a 3.05 W PIC.

| Stack | Purpose / condition |
|---|---|
| [pan-tdp.stk](provisioning/pan-tdp.stk) | provisioning |
| [pan-wl.stk](provisioning/pan-wl.stk) | provisioning |
| [pan-std.stk](trace-floor/pan-std.stk) | trace-floor |
| [pan-tdp-575.stk](warm-loop/pan-tdp-575.stk) | warm-loop |
| [pan-tdp-735.stk](warm-loop/pan-tdp-735.stk) | warm-loop |
| [pan-wl-575.stk](warm-loop/pan-wl-575.stk) | warm-loop |

```bash
python3 tools/generate.py panel --output runs/my-panel
python3 tools/run_case.py models/panel/provisioning/pan-tdp.stk
```

[Native input/academic index](../../docs/case-index.md) · [Calibration](../../docs/calibration.md) · [Builders](../../docs/builders.md).
