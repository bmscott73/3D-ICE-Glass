# Co Planar models

Shared liquid plate over the co-planar compute/memory bridge and glass optical plane.

| Stack | Purpose / condition |
|---|---|
| [cp-h234.stk](warm-loop/cp-h234.stk) | warm-loop |
| [cp-h300.stk](warm-loop/cp-h300.stk) | warm-loop |
| [static-standard.stk](water/static-standard.stk) | water |

```bash
python3 tools/generate.py co-planar --output runs/my-co-planar
python3 tools/run_case.py models/co-planar/warm-loop/cp-h234.stk
```

[Native input/academic index](../../docs/case-index.md) · [Calibration](../../docs/calibration.md) · [Builders](../../docs/builders.md).
