# Dual-side hybrid cooling

The xPU remains top-liquid-cooled. `water/d2-noplate` omits a far-side sink; `water/d2-standard` adds the secondary liquid plate. `air/` retains the named 3/4 m/s archived runs. `warm-loop/` contains the paper-envelope 4 m/s cases with both environmental references at 308 K.

The archived `air/d2air-3ms` and `air/d2air-4ms` use a 300 K reference and the older 0.76 plate multiplier. They are preserved as requested, but must not be mistaken for the final 0.735/0.575 warm-loop cases. Air coefficients describe the complete catalogued sink-to-air resistance normalized over package area.

## Cases

| Stack | First-sample power (W) | Floorplans |
|---|---:|---|
| [air/d2air-3ms.stk](air/d2air-3ms.stk) | 405.27 | [die_xpu_dual.flp](air/die_xpu_dual.flp), [pic_plane_dual.flp](air/pic_plane_dual.flp), [die_logic_dual.flp](air/die_logic_dual.flp), [die_mem_dual.flp](air/die_mem_dual.flp) |
| [air/d2air-4ms.stk](air/d2air-4ms.stk) | 405.27 | [die_xpu_dual.flp](air/die_xpu_dual.flp), [pic_plane_dual.flp](air/pic_plane_dual.flp), [die_logic_dual.flp](air/die_logic_dual.flp), [die_mem_dual.flp](air/die_mem_dual.flp) |
| [warm-loop/d2air-4ms-575.stk](warm-loop/d2air-4ms-575.stk) | 405.27 | [die_xpu_dual.flp](warm-loop/die_xpu_dual.flp), [pic_plane_dual.flp](warm-loop/pic_plane_dual.flp), [die_logic_dual.flp](warm-loop/die_logic_dual.flp), [die_mem_dual.flp](warm-loop/die_mem_dual.flp) |
| [warm-loop/d2air-4ms-735-new.stk](warm-loop/d2air-4ms-735-new.stk) | 405.27 | [die_xpu_dual.flp](warm-loop/die_xpu_dual.flp), [pic_plane_dual.flp](warm-loop/pic_plane_dual.flp), [die_logic_dual.flp](warm-loop/die_logic_dual.flp), [die_mem_dual.flp](warm-loop/die_mem_dual.flp) |
| [water/d2-noplate.stk](water/d2-noplate.stk) | 405.27 | [die_xpu_dual.flp](water/die_xpu_dual.flp), [pic_plane_dual.flp](water/pic_plane_dual.flp), [die_logic_dual.flp](water/die_logic_dual.flp), [die_mem_dual.flp](water/die_mem_dual.flp) |
| [water/d2-standard.stk](water/d2-standard.stk) | 405.27 | [die_xpu_dual.flp](water/die_xpu_dual.flp), [pic_plane_dual.flp](water/pic_plane_dual.flp), [die_logic_dual.flp](water/die_logic_dual.flp), [die_mem_dual.flp](water/die_mem_dual.flp) |

## Run

From the repository root:

```bash
python3 tools/run_case.py models/dual-side/air/d2air-3ms.stk
```

[Calibration assumptions](../../docs/calibration.md) · [Validation checkpoint map](../../validation/README.md) · [Every input and reference](../../docs/case-index.md) · [Provenance](../../provenance/files.json)
