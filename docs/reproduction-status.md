# Release verification and paper/input differences

This page records the evidence available for the release. A copied input, an archived research result, a successful solver run, and an exact reproduction of a manuscript number are separate claims.

## Import and integrity

- All **91 original research files** from the local `Baselines` subtree were copied, including nested outputs and scripts. Unrelated local validation-repository folders were excluded.
- All named architecture inputs were imported from Russell. Additional files were included where required by a stack or the supplied generators.
- The four interlayer floorplans named under `interlayer/runs` were absent there and were located in `interlayer/`. Their actual locations are recorded, rather than inventing the requested paths.
- `demo_figure.py` was found in `~/DTM2/`, rather than `~/DTM2/row/`. The compatible `~/DTM2/tflp_metrics.py` is required by it. The older row helper is retained separately on the demo branch.
- `provenance/files.json` records original paths, sizes, roles, and SHA-256 hashes. `provenance/upstream.json` pins all **282 files** in the unmodified EPFL snapshot. The runner edits only staged copies to relocate input/output paths and optionally change thread count.
- `python3 tools/check_inputs.py` verifies byte integrity, floorplan resolution, unique block names, and transient queue lengths. This is a structural/input check, not a thermal validation.

## Exact reproduction limitations

| Item | Observed input | Implication |
|---|---|---|
| Grid statement | The manuscript says 100 µm throughout; panel inputs use 200 × 200 µm, the H100 TTV uses 250 × 250 µm, and the silicon channel needs 75 × 100 µm | Preserve the released numeric grid and identify any future refinement separately |
| H100 TTV | The supplied baseline is 700 W with a 320.65 K inferred saturation reference; the manuscript discusses a held-out 720 W checkpoint | The baseline closure cannot be called an exact reproduction of the 720 W result |
| H200 | Archived at 300 K; vendor inlet is 38 °C; contact-plane and source-plane outputs differ | Compare the proper plane and apply the explicit 11.15 K steady reference offset |
| Stratum-L | Exact six-memory-stack checkpoint not located in the searched server inputs | Stratum-S and H100 TTV are not substitutes |
| Experimental glass microchannels | Exact 248 W/cm² glass test-vehicle input not located | Package-scale HyFlexPIM / CFD anchor is a different validation |
| Silicon interlayer | Calibrated-lid baseline plus 19–22 mL/min sweep recovered | The exact Table II flow variant is not assigned merely by matching its target peak |
| Panel totals | Active sums 942.03 / 1119.63 / 1361.01 W; older headers claim totals 6.1 W higher | Active floorplans match the manuscript's rounded totals; header arithmetic is historical |
| Inlet rounding | Files use 308 K, equal to 34.85 °C | The manuscript's “35 °C” label is rounded; use exact kelvin references for sub-kelvin comparisons |
| Old air cases | `dual-side/air` uses 300 K and a 0.76 plate multiplier | The bounded 308 K 0.735/0.575 inputs are the appropriate final-envelope cases |
| Comments in generated stacks | Lower copied headers retain water parameters inside warm-loop files | Active boundary blocks, not inherited comments, define the solve |
| Aggregate accuracy | Manuscript reports 2.6% over eight scalar checkpoints | This release does not independently recalculate that aggregate while exact checkpoint inputs are missing |
| Publication metadata | Supplied manuscript omits authors for blind review; no public DOI supplied | The project is attributed by title; acceptance, authors, and DOI are not invented |

## Runtime verification

Local checks completed on October 11, 2026:

- **Integrity/dependencies:** all 195 main imported assets and all 282 pinned engine files verified; every released stack resolves its floorplans and has consistent power queues.
- **Runner relocation:** all 49 main cases staged successfully without changing numeric statements, material geometry, or power queues. Four additional demo cases were also staged on the extension branch.
- **Reference demo analysis:** all 19 non-fill block metrics regenerated from the archived Tflp traces with **zero numeric difference** from the original metrics CSV. Generated PNGs were visually inspected. The release plotting copy fixes descriptive labels and reload-span endpoints; original scripts/results are retained.
- **Markdown/source checks:** local documentation links resolve; newly authored shell/Python files pass syntax checks. Imported and vendored whitespace is intentionally preserved.

- **Clean engine build:** Ubuntu 24.04 ARM64 in Docker Desktop, GCC 13, OpenBLAS 0.3.26, and bundled SuperLU MT 4.0.0. Emulator, server, and client executables built from the pinned, unmodified source. The release workflows use the emulator.
- **H100 TTV solve:** 2 solver threads; case-plane temperature **338.160 K / 65.010 °C**, heater maximum **341.996 K / 68.846 °C**; emulator time **0.250 s**, peak memory **151.86 MB**. Both declared Tflp outputs passed numeric checks.
- **Cu-pillar solve:** `estc_cupillar_pinfin_active1mm_p111.stk`, 2 threads; heater maximum **350.782 K / 77.632 °C**; emulator time **0.011 s**, peak memory **15.65 MB**. Both declared Tflp outputs passed numeric checks. These are runtime observations for the released inputs, not newly claimed experimental validation errors.

Archived result files retain their original provenance and are not relabeled as newly generated results. A complete fresh 6000-slot panel solve and the manuscript's eight-checkpoint aggregate were not rerun for this release.
