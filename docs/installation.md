# Installation

The engine source is pinned to EPFL commit [`e0bb685`](https://github.com/esl-epfl/3d-ice/commit/e0bb6850c5e446363e26936586d625270c87f224). Its bulky test matrices and Word guide are omitted; the thermal source and PDF guide are retained unchanged.

## Ubuntu / Debian

```bash
sudo apt-get update
sudo apt-get install -y build-essential bison flex libopenblas-dev csh unzip python3 python3-venv git
git clone https://github.com/bmscott73/3D-ICE-Glass.git
cd 3D-ICE-Glass
python3 tools/check_inputs.py
bash tools/build.sh
python3 tools/reproduce.py --case glass-microchannel h100-ttv
```

The executable is `build/3d-ice/bin/3D-ICE-Emulator`. The builder copies the source into `build/`, preserving `vendor/`; logs are `build/superlu-build.log` and `build/3d-ice-build.log`. Existing build trees are refused. Inspect logs and rename a failed tree before retrying.

The build uses GCC/OpenMP, OpenBLAS and bundled SuperLU MT 4.0.0. SuperLU U-factor storage defaults to **100 times the original matrix nonzero count**, sufficient for the checked 200 µm panel. Larger models may need `SUPERLU_U_FILL=500 bash tools/build.sh` and more memory. The multiplier affects allocation capacity, not thermal equations. The original bundled default 50 was too small for the panel; Russell's research build uses 500.

For plotting and the transient extension:

```bash
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements-analysis.txt
python3 transient/run_demo.py reference
```

Native input construction, calibration, geometry checks and validation-table printing use the Python standard library. Plotting uses NumPy/Pandas/Matplotlib. GDS extraction, Modelica, SystemC and pluggable heatsinks are optional upstream features described in the [EPFL PDF guide](../vendor/3d-ice/doc/3D-ICE-User_Guide.pdf).

## macOS / Windows: Docker

```bash
docker build -t 3d-ice-glass .
mkdir -p runs
docker run --rm \
  --mount "type=bind,src=$(pwd)/runs,dst=/opt/3d-ice-glass/runs" \
  3d-ice-glass
```

The default command reproduces the glass vehicle and held-out 720 W TTV. To run another checkpoint, append `--case stratum-l`, for example. For the full table, append `--cores 2`; no `--case` means all ten rows. For a larger allocation multiplier, build with `--build-arg SUPERLU_U_FILL=500`.

To use any other Python tool in the same image:

```bash
docker run --rm --entrypoint python3 \
  --mount "type=bind,src=$(pwd)/runs,dst=/opt/3d-ice-glass/runs" \
  3d-ice-glass transient/run_demo.py smoke --cores 2
```

The image includes analysis dependencies. Vendor/build-tool layers precede the model and documentation copy, so a documentation edit does not rebuild SuperLU. The release was tested on Ubuntu 24.04 ARM64 through Docker Desktop and Linux x86-64 on the research server. Allocate enough memory for the chosen grid: the original-grid short panel check reported **11.50 GB**, while the coarse demo used about **657 MB**. The full 100 µm Stratum-S case needs a larger workstation than the quick start.
