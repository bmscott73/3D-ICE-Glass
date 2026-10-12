# Reproduce the paper

## Validation table

```bash
python3 tools/reproduce.py
```

This runs all ten Table II rows, validates finite/complete outputs and staged input equivalence, reads each physical observation plane, and prints the model/reference/difference table. Each target has a **±0.10 K numerical reproduction tolerance** in its checkpoint's `expected.json`. The full table requires enough memory for the 100 µm Stratum-S model.

```bash
python3 tools/reproduce.py --case stratum-l
python3 tools/reproduce.py --case glass-microchannel h100-ttv
python3 tools/reproduce.py --results runs/my-existing-validation
python3 tools/reproduce.py --recorded
```

`--results` checks existing result directories against the active stack/floorplan statements. `--recorded` prints the checked release result without running a solver. The release's eight scalar rows give **2.598%**, which rounds to the paper's **2.6%**. This reproduces the paper's convention using Celsius reference values. H200's upper-limit check and the PIC colorbar/range comparison are excluded. The aggregate includes both anchored comparisons and predictions; it is not eight independent held-out experiments.

[One folder per checkpoint](../validation/README.md) holds its input, reference, expected output and assumptions. [summary.csv](../validation/summary.csv) is the compact checked table; raw baseline maps are in the [archive release](https://github.com/bmscott73/3D-ICE-Glass/releases/tag/archive-byte-identical-2026-10-11). [Detailed execution and historical notes](reproduction-status.md).

## Paper figures and primitives

| Item | Command / data | Expected |
|---|---|---|
| Table I | [Primitive registry](../library/primitives.json), `python3 tools/calibrate.py --help` | Water plate 40,800 W/m²K; anchored glass 4RM 12,700 W/m²K; pin-fin geometry/velocity in its checkpoint |
| Fig. 1 | [Stage 1](calibration.md), [original PDF](figures/source/methodology.pdf) | Reference → anchor → frozen-domain exploration |
| Fig. 2 | `python3 tools/reproduce.py --case stratum-s hyflex-microchannel` | 55.47 / 97.51 °C; new 3D-ICE fields in the run output folders; Icepak fields are external reference data |
| Fig. 3 | `python3 tools/check_geometry.py`, [original PDF](figures/source/architectures.pdf) | Checked geometry for four architecture families; areas/powers from the input index |
| Fig. 4 | Commands below; [original PDF](figures/source/panel-temperature.pdf) | Memory peak 91.26 °C; package peak 91.30 °C |

## Panel temperature field

```bash
python3 tools/run_case.py models/panel/warm-loop/pan-tdp-575.stk \
  --run-dir runs/figure4 --cores 2
python3 tools/plot_map.py runs/figure4/outputs/pan-tdp-575_die_mem_tmap.txt \
  --output runs/figure4/memory-field.png --expected-c 91.26
```

This uses the active **1361.01 W**, **0.575** plate endpoint, **308 K** reference and **200 × 200 µm** grid. The reported 35 °C inlet is rounded from 308 K. The map is the memory tier; the hottest block anywhere in the package reaches about **91.30 °C**. An 85 °C architecture ceiling gives a static capacity near **1209 W**, using uniform power scaling with frozen coefficients. This is a capacity estimate, not a controller response.

## Transient extension

```bash
python3 transient/run_demo.py reference
python3 transient/run_demo.py smoke --cores 2
python3 transient/run_demo.py simulate --cores 12
```

Reference analysis regenerates the saved result and checks 19 metrics; smoke is a short synthetic live solver run; simulate re-solves the full 6000-slot experiment and static comparisons. [Five-minute guide](../transient/README.md) gives input timing, workload mapping and the distinction between these modes.
