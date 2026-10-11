# Panel-scale serving neighborhood

One fixed prefill node and two decode nodes occupy an 89.8 × 24.4 mm row. `trace-floor/` contains the initial architecture and generator. `provisioning/` contains workload-average and TDP maps plus `gen_prov.py`. `warm-loop/` contains the requested 0.735/0.575 TDP and conservative workload cases.

All released panel stacks use 200 × 200 µm cells. Active power sums are 942.03 W (trace floor), 1119.63 W (workload), and 1361.01 W (TDP). The old generators write additional retired 0.76 variants and contain stale total-power comments; run them in a disposable copied directory, rather than over the release inputs. Generator seed floorplans and pan-std.stk are included.

## Cases

| Stack | First-sample power (W) | Floorplans |
|---|---:|---|
| [provisioning/pan-std.stk](provisioning/pan-std.stk) | 942.03 | [pan_mem.flp](provisioning/pan_mem.flp), [pan_logic.flp](provisioning/pan_logic.flp), [pan_pic_die.flp](provisioning/pan_pic_die.flp), [pan_pic.flp](provisioning/pan_pic.flp) |
| [provisioning/pan-tdp.stk](provisioning/pan-tdp.stk) | 1361.01 | [pan_mem_tdp.flp](provisioning/pan_mem_tdp.flp), [pan_logic_tdp.flp](provisioning/pan_logic_tdp.flp), [pan_pic_die.flp](provisioning/pan_pic_die.flp), [pan_pic.flp](provisioning/pan_pic.flp) |
| [provisioning/pan-wl.stk](provisioning/pan-wl.stk) | 1119.63 | [pan_mem_wl.flp](provisioning/pan_mem_wl.flp), [pan_logic_wl.flp](provisioning/pan_logic_wl.flp), [pan_pic_die.flp](provisioning/pan_pic_die.flp), [pan_pic.flp](provisioning/pan_pic.flp) |
| [trace-floor/pan-std.stk](trace-floor/pan-std.stk) | 942.03 | [pan_mem.flp](trace-floor/pan_mem.flp), [pan_logic.flp](trace-floor/pan_logic.flp), [pan_pic_die.flp](trace-floor/pan_pic_die.flp), [pan_pic.flp](trace-floor/pan_pic.flp) |
| [warm-loop/pan-tdp-575.stk](warm-loop/pan-tdp-575.stk) | 1361.01 | [pan_mem_tdp.flp](warm-loop/pan_mem_tdp.flp), [pan_logic_tdp.flp](warm-loop/pan_logic_tdp.flp), [pan_pic_die.flp](warm-loop/pan_pic_die.flp), [pan_pic.flp](warm-loop/pan_pic.flp) |
| [warm-loop/pan-tdp-735.stk](warm-loop/pan-tdp-735.stk) | 1361.01 | [pan_mem_tdp.flp](warm-loop/pan_mem_tdp.flp), [pan_logic_tdp.flp](warm-loop/pan_logic_tdp.flp), [pan_pic_die.flp](warm-loop/pan_pic_die.flp), [pan_pic.flp](warm-loop/pan_pic.flp) |
| [warm-loop/pan-wl-575.stk](warm-loop/pan-wl-575.stk) | 1119.63 | [pan_mem_wl.flp](warm-loop/pan_mem_wl.flp), [pan_logic_wl.flp](warm-loop/pan_logic_wl.flp), [pan_pic_die.flp](warm-loop/pan_pic_die.flp), [pan_pic.flp](warm-loop/pan_pic.flp) |

## Run

From the repository root:

```bash
python3 tools/run_case.py models/panel/provisioning/pan-std.stk
```

[Calibration assumptions](../../docs/calibration.md) · [Validation checkpoint map](../../validation/README.md) · [Every input and reference](../../docs/case-index.md) · [Provenance](../../provenance/files.json)
