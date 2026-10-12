# Interlayer models

Frozen glass/Cu-TGV 4RM cavity with E0/E1/E2/E4 and H1/H1M2 embedded-capacity maps.

| Stack | Purpose / condition |
|---|---|
| [emb-E4-575.stk](warm-loop/emb-E4-575.stk) | warm-loop |
| [emb-E4-735.stk](warm-loop/emb-E4-735.stk) | warm-loop |
| [emb-E0-std.stk](water/emb-E0-std.stk) | water |
| [emb-E1-std.stk](water/emb-E1-std.stk) | water |
| [emb-E2-std.stk](water/emb-E2-std.stk) | water |
| [emb-E4-std.stk](water/emb-E4-std.stk) | water |
| [emb-H1-std.stk](water/emb-H1-std.stk) | water |
| [emb-H1M2-std.stk](water/emb-H1M2-std.stk) | water |

```bash
python3 tools/generate.py interlayer --output runs/my-interlayer
python3 tools/run_case.py models/interlayer/warm-loop/emb-E4-575.stk
```

[Native input/academic index](../../docs/case-index.md) · [Calibration](../../docs/calibration.md) · [Builders](../../docs/builders.md).
