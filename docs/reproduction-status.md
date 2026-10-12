# Reproduction status and archive history

## Current release checks

The ten Table II model values have been regenerated and checked against their stated observation planes with **±0.10 K numerical tolerance**. The eight-scalar aggregate is **2.5982927%**, rounding to **2.6%**, using the paper's Celsius-reference convention. H200's specification limit and the photonic range comparison are excluded. [Verified result and output hashes](../validation/verified-results.json) · [Summary CSV](../validation/summary.csv).

Six cases were run with the pinned stock engine on Ubuntu 24.04 ARM64 in local Docker: H100 720 W, H200 at 38 °C, Stratum-L, experimental glass vehicle, Cu-pillar, and silicon interlayer. Four large/reference cases were freshly run on Russell's x86-64 research emulator: Stratum-S, HyFlexPIM pin-fin, anchored HyFlexPIM microchannel and photonic map. Active stack parameters and floorplan power/geometry were checked against those staged files. The research source has two nonuniform-only null guards; every verified case uses a uniform mesh. Its SuperLU U allocation multiplier is 500, versus local 100.

The paired Docker quick start passed. A library-built glass case and a three-slot transient case also solved with the stock engine; constant JSON sources were expanded across all native slots. Six independent dimensional, geometry and queue checks pass. The final image rebuild reused the compiled engine layer. All 44 active stacks pass dependency/power checks, with 127 floorplan bounds/overlap/area checks and verified hashes for 228 project assets and 211 retained upstream files.

The transient reference analysis reproduces all **19** archived metrics with **zero numeric difference**. A fresh coarse-grid synthetic 40-slot run completed in **5.7 s** (about 657 MB reported peak memory). The same synthetic run on the original 200 µm panel grid passed in **268.6 s**, with **11.50 GB** reported peak memory. A complete fresh 6000-slot transient experiment was not repeated during this reorganization.

## Reference and condition discipline

| Row / issue | Current treatment |
|---|---|
| H100 720 W | Recovered 510/720/920 W inputs; h fitted at 510 W and frozen; power-specific local saturation references. Correct the case probe's 5 µm depth offset. No silicon junction claim. |
| H200 | The active inlet and initial state are 311.15 K. This is the exact constant-property 11.15 K shift of the old 300 K model, with no coefficient refit. Compare the plate-contact map, not the source plane. |
| Stratum-L | Recovered steady 125 µm checkpoint predicts 80.969 °C; original transient and nonuniform inputs preserved unchanged in its provenance folder. The native uniform parser truncates the nonintegral x-grid extent, as in the supplied checkpoint. |
| Glass vehicle | Recovered 248 W/cm² input predicts 86.405 °C. Its effective 50,000 W/m²K HTC, interface and source-depth choices are assumptions. The physical ten-channel vehicle is represented by a 2RM finite-width approximation that rounds to nine effective channels. |
| Silicon interlayer | The table's 86.506 °C result is the original 22 mL/min/layer case. Nominal 0.3 g/s is about 18 mL/min, where the released model gives about 94.89 °C. The flow-conditioned comparison is disclosed, including the full sweep. |
| Photonic map | 40 °C is a reference field/range endpoint, not a matched scalar measurement. The named PIC peak is 41.838 °C; it is excluded from the eight-point aggregate. |
| Grid statement | The paper says 100 µm throughout, while the panel uses 200 µm, Stratum-L 125 µm, TTV 250 µm, and silicon channels need their own lateral pitch. Exact active grids are now in each generated file header. |
| Inlet labels | 308 K equals 34.85 °C; 35 °C is a rounded paper label. Use exact references for sub-kelvin checks. |
| Optical limits | The 85 °C ceiling is an architecture comparison criterion. Transient tracking-rate references are illustrative; they are not universal device limits. |

The 2.6% number is a reproducible statistic over the reported rows, including anchored and conditional comparisons. It does not make all rows independent held-out experiments. Raw conjugate-CFD wall patches and the historical 510 W experimental digitization are not bundled; Stage 1 tools accept those data for new anchors.

## Byte-identical archive and provenance

The annotated tag [archive-byte-identical-2026-10-11](https://github.com/bmscott73/3D-ICE-Glass/tree/archive-byte-identical-2026-10-11) points to original commit **f7e6b7b75e2c6daf0d48d0d5833318764866fe18**. It preserves the original static/transient inputs, all local Baselines research files, the full 282-file engine snapshot, and their original licensing. [Original import hashes](../provenance/archive-files.json) remain verifiable against that tag.

Current `main` is a usable framework rather than the import layout. It has one folder per checkpoint; source-derived figure PDFs; twelve recovered generators; a material/primitive library; calibration and reproduction tools; and transient work under `transient/`. Full-line historical comments are replaced by one active-statement header. Floorplans and outputs use relative native paths. Numeric material, geometry and power values are retained, except the explicit H200 reference-temperature shift. The pin-fin declaration was moved before dimensions to satisfy the native grammar.

Current [input hashes](../provenance/files.json) and [retained upstream hashes](../provenance/upstream.json) check the new layout. Original source hashes, locations and transformation notes are retained separately. The four interlayer floorplans requested under `interlayer/runs` were found in its parent directory; the compatible transient analysis helper came from `~/DTM2/`.

## Removed from the working tree

- Retired 300 K / 0.76 secondary-air cases and company-named warm-loop variants.
- Superseded HyFlexPIM glasswall/v4 inputs, duplicate panel `pan-std`, old logs, parse scripts, combined master dumps and raw baseline field arrays.
- The upstream **133 MB test tree** and Word user guide. Retained source and PDF guide total about **9.7 MB** and stay pinned to `e0bb685`.

Raw baseline files/maps and original recovered generator code are [release assets](https://github.com/bmscott73/3D-ICE-Glass/releases/tag/archive-byte-identical-2026-10-11). The archive tag retains the complete historical tree. Model inputs/reference data now use CC-BY-4.0; software remains GPL-3.0-or-later, and third-party dependency notices remain in force. Historical licenses are retained in the archive.

## Sparse factorization allocation

Upstream SuperLU MT defaults to `sp_ienv(7) = -50`. The original-grid panel exceeded that U storage at column 749,221 and the emulator terminated with SIGSEGV; those failed outputs were not accepted. The release builder uses **-100**, configurable from 50 to 500, and rebuilds the extracted dependency. It changes allocation capacity only; the pinned source/ZIP stay unchanged. Russell's [original tuning source](../provenance/research-build/sp_ienv.c) uses -500 and retains its [BSD license](../provenance/research-build/License.txt).

The source figures are rendered from the original PDF files, replacing crops from a manuscript page. Publication metadata not present in the paper is not fabricated; verified external references are in the bibliography.
