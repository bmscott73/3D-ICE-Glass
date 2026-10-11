# Calibration, units, and transfer limits

The source of truth for a simulation is the active numeric statements in its `.stk` and `.flp`. [The input index](case-index.md) removes comments before reporting parameters. Imported files remain unchanged, including their historical comments.

## What the engine solves

3D-ICE 4.0 constructs a compact thermal conductance/capacitance network. Steady simulations solve `G T = P` with environmental terms; transient simulations include the cell heat capacities. Glass-package geometry, source placement, and cooling parameters are supplied through inputs. The release includes the clean EPFL revision recorded in [upstream.json](../provenance/upstream.json).

The Russell working tree also contained client/server DTM experiments and two null-pointer guards in `thermal_data.c`. These uncommitted modifications are excluded from the pinned engine. The rectangular cases use the stock emulator, not those client/server extensions.

## Input units

| Input | Native units | Conversion to SI |
|---|---|---|
| Length, layer thickness | µm | multiply by 1e-6 for m |
| Thermal conductivity | W/(µm·K) | multiply by 1e6 for W/(m·K) |
| Volumetric heat capacity | J/(µm³·K) | multiply by 1e18 for J/(m³·K) |
| Heat transfer coefficient | W/(µm²·K) | multiply by 1e12 for W/(m²·K) |
| Power per floorplan block | W | already SI; entries are block totals |
| Temperature | K | subtract 273.15 for °C |
| Time step and power slot | s | already SI |
| Coolant flow rate | mL/min | total flow specified by the channel model |
| Darcy velocity | µm/s | multiply by 1e-6 for m/s |

For example, glass `k = 1.40e-6` represents **1.4 W/mK**, and water `C_vol = 4.18e-12` represents **4.18 MJ/m³K**. Every directional material value and layer height is retained in the stack, rather than hidden in a shared global default.

## Anchor, freeze, evaluate

1. Match the reference geometry, material, cooled footprint, power, coolant, and inlet.
2. Extract one missing effective cooling input from experiment, conjugate CFD, or a specification. Record whether it is a calibration, a held-out test, a range check, or a specification check.
3. Freeze that input before evaluating another floorplan or power map in the same domain. Changing the coolant or hydraulic domain requires a new anchor.

### Direct-to-chip plate

