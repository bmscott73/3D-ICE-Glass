# Dual Side models

Primary liquid plate over compute, with absent, liquid or catalogued secondary air cooling. Final warm-loop cases use the 4 m/s sink and 0.735/0.575 plate endpoints.

| Stack | Purpose / condition |
|---|---|
| [d2air-4ms-575.stk](warm-loop/d2air-4ms-575.stk) | warm-loop |
| [d2air-4ms-735.stk](warm-loop/d2air-4ms-735.stk) | warm-loop |
| [d2-noplate.stk](water/d2-noplate.stk) | water |
| [d2-standard.stk](water/d2-standard.stk) | water |

```bash
python3 tools/generate.py dual-side --output runs/my-dual-side
python3 tools/run_case.py models/dual-side/warm-loop/d2air-4ms-575.stk
```

[Native input/academic index](../../docs/case-index.md) · [Calibration](../../docs/calibration.md) · [Builders](../../docs/builders.md).
