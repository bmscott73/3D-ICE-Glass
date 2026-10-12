# Anchor once, freeze, transfer

![Calibration workflow and glass-package thermal exploration](figures/methodology.png)

[Original figure PDF](figures/source/methodology.pdf).

1. **Define the reference and its observation plane.** Record physical geometry, source power, coolant/reference temperature, flow, and contact area. Distinguish a measured peak from a vendor limit or field range.
2. **Anchor the cooling primitive.** [Stage 1 tools](calibration.md) extract projected effective HTC from CFD wall flux, fit a TTV case boundary, or convert a catalogued sink resistance into applied-area conductance.
3. **Freeze the primitive.** Store parameters, units, source and transfer domain in [the library](../library/primitives.json). Preserve the material tensor, wall geometry and velocity regime needed by that anchor.
4. **Build and explore.** [Stack/floorplan builders](builders.md) check bounds, overlap, area and power. Vary placement, embedded capacity, plate-property endpoints or workload queues; generate native `.stk`/`.flp` inputs.
5. **Report the right output.** Use block maxima, averages, lateral spans and finite-difference transient slew. For architecture studies the paper compares against an 85 °C ceiling; device-specific photonic drift/tracking limits require their own inputs.

[Validation table](../validation/README.md) · [Paper commands](reproduce.md) · [Transient workflow](../transient/README.md).
