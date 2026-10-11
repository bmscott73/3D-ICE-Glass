# Transient thermal extension and five-minute demo

This branch extends the static release with the supplied panel workload, analysis scripts, archived results, and a short live solver workload. It uses the same **stock EPFL emulator** as `main`; client/server DTM experiments are outside this demo.

## Start here

From the repository root, with the analysis dependencies installed:

```bash
git switch codex/transient-demo
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements-analysis.txt
python3 demo/run_demo.py reference
```

`reference` regenerates the metrics CSV/PNG and full/zoom demo figures from the **saved block-temperature traces** in `reference/outputs/`. It compares all 19 non-fill block metrics against the original CSV. It needs no compiled solver. Results appear in `runs/demo-reference/`. This mode establishes analysis reproducibility; it does not claim a fresh thermal solve.

![Regenerated transient presentation view with clarified power and tracking labels](figures/transient-full.png)

## Five-minute presentation

| Time | Action | Point to explain |
|---|---|---|
| 0:00–0:45 | Show the [panel architecture](../models/panel/README.md) and [cooling assumptions](../docs/calibration.md) | One prefill node, two decode nodes, buried PICs, a glass waveguide plane, and a frozen plate boundary |
| 0:45–1:30 | Run `python3 demo/run_demo.py reference` | Read one measured simulation trace and regenerate its figures and metrics |
| 1:30–3:00 | Open the generated `demo_*_full.png` / `demo_*_zoom.png` | The same activity drives distinct temperature histories at the embedded PIC and glass-plane coupler |
| 3:00–4:15 | Show PIC_A and CPL_A rows in the regenerated metrics CSV | Compare transient swing/slew with static window-mean and window-peak predictions |
| 4:15–5:00 | Show the [input map](inputs/pan-tdp-735.map.json), or the short live run prepared below | The workload mapping, initial state, and time step are explicit and editable |

Prebuild the solver before presenting. A five-minute walkthrough is a presentation plan, not a guarantee that a clean install and complete 6000-slot solve finish within five minutes.

## Short live transient simulation

```bash
bash tools/build.sh                         # once, on Linux
python3 demo/run_demo.py smoke --cores 2
```

On macOS or Windows, build the Docker image from this branch, then run:

```bash
docker build -t 3d-ice-glass-demo .
mkdir -p runs
docker run --rm --entrypoint python3 \
  --mount "type=bind,src=$(pwd)/runs,dst=/opt/3d-ice-glass/runs" \
  3d-ice-glass-demo demo/run_demo.py smoke --cores 2
```

Replace `smoke --cores 2` with `reference` to regenerate the archived analysis in the container. The image includes its analysis dependencies. The measured smoke runtime and test machine are recorded in [release verification](../docs/reproduction-status.md).

This generates a **40-slot, 0.2 s** synthetic two-level workload from the supplied floorplans. It retains the package footprint, layers, plate coefficient, and **5 ms** step, and uses a **coarse 898 × 400 µm demo grid** (100 × 61 cells per layer) for a quick live run. The original research inputs remain at **200 × 200 µm**. It starts at the archived 308 K initial state, applies the first power level, a 20-slot high-power phase, then returns. The wrapper checks the number of solved slots and finite temperatures and creates `smoke.png`, `smoke-check.json`, and an explicit list of staged changes in `runs/demo-smoke/`.

The smoke workload demonstrates solver execution. Its coarse cells do not resolve small photonic features, and its duration is too short to establish warm-up, serving performance, final thermal feasibility, or agreement with the archived ten-second scientific result.

The release check completed this workload in **5.7 wall seconds** with **2 solver threads**, on an Ubuntu 24.04 ARM64 Docker VM with 16 GB allocated memory. This is an observed runtime after building, and varies by machine. The [saved check](figures/smoke-check.json) and plot below come from that fresh synthetic run.

![Fresh short synthetic transient run on the explicitly coarse demo grid](figures/smoke.png)

On a workstation with sufficient memory, `python3 demo/run_demo.py smoke --research-grid --run-dir runs/demo-smoke-fine --cores 12` keeps the original 200 µm grid for the same short synthetic workload. The build's increased SuperLU storage allocation is required; see [installation](../README.md#installation). The [two-thread release check](figures/smoke-fine-check.json) passed in **268.6 wall seconds**, with **11.50 GB** reported emulator peak memory. This grid check still is not the archived workload-window reproduction.

## Complete new solve

```bash
python3 demo/run_demo.py simulate --cores 12
```

