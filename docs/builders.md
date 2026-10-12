# Stack, floorplan and architecture builders

## Library-based construction

```bash
python3 tools/build_model.py --config examples/glass-package.json \
  --output runs/my-package
python3 tools/run_case.py runs/my-package/glass-package.stk
```

The JSON configuration specifies `name`, `chip_um`, `cell_um`, `cooling`, and an ordered `layers` list. Layer materials refer to IDs in [materials.json](../library/materials.json). Cooling refers to a primitive in [primitives.json](../library/primitives.json).

A passive layer has `id`, `material`, and `height_um`. A die has `kind: "die"`, `id`, `material`, `source_um`, optional `passive_above_um` / `passive_below_um`, and rectangular `blocks`. Each block has `name`, `position_um`, `size_um`, and `power_W` (an array). A `kind: "channel"` stack entry places the configured 4RM cavity. Channel geometry must fit the width; total flow scales with channel count to preserve the frozen anchor's velocity.

The default solver is steady. To build a transient case, add `solver: {"step_s": 0.005, "slot_s": 0.005}` and equal-length power queues. A constant one-value block may coexist with transient blocks in the JSON configuration; the builder repeats its value for every slot in the native floorplan. Material and cooling values are converted to native 3D-ICE units during serialization.

Construction rejects duplicate IDs, invalid geometry, overlaps, nonfinite/negative power, and incompatible grid/time-step choices. Its `model.json` records area and calibration-domain status. The small example is illustrative, not a new validated cooling domain.

## Area-preserving case variants

```bash
python3 tools/build_model.py \
  --from-stack models/co-planar/water/static-standard.stk \
  --plate-factor .575 --reference-k 308 --output runs/bridge-575
```

`--plate-factor` multiplies the seed's **top** Robin coefficient; it leaves a secondary air boundary alone. `--cavity-factor` separately scales prescribed cavity coefficients. `--reference-k` moves all environmental/initial temperature references together. `--power-scale` scales each block's queue without changing its rectangle. Choose a water seed when requesting a water-relative property factor. Existing output directories are refused.

The builder keeps every block area and position, verifies bounds/overlap, and records the results. The native files receive a single header generated from active statements. For a placement change, edit block coordinates in a JSON configuration or a recovered geometry generator and run its checks; preserve component areas when comparing architectures.

## Recovered architecture generators

```bash
python3 tools/generate.py all --output runs/architectures
python3 tools/generate.py matrix --output runs/cooling-matrix
python3 generators/shared/gen_endpoints.py --output runs/endpoints
```

| Folder | Recovered scripts | Purpose |
|---|---|---|
| `generators/co-planar/` | `gen_bridge_flps.py`, `build_bridge_stks.py` | Bridge layout, mirrored placement and cooling configurations |
| `generators/dual-side/` | `gen_dual.py`, `build_dual_stks.py` | Preserve component areas while placing the tiers on opposite sides |
| `generators/interlayer/` | `gen_embedded.py`, `build_embedded_stks.py` | E0/E1/E2/E4 and H1/H1M2 capacity maps, translated PIM footprint |
| `generators/panel/` | `gen_pan_flps.py`, `build_pan_stks.py`, `gen_prov.py` | Three-node row, separate workload channels and workload/TDP levels |
| `generators/shared/` | `build_matrix.py`, `gen_endpoints.py` | Catalogued 1/2/3/4 m/s sink conductance and 0.735/0.575 plate endpoints |
| `generators/photonic/` | `gen_cpo_flps.py` | 2.5D/3D package topology and PIC footprints |

The primary CLI creates a fresh workspace, supplies dependency floorplans, runs the recovered coordinate/stack code, relocates native paths, and checks generated rectangles before recording `generation.json`. Generator output headers are regenerated from active values. Panel sums are **942.03 / 1119.63 / 1361.01 W**, with a fixed 3.05 W PIC per node in the static maps. Current generators emit the property-derived 0.735/0.575 endpoints; the retired 0.76 condition is in the archive only.

[Source locations and original generator hashes](../provenance/generators.json) identify the recovered code. The originals are also preserved as a release asset. Generated exploration variants are distinct from the fixed paper checkpoints in `validation/`.

## Registering a new anchor

Use `tools/calibrate.py` with real reference data, then add a new primitive entry with its value, units, source, applied area, calibration condition and transfer domain. Keep the previous anchor ID for existing cases. A changed coolant/flow regime or wall geometry requires a new anchor; a fitted value must not be presented as a held-out prediction.
