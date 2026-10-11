# Validation models

`Baselines/` contains all **91 research files** supplied in the local validation repository's `Baselines` subtree, including nested results, scripts, and logs. No local `Old`, `Photonic`, or `floorplans` contents were imported. Original baseline files are unchanged. The missing `pic-sohrab/tier2_cpu.flp` was subsequently added from the server with separate provenance.

`supplemental/` adds the server validation models and dependencies authorized for this release. [files.json](../provenance/files.json) records the source and SHA-256 of every original file. The [complete index](../docs/case-index.md) links all stacks and floorplans.

## Checkpoint map

| Supplied manuscript checkpoint | Released input | What it can establish |
|---|---|---|
| H100-scale two-phase copper TTV | [700 W baseline](Baselines/H100/ttv_interpack.stk); [power sweep](supplemental/h100-power-sweep/) | Copper case/saturation boundary and thermocouple proxy; exact 720 W manuscript variant not located |
| H200 cold-plate specification | [H200 source/contact probe](Baselines/H200/h200_stratum_htc_probe.stk) | Compare the contact plane after shifting the archived 300 K reference to 38 °C; specification consistency |
| Stratum-S / Icepak | [Stratum-S liquid](Baselines/Stratum-S/stratum_S_v2_liquid.stk) | Stack, orthotropic composite, source placement, and fixed plate input |
| Stratum-L H100-scale | Not located | Do not equate the Stratum-S or unrelated H100 TTV with this checkpoint |
| Glass µCH/Cu-TGV experimental vehicle | Not located | Package-scale HyFlexPIM is a different geometry and CFD anchor |
| Direct-contact Cu-pillar vehicle | [Corrected 1 mm active-region input](supplemental/cu-pillar/estc_cupillar_pinfin_active1mm_p111.stk), [p100 alternative](supplemental/cu-pillar/estc_cupillar_pinfin_active1mm_p100.stk) | Calibrated geometry/velocity; identify calibration versus evaluation before quoting error |
| Silicon interlayer µCH | [Calibrated-lid baseline](supplemental/silicon-interlayer/ibm_intra_100W_calibrated.stk), [19–22 mL/min sweep](supplemental/silicon-interlayer/) | Advection, chip ordering, flow sensitivity; exact Table II variant not asserted |
| HyFlexPIM Cu-pillar / Icepak | [Pin-fin input](Baselines/HyFlexPIM/hfp_chiplet_pinfin.stk) | Package-scale pin-fin comparison; runner relocates its old absolute floorplan path |
| HyFlexPIM µCH/Cu-TGV / Icepak | [Frozen CFD anchor](supplemental/coefficient-comparison/hfp_tgv_E1c_anchored.stk) | Matched conjugate-CFD checkpoint; [circular](supplemental/coefficient-comparison/hfp_tgv_E1a_hausen.stk) / [square](supplemental/coefficient-comparison/hfp_tgv_E1b_hausen_square.stk) closures isolate coefficient sensitivity |
| Photonic package field | [2.5D baseline](Baselines/pic-sohrab/cpo_2p5d.stk), [3D comparison](supplemental/photonic/cpo_3d.stk) | Range and vertical-stacking trend; no precise scalar reference peak supplied |

These distinctions matter for the manuscript's aggregate **2.6%** claim: this archive does not independently rederive that statistic because exact inputs for every scalar checkpoint are not available. The H200 specification check and photonic range check are different kinds of evidence from a measured scalar error.

## Run

```bash
python3 tools/run_case.py validation/Baselines/H100/ttv_interpack.stk
python3 tools/run_case.py validation/supplemental/coefficient-comparison/hfp_tgv_E1c_anchored.stk
```

Run from the repository root. The wrapper creates a new isolated directory, copies each required `.flp`, fixes legacy path spelling in the staged copy, and sends generated outputs into its `outputs/` folder. Original input and archived result bytes remain intact. Use `--run-dir runs/unique-name` for a repeated run.

[Calibration protocol](../docs/calibration.md) · [Academic sources](../docs/references.md) · [Release verification](../docs/reproduction-status.md)
