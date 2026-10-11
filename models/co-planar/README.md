# Co-planar bridge

The xPU and a Mono3D memory/NMP column share a top copper base and liquid plate. `water/` is the 300 K anchor. `warm-loop/` contains the named plate-property endpoints at 308 K; these stacks reference the non-memW floorplan filenames from the original redo folder.

Static source power is approximately 405.27 W. The cold plate derives from the H200 anchor; the memory/logic organization derives from Stratum. Read the exact plate coefficient from each file, including the rounded `cp-h300` and `cp-h234` values.

## Cases

| Stack | First-sample power (W) | Floorplans |
|---|---:|---|
| [warm-loop/cp-h234.stk](warm-loop/cp-h234.stk) | 405.27 | [die_top_bridge.flp](warm-loop/die_top_bridge.flp), [die_bot_bridge.flp](warm-loop/die_bot_bridge.flp), [pic_plane_bridge.flp](warm-loop/pic_plane_bridge.flp) |
| [warm-loop/cp-h300.stk](warm-loop/cp-h300.stk) | 405.27 | [die_top_bridge.flp](warm-loop/die_top_bridge.flp), [die_bot_bridge.flp](warm-loop/die_bot_bridge.flp), [pic_plane_bridge.flp](warm-loop/pic_plane_bridge.flp) |
| [water/static-standard.stk](water/static-standard.stk) | 405.27 | [die_top_bridge_memW.flp](water/die_top_bridge_memW.flp), [die_bot_bridge_memW.flp](water/die_bot_bridge_memW.flp), [pic_plane_bridge_memW.flp](water/pic_plane_bridge_memW.flp) |

## Run

From the repository root:

```bash
python3 tools/run_case.py models/co-planar/warm-loop/cp-h234.stk
```

[Calibration assumptions](../../docs/calibration.md) · [Validation checkpoint map](../../validation/README.md) · [Every input and reference](../../docs/case-index.md) · [Provenance](../../provenance/files.json)