This runs the transient stack and all three static comparisons in new directories, then regenerates the figures and compares metrics with the archive. It can take substantially longer than the presentation, depending on CPU, memory, and BLAS. Set `--emulator /absolute/path/to/3D-ICE-Emulator` to use a different installed stock build and `--run-dir runs/unique-demo-name` for another execution. Reusing an existing directory is refused.

## Included inputs and their meanings

| Input | Meaning |
|---|---|
| [Transient stack](inputs/pan-tdp-735_1000-1010s_5ms.stk) and four `*_1000-1010s_5ms.flp` files | 6000 power entries per block; 20 s warm-up plus 10 s selected workload |
| [Slots CSV](inputs/slots_1000-1010s_5ms.csv) | Workload timestamps 980.000–1009.995 s; `warmup=1` for the first 4000 slots; selected interval 1000–1010 s |
| [Mean-power stack](inputs/pan-tdp-735_mean_1000-1010s_5ms.stk) and four mean floorplans | Steady simulation at the selected window's block-wise mean power |
| [Peak-power stack](inputs/pan-tdp-735_peak_1000-1010s_5ms.stk) and four peak floorplans | Steady simulation at the selected window's block-wise peak power |
| [TDP stack](inputs/pan-tdp-735.stk) and four static floorplans | Configuration-TDP comparison, distinct from the window peak |
| [Power-mapping JSON](inputs/pan-tdp-735.map.json) | DRAM channel split among tiles, logic from `compute`, decode PICs from `io*0.5`, prefill blocks constant |

The solver's time axis begins at zero. The slots CSV retains the source workload clock; the figures subtract 1000 s and display the **10 s observation window**, after discarding the **4000 warm-up rows**. No 1000-second thermal simulation is implied.

The plate coefficient is **2.999e-8 W/µm²K**, its reference is **308 K**, and the initial state is **308 K**. No embedded coolant cavity is present in this panel case. The unchanged source inputs and original analysis helper are recorded in [demo-files.json](../provenance/demo-files.json).

The original archived figure's “Decode-node power” axis plots the CSV channel sum `dram+compute+io` (**6.12–386.79 W**, mean **157.21 W**). The released mapping puts `io*0.5` in each of the two decode PICs. Consequently this channel-sum curve is **not the sum of watts in a physical decode node**, and the dynamic PIC power is **not fixed at 3.05 W** as it is in the static paper maps. Sum the actual floorplan queues for the injected package power. This window is an extension experiment, not the manuscript's approximately 398 W/decode steady operating point.

## Interpreting the saved result

For **PIC_A**, the archive reports a **24.856 K** swing and a **984.2 K/s** maximum finite-difference slew. For **CPL_A**, the corresponding values are **11.647 K** and **38.0 K/s**. The PIC_A transient maximum is **67.365 °C**, while its window-mean steady prediction is **51.982 °C** and its window-peak steady prediction is **72.464 °C**. These compare temperature histories under explicit model assumptions; they do not establish an optical tracking requirement or universal failure criterion.

The **62.5 K/s** line drawn by the plot is an illustrative, configurable tracking-rate reference, not a validated device limit. Slew values depend on the 5 ms sampling and the rounding of Tflp outputs; they are finite differences of compact-model temperatures.

## Analysis scripts and outputs

[analysis/tflp_metrics.py](analysis/tflp_metrics.py) is the compatible multi-die helper recovered from `~/DTM2/`. [analysis/demo_figure.py](analysis/demo_figure.py) imports its `outputs` and `load` functions. The release plotting copy corrects the channel-total axis label, describes the tracking-rate line as illustrative, and ends shaded reload spans at their exclusive slot edge. The unchanged server script is preserved in [reference/original-scripts/demo_figure.py](reference/original-scripts/demo_figure.py). Numeric temperature metrics are unchanged. The older helper originally specified in `row` is preserved as [tflp_metrics_row_original.py](analysis/tflp_metrics_row_original.py); its single-output interface does not satisfy that import.

`reference/` includes the requested original metrics CSV/PNG, every requested `demo_pan-tdp-735_1000-1010s_5ms_*` PDF/PNG, and block max/mean/min Tflp outputs required to rerun the analysis. Large static/final temperature maps are regenerated by a complete solve and were not needed for the reference walkthrough.

[Main README](../README.md) · [Every stack/floorplan](../docs/case-index.md) · [Release verification](../docs/reproduction-status.md) · [Academic references](../docs/references.md)
