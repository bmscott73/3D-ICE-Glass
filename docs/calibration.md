# Calibration and transfer

Anchor one cooling primitive against a reference, freeze its coefficients, and then change floorplans or workload maps within that primitive's domain. [Materials](../library/materials.json) and [primitives](../library/primitives.json) carry provenance and transfer conditions. A change of coolant, channel geometry, wall material, contact interpretation or flow regime needs a new anchor.

## Stage 1: CFD wall-flux extraction

```bash
python3 tools/calibrate.py cfd wall-patches.csv --projected-area-um2 454140000
```

CSV columns are `area_um2,wall_K,bulk_K,heat_W`. `heat_W` is heat removed into the coolant; use the local bulk fluid temperature for each patch. The effective projected-area coefficient is

`h_eff = sum(Q_wall) / [A_projected * area-weighted(T_wall - T_bulk)]`.

The tool also reports wetted area, heat, mean temperature difference, native `h`, and W/m²K. Declare the projected area used by the compact model: substituting wetted area without conversion changes the boundary. Include the CFD geometry, flow, coolant and wall-material identity in the new anchor's provenance. The project's frozen glass/Cu-TGV coefficient is **1.27e-8 W/µm²K**; raw CFD wall patches are not part of this input release.

A synthetic format/example check:

```bash
python3 tools/calibrate.py cfd examples/calibration/synthetic-cfd.csv \
  --projected-area-um2 2000000
```

Expected `h = 8.181818e-8 W/µm²K`. This synthetic CSV illustrates the calculation and is not the project's CFD anchor.

## Stage 1: TTV boundary fit

```bash
python3 tools/calibrate.py ttv calibration-points.csv --area-mm2 910
```

CSV columns are `power_W,case_C,saturation_C`. Fit `T_case - T_local_sat = R_case_sat * Q` through zero, then obtain `G = 1/R` and `h = G/A_applied`. Use only calibration powers in this CSV; held-out predictions belong in separate files. The tool records calibration powers and residuals.

For the H100-scale vehicle, the **510 W** fit gives **h = 4.4186e-8 W/µm²K**, frozen for the **720 and 920 W** inputs. Local saturation temperature is power-specific. The 720 W paper result is **64.83 °C**, against **64.90 °C**. The model's 5 µm-deep case probe is corrected to the surface by subtracting `Q * 5 µm / (k_Cu * A)`. This checks a copper case-to-coolant abstraction; it is not a silicon junction validation. Do not add an explicit TIM if the adopted effective boundary already lumps it.

`examples/calibration/synthetic-ttv.csv` gives an independent arithmetic check: `R = 0.5 K/W`, `G = 2 W/K`, `h = 2e-8 W/µm²K` over 100 mm². The raw experimental digitization used for the historical 510 W fit is not bundled; the recovered fitted inputs and power-specific references are.

## Stage 1: catalogued air sink

```bash
python3 tools/calibrate.py air --resistance-k-w .23 \
  --area-mm2 1259.28 --sink-base-mm2 8700
```

Convert sink-to-air resistance to conductance, `G = 1/R`, then normalize to the area where the engine applies the boundary, `h = G/A_applied`. At 4 m/s, the ATS sink's **0.23 K/W** gives **4.347826 W/K** and **3.452629e-9 W/µm²K** over the 39.6 × 31.8 mm model. The physical 100 × 87 mm sink base is 6.91× larger; dividing by that base and applying the result over the smaller model would change conductance. The other ducted resistances are 0.52/0.32/0.26 K/W at 1/2/3 m/s. [Manufacturer reference](references.md#air).

## Stage 2: frozen inputs and property endpoints

- Water plate: **4.08e-8 W/µm²K**, 300 K laboratory reference, with explicit copper base and TIM.
- HyFlexPIM 4RM: **130 channels**, 100 × 100 µm flow sections, **156.5 mL/min**, 300 K inlet, Cu-TGV wall composite, **1.27e-8** prescribed side/top/bottom coefficients.
- Interlayer package: **197 channels**, **237.2 mL/min**, preserving approximately 2.006 m/s channel velocity.
- Warm loop: **308 K** references (34.85 °C, rounded to 35 °C in the paper), top-plate multipliers **0.735 / 0.575**. The cavity uses **0.735** at both endpoints and native volumetric capacity **3.95e-12 J/µm³K**. These explicit inputs form a sensitivity envelope; they do not constitute a new glycol calibration.
- Constant orthotropic material tensors and layer thicknesses are explicit in each native input. The TGV composite is an effective medium, not a resolved via mesh.

A uniform reference-temperature shift is exact for these constant-property steady models when every heat-removal reference moves together. The active H200 checkpoint uses 311.15 K directly; the archive's 300 K case is equivalent after an 11.15 K shift. In dual-side cases both air and liquid references must move together.

## Observations and tolerances

Match the physical plane: copper case surface, copper plate contact, active die, bottom die, or named PIC footprint. Simulator output is kelvin. Subtract **273.15** for Celsius; a temperature difference has the same numerical value in kelvin and Celsius.

Each [checkpoint](../validation/README.md) separates the model reproduction target, numerical tolerance, experimental/CFD reference, and assessment type. The silicon row uses the original **22 mL/min per layer** case and is flow-conditioned. H200 is a specification check and the PIC row is a range/topology comparison; neither enters the eight-scalar aggregate. [Reproduction notes](reproduction-status.md) retain the detailed historical differences.