The surface boundary is `q'' = h_cp (T_surface - T_ref)`. Water architecture cases use **40,800 W/m²K**. For the 39.6 × 31.8 mm footprint, the applied area is **1259.28 mm²** and conductance is approximately **51.38 W/K**. The original H200 boundary is a [manufacturer specification](references.md#plate), not a fitted measurement of every later package.

An explicit 20 µm TIM and 2 mm copper base are retained in the architecture stacks. The H100 copper TTV has its own **43,956 W/m²K** effective case-to-saturation boundary, which already lumps its interface/cold-plate resistance. It must not be substituted into the TIM-explicit package without checking what is already included.

The [H200 probe](../validation/Baselines/H200/h200_stratum_htc_probe.stk) is archived at **300 K**. To compare its plate-contact result with the vendor's **38 °C** inlet, apply the common-reference steady offset **311.15 - 300 = 11.15 K**. A silicon-source maximum is a different observation plane.

### Glass microchannel / Cu-TGV

The [anchored coefficient case](../validation/supplemental/coefficient-comparison/hfp_tgv_E1c_anchored.stk) uses approximately **12,700 W/m²K**, derived from `wall heat flux / (wall temperature - local bulk coolant temperature)` in conjugate CFD. The 4RM channel model receives this effective coefficient; it does not resolve all developing-flow and conjugate wall effects.

HyFlexPIM uses a 26.1 × 17.4 mm chiplet, 100 µm channel/wall dimensions, and **156.5 mL/min** per chiplet. The interlayer packages extend the same velocity-matched domain to **197 channels and 237.2 mL/min**. Frozen `h_eff` does not establish hydraulic pressure drop; channel pressure and manifold losses must be evaluated separately.

The controlled coefficient comparison holds geometry, flow, materials, inlet, and floorplan fixed, and contrasts [Hausen circular](../validation/supplemental/coefficient-comparison/hfp_tgv_E1a_hausen.stk), [square duct](../validation/supplemental/coefficient-comparison/hfp_tgv_E1b_hausen_square.stk), and [CFD anchor](../validation/supplemental/coefficient-comparison/hfp_tgv_E1c_anchored.stk). These are alternative closures of one compact model, not three independent experiments.

### Direct-contact copper pin fins

The 4RM pin-fin model computes its wall coefficient from Darcy velocity and pin geometry. The [corrected active 1 × 1 mm vehicle](../validation/supplemental/cu-pillar/estc_cupillar_pinfin_active1mm_p111.stk) retains the reference active area, **5.02 W** load, **295.15 K** inlet, and calibrated superficial velocity. It is distinct from the package-scale [HyFlexPIM pin-fin input](../validation/Baselines/HyFlexPIM/hfp_chiplet_pinfin.stk). Do not transfer the fitted velocity to a new footprint without checking the flow interpretation.

### Dual-side air sink

The secondary coefficient is an area-normalized **sink-to-air conductance**, not a raw local air-film coefficient. The [ATS sink](references.md#air) has catalogued ducted resistances at 1/2/3/4 m/s. The bounded 4 m/s cases use `h_air = 3.453e-9 W/µm²K`, equivalent to approximately **0.230 K/W** over the 1259.28 mm² package footprint. The catalogue sink base overhangs the package and requires its specified airflow condition. Air and liquid references are both **308 K** in the warm-loop cases.

## Warm-loop envelope

The manuscript compares inhibited propylene glycol at the conservative **30 vol%** edge to water properties at 40 °C. Ratios are `rho=1.04`, `c_p=0.92`, `k=0.735`, and `mu=2.49`. Constant laminar Nusselt number gives `h/h_water=0.735`; a Dittus–Boelter property estimate gives approximately 0.576, implemented as **0.575**. This brackets the unresolved plate boundary; it is not an independently calibrated glycol cold plate.

Both embedded-cavity endpoints retain the laminar **0.735** coefficient multiplier and `C_vol=3.95e-12 J/µm³K`. The **237.2 mL/min** flow remains fixed. The active statements in both `emb-E4-735` and `emb-E4-575` put the plate and cavity at **308 K**.

With temperature-independent coefficients, a uniform shift of **all** environmental references and the initial state preserves the transient temperature differences and shifts absolute temperature by the same amount. Changing only the liquid reference in a hybrid design does not give that identity. Source files use **308 K = 34.85 °C**, while the manuscript often calls this 35 °C; record the exact inlet when comparing sub-kelvin differences.

## Power, grids, and feasibility

Floorplan power entries are **watts per rectangular block**, not W/cm². The panel maps independently assign memory, logic/transfer, and PIC power; uniform scaling of every block does not reproduce the workload ladder. The prefill xPU/HBM/PIC are fixed at **300/20/3.05 W** because a prefill activity trace was unavailable. The decode mapping is based on GLM-4.5 MoE BF16, context 65,536, and the architecture assumptions cited in the manuscript; it is not direct hardware power telemetry.

Most package cases use **100 × 100 µm** cells; released panel and transient cases use **200 × 200 µm**, and some validation vehicles have other pitches. The silicon-interlayer 4RM geometry requires **75 × 100 µm** cells. The [index](case-index.md) records each active grid. Do not silently coarsen a model and report it as the paper case.

The manuscript's **85 °C** ceiling is a system-level comparison threshold. Compute `H = min_i(T_limit,i - T_max,i)` and identify the limiting block. PIC temperature spread and transient slew are additional metrics; a universal optical failure threshold is not supplied.

Uniform-power steady capacity can be estimated as `P_sus = P_nom * min(1, (T_limit-T_ref)/(T_max-T_ref))` when the model is linear and all environmental references share `T_ref`. This is a static capacity estimate, not a closed-loop control simulation.
