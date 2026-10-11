# Cost-aware interlayer cooling

The bridge stack is augmented by a velocity-matched 4RM cavity and an embedded capacity tier. `E0/E1/E2/E4` vary the number of added Mono3D stacks. `H1/H1M2` place HyFlexPIM alone or with memory. `warm-loop/` carries the requested four-stack property endpoints.

The standard cavity has 197 channels, 237.2 mL/min, a 300 K inlet, and frozen h=1.27e-8 W/µm²K. Both glycol-property cavity endpoints use 0.735 of that h and volumetric heat capacity 3.95e-12. The original water runs folder lacked its floorplans; they were imported from the parent interlayer folder. E1/E2/E4 dependencies are included.

## Cases

| Stack | First-sample power (W) | Floorplans |
|---|---:|---|
| [warm-loop/emb-E4-575.stk](warm-loop/emb-E4-575.stk) | 983.95 | [die_top_bridge.flp](warm-loop/die_top_bridge.flp), [die_bot_bridge.flp](warm-loop/die_bot_bridge.flp), [die_emb_E4.flp](warm-loop/die_emb_E4.flp), [pic_plane_bridge.flp](warm-loop/pic_plane_bridge.flp) |
| [warm-loop/emb-E4-735.stk](warm-loop/emb-E4-735.stk) | 983.95 | [die_top_bridge.flp](warm-loop/die_top_bridge.flp), [die_bot_bridge.flp](warm-loop/die_bot_bridge.flp), [die_emb_E4.flp](warm-loop/die_emb_E4.flp), [pic_plane_bridge.flp](warm-loop/pic_plane_bridge.flp) |
| [water/emb-E0-std.stk](water/emb-E0-std.stk) | 405.27 | [die_top_bridge.flp](water/die_top_bridge.flp), [die_bot_bridge.flp](water/die_bot_bridge.flp), [die_emb_E0.flp](water/die_emb_E0.flp), [pic_plane_bridge.flp](water/pic_plane_bridge.flp) |
| [water/emb-E1-std.stk](water/emb-E1-std.stk) | 549.94 | [die_top_bridge.flp](water/die_top_bridge.flp), [die_bot_bridge.flp](water/die_bot_bridge.flp), [die_emb_E1.flp](water/die_emb_E1.flp), [pic_plane_bridge.flp](water/pic_plane_bridge.flp) |
| [water/emb-E2-std.stk](water/emb-E2-std.stk) | 694.61 | [die_top_bridge.flp](water/die_top_bridge.flp), [die_bot_bridge.flp](water/die_bot_bridge.flp), [die_emb_E2.flp](water/die_emb_E2.flp), [pic_plane_bridge.flp](water/pic_plane_bridge.flp) |
| [water/emb-E4-std.stk](water/emb-E4-std.stk) | 983.95 | [die_top_bridge.flp](water/die_top_bridge.flp), [die_bot_bridge.flp](water/die_bot_bridge.flp), [die_emb_E4.flp](water/die_emb_E4.flp), [pic_plane_bridge.flp](water/pic_plane_bridge.flp) |
| [water/emb-H1-std.stk](water/emb-H1-std.stk) | 545.97 | [die_top_bridge.flp](water/die_top_bridge.flp), [die_bot_bridge.flp](water/die_bot_bridge.flp), [die_emb_H1.flp](water/die_emb_H1.flp), [pic_plane_bridge.flp](water/pic_plane_bridge.flp) |
| [water/emb-H1M2-std.stk](water/emb-H1M2-std.stk) | 835.31 | [die_top_bridge.flp](water/die_top_bridge.flp), [die_bot_bridge.flp](water/die_bot_bridge.flp), [die_emb_H1M2.flp](water/die_emb_H1M2.flp), [pic_plane_bridge.flp](water/pic_plane_bridge.flp) |

## Run

From the repository root:

```bash
python3 tools/run_case.py models/interlayer/warm-loop/emb-E4-575.stk
```

[Calibration assumptions](../../docs/calibration.md) · [Validation checkpoint map](../../validation/README.md) · [Every input and reference](../../docs/case-index.md) · [Provenance](../../provenance/files.json)
