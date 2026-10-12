# 3D-ICE-Glass

**Calibrated thermal design for glass packages, Cu-TGV heat paths, embedded cooling, and photonic AI architectures.**

3D-ICE-Glass follows **anchor once, freeze, then transfer within the calibrated cooling domain**. It combines glass and orthotropic TGV primitives, hybrid bonds, liquid plates, and embedded microchannels with stack/floorplan builders, power maps, and steady/transient studies. [EPFL's 3D-ICE 4.0](https://github.com/esl-epfl/3d-ice) provides the compact thermal engine; this project provides the calibration workflow and glass-package framework.

![Co-planar, dual-side, interlayer, and panel-scale glass architectures](docs/figures/architectures.png)

## Quick start: a glass result and a held-out boundary check

With Docker installed, from the repository root:

```bash
git clone https://github.com/bmscott73/3D-ICE-Glass.git
cd 3D-ICE-Glass
docker build -t 3d-ice-glass .
mkdir -p runs
docker run --rm \
  --mount "type=bind,src=$(pwd)/runs,dst=/opt/3d-ice-glass/runs" \
  3d-ice-glass
```

The default command solves the small **glass microchannel/Cu-TGV vehicle** and the **720 W copper TTV**. Expected results are **86.41 °C** at the glass vehicle's die peak and **64.83 °C** at the held-out TTV case surface, each within **±0.10 K** of the released model value. The first tests the glass cooling path; the second tests the two-phase boundary frozen after a 510 W fit. Their reference measurements are 83.3 and 64.90 °C. Generated inputs, logs, JSON and CSV appear in a new `runs/validation-*` folder.

Already built on Linux:

```bash
python3 tools/reproduce.py --case glass-microchannel h100-ttv
```

[Native installation](docs/installation.md) · [Full paper reproduction](docs/reproduce.md) · [Five-minute transient demo](transient/README.md)

## Paper results: command → expected value

Run these commands from the repository root. The [checkpoint index](validation/README.md) gives each row's inputs, reference, physical observation plane and assumptions. Tolerances below check numerical reproduction of the model; experimental differences are reported separately.

| Paper item | Command | Expected result |
|---|---|---|
| Table I: cooling primitives | `python3 tools/calibrate.py air --resistance-k-w .23 --area-mm2 1259.28 --sink-base-mm2 8700` | `G = 4.347826 W/K`, `h = 3.452629e-9 W/µm²K`; [plate/4RM library](library/primitives.json) |
| Table II: complete validation table | `python3 tools/reproduce.py` | All ten rows within ±0.10 K; eight-scalar aggregate **2.6%** |
| Table II: Stratum-L | `python3 tools/reproduce.py --case stratum-l` | **80.97 °C** die peak versus 86 °C |
| Fig. 1: anchoring workflow | `python3 tools/calibrate.py --help` | CFD wall-flux extraction, TTV fit, and sink-conductance conversion; [methodology](docs/methodology.md) |
| Fig. 2: Stratum-S / HyFlexPIM cross-validation | `python3 tools/reproduce.py --case stratum-s hyflex-microchannel` | **55.47 / 97.51 °C** die peaks |
| Fig. 3: architecture floorplans | `python3 tools/check_geometry.py` | In-bounds, non-overlapping rectangular maps; [architecture inputs](docs/case-index.md) |
| Fig. 4: panel warm-loop memory field | [Run and plot commands](docs/reproduce.md#panel-temperature-field) | **91.26 °C** memory-tier peak; **91.30 °C** package maximum |
| Transient extension | `python3 transient/run_demo.py reference` | **19** reproduced metrics; PIC_A swing **24.856 K**, CPL_A swing **11.647 K** |

For an immediate view of the **recorded release checks**, without a new solve:

```bash
python3 tools/reproduce.py --recorded
```

The full validation table needs a workstation with enough memory for Stratum-S's 100 µm grid. The two-case quick start runs in seconds after compilation. [Measured checks and input history](docs/reproduction-status.md) document hardware, numerical precision, and the flow-conditioned silicon row.

## Build your own glass stack or variant

The [materials library](library/materials.json) stores glass, copper, silicon, an orthotropic Cu-TGV composite, hybrid bond, TIM, and die-attach properties with provenance. The [primitive library](library/primitives.json) records frozen plate, two-phase, air-sink, and 4RM anchors, including the domain in which each may transfer.

```bash
# Assemble a small native stack and floorplan from a JSON configuration.
python3 tools/build_model.py --config examples/glass-package.json \
  --output runs/my-glass-package
python3 tools/run_case.py runs/my-glass-package/glass-package.stk

# Keep a paper floorplan's area and power map; change only the plate endpoint.
python3 tools/build_model.py \
  --from-stack models/co-planar/water/static-standard.stk \
  --plate-factor .575 --reference-k 308 --output runs/my-bridge-575

# Regenerate architecture layouts and stacks with their geometry checks.
python3 tools/generate.py panel --output runs/my-panel
python3 generators/shared/gen_endpoints.py --output runs/my-endpoints
```

Builders reject out-of-bounds and overlapping rectangles, check power queues, and record area-preservation results in `model.json` or `generation.json`. New directories are required, so existing inputs/results are not overwritten. [Builder and generator guide](docs/builders.md) explains configuration fields, all twelve recovered generators, and how to register a new calibrated primitive.

## Calibrate before transferring

Native 3D-ICE uses **µm, W, K, s**; volumetric heat capacity is J/µm³K. Convert `h` from W/m²K by multiplying by `1e-12`, conductivity from W/mK by `1e-6`, and volumetric capacity from J/m³K by `1e-18`.

The main water plate is **40,800 W/m²K**. The glass/Cu-TGV 4RM anchor is **12,700 W/m²K**, with **156.5 mL/min over 130 channels**. Warm-loop studies apply plate ratios **0.735 / 0.575**, while the laminar cavity uses **0.735** at both endpoints. These are property sensitivities; a new coolant, channel geometry, wall material or flow regime requires a new anchor. [Calibration equations and input formats](docs/calibration.md) cover Stage 1 and the observation-plane discipline.

## Architecture studies and transient work

| Family | Inputs | Main distinction |
|---|---|---|
| [Co-planar bridge](models/co-planar/README.md) | Water and warm-loop endpoints | Shared plate, local electrical bridge, glass optical plane |
| [Dual-side hybrid](models/dual-side/README.md) | Liquid-only, dual-liquid, final 4 m/s air endpoints | Parallel primary-liquid and secondary-sink heat paths |
| [Interlayer cooling](models/interlayer/README.md) | E0/E1/E2/E4 and H1/H1M2 | Frozen glass 4RM cavity and embedded capacity |
| [Panel neighborhood](models/panel/README.md) | Trace-floor, workload mean, TDP and warm-loop endpoints | One prefill node and two decode nodes |

![Panel memory-tier field at the 0.575 warm-loop plate endpoint](docs/figures/panel-temperature.png)

The embedded visuals are rendered from the [original figure PDFs](docs/figures/source/). [Reproduce Fig. 4](docs/reproduce.md#panel-temperature-field) to generate a new thermal field.

`transient/` is part of **main**. It includes the 1000–1010 s workload window, static mean/peak/TDP comparisons, temperature traces, and a five-minute walkthrough. Its fast live smoke case uses a clearly labeled coarse grid; the original 200 µm grid and complete 6000-slot solve remain available. [Block-temperature metrics](tools/tflp_metrics.py) are shared tools.

## Layout, references, and licenses

```text
library/       Materials and frozen cooling primitives, with provenance
validation/    One folder per paper checkpoint; inputs, reference, expected value
models/        Four architecture families and current cooling endpoints
transient/     Workload extension, reference traces, live demo and analysis
iceglass/      Stack/floorplan construction and input inspection
tools/        Build, calibration, reproduction, generation, metrics and plotting
generators/   Twelve recovered architecture-generation scripts
docs/         Installation, methodology, reproduction and source figures
vendor/3d-ice/ Pinned EPFL source and PDF guide; bulky test fixtures omitted
```

Please cite **3D-ICE-Glass: Calibrated Thermal-Aware Floorplanning of Photonic Glass Packages for Scalable AI**, the applicable validation/architecture sources, and the four underlying [3D-ICE publications](docs/references.md#underlying-thermal-engine). [References](docs/references.md) · [BibTeX](docs/references.bib).

**Code:** [GPL-3.0-or-later](LICENSE), retaining EPFL and dependency notices. **Model inputs, material/primitive data, reference data, and project figures:** [CC-BY-4.0](LICENSE-MODELS.txt), with source attribution. [NOTICE](NOTICE) defines the scope. The [byte-identical archive tag](https://github.com/bmscott73/3D-ICE-Glass/tree/archive-byte-identical-2026-10-11) preserves the original files and licensing; raw baseline maps are available in the [archive release](https://github.com/bmscott73/3D-ICE-Glass/releases/tag/archive-byte-identical-2026-10-11).
