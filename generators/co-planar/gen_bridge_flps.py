#!/usr/bin/env python3
"""
gen_bridge_flps.py -- Co-planar bridge floorplan generator (Stratum-S v2 canvas).

Emits, for each orientation (memW: memory column at low x; memE: mirrored in x):
    die_top_bridge_<o>.flp   top tier: MEM0 + OPT_IO + GPU0 (+ passive fill)
    die_bot_bridge_<o>.flp   bottom tier: LOGIC0 only, IDENTICAL block boundaries
    pic_plane_bridge_<o>.flp 20 um glass readout plane: COMB_SRC + 0 W markers
and for the anchor runs:
    pic_plane_zero.flp       readout plane with every block at 0 W

Every emitted floorplan is checked for: in-bounds, no overlap, exact tiling
(sum of block areas == canvas area), and the expected total power.
"""
import sys

CANVAS_X, CANVAS_Y = 39600, 31800
GRID = 100                      # every edge must sit on the 100 um simulation grid

# ---- v2 geometry (unchanged) ----
GAP_X0, GAP_X1 = 13000, 15000   # 2 mm guard gap / bridge seam
MEM_X0, MEM_X1 = 2000, 13000    # Mono3D column
MEM_Y0, MEM_Y1 = 10400, 21400   # 11 x 11 mm tile
GPU_Y0, GPU_Y1 = 2000, 29800    # 27.8 mm tall xPU
OPT_X0, OPT_X1 = 15000, 16200   # OPT_IO strip carved from GPU0 seam edge (1.2 mm)
GPU_X0, GPU_X1 = 16200, 37600   # GPU0 remainder (21.4 mm)

P_GPU, P_MEM, P_LOGIC, P_OPT, P_COMB = 230.0, 102.0, 42.67, 30.6, 0.0

# readout plane: comb at west edge mid-height, route east under MEM0 to the seam
COMB = (0, 15500, 400, 400)
ROUTE = (400, 15500, GAP_X0 - 400, 400)          # x 400..13000, under MEM0
BRIDGE = (GAP_X0, MEM_Y0, GAP_X1 - GAP_X0, MEM_Y1 - MEM_Y0)   # seam, memory span
MRR = (OPT_X0, MEM_Y0, OPT_X1 - OPT_X0, MEM_Y1 - MEM_Y0)      # under OPT_IO
WG_S = (GAP_X0, GPU_Y0, OPT_X1 - GAP_X0, MEM_Y0 - GPU_Y0)     # seam lanes below
WG_N = (GAP_X0, MEM_Y1, OPT_X1 - GAP_X0, GPU_Y1 - MEM_Y1)     # seam lanes above


def tile(actives):
    """Return list of (name, x, y, w, h, p) covering the canvas exactly.
    actives: list of (name, x, y, w, h, p). Fill is computed by slicing the
    canvas into rows at every active y-edge, then columns within each row."""
    ys = sorted({0, CANVAS_Y} | {a[2] for a in actives} | {a[2] + a[4] for a in actives})
    blocks, n = [], 0
    for y0, y1 in zip(ys, ys[1:]):
        # active blocks that span this row band
        row = sorted([a for a in actives if a[2] <= y0 and a[2] + a[4] >= y1], key=lambda a: a[1])
        x = 0
        for a in row:
            if a[1] > x:
                blocks.append((f"FILL_{n}", x, y0, a[1] - x, y1 - y0, 0.0)); n += 1
            x = a[1] + a[3]
        if x < CANVAS_X:
            blocks.append((f"FILL_{n}", x, y0, CANVAS_X - x, y1 - y0, 0.0)); n += 1
    # active blocks are emitted whole (not split by row); the row slicing above
    # only generates fill, so an active block must not partially overlap a band.
    for a in actives:
        for y0, y1 in zip(ys, ys[1:]):
            inter = max(0, min(a[2] + a[4], y1) - max(a[2], y0))
            assert inter in (0, y1 - y0), f"{a[0]} straddles row band {y0}-{y1}"
    return blocks + list(actives)


def check(blocks, p_expect):
    area = 0
    for b in blocks:
        name, x, y, w, h, p = b
        assert x >= 0 and y >= 0 and x + w <= CANVAS_X and y + h <= CANVAS_Y, f"{name} out of bounds"
        assert w > 0 and h > 0, f"{name} degenerate"
        for v in (x, y, w, h):
            assert v % GRID == 0, f"{name} off grid: {v}"
        area += w * h
    for i, a in enumerate(blocks):
        for b in blocks[i + 1:]:
            if a[1] < b[1] + b[3] and b[1] < a[1] + a[3] and a[2] < b[2] + b[4] and b[2] < a[2] + a[4]:
                raise AssertionError(f"overlap {a[0]} / {b[0]}")
    assert area == CANVAS_X * CANVAS_Y, f"tiling gap: {area} != {CANVAS_X*CANVAS_Y}"
    ptot = sum(b[5] for b in blocks)
    assert abs(ptot - p_expect) < 1e-6, f"power {ptot} != {p_expect}"


def mirror(blocks):
    return [(n, CANVAS_X - x - w, y, w, h, p) for (n, x, y, w, h, p) in blocks]


def write(path, header, blocks):
    with open(path, "w") as f:
        f.write(header)
        for name, x, y, w, h, p in blocks:
            f.write(f"{name} :\n    position  {x}, {y} ;\n    dimension {w}, {h} ;\n    power values {p:g} ;\n\n")


def main():
    # shared rectangle set for both die tiers (identical boundaries, per v2 rule)
    rects = [
        ("MEM0",   MEM_X0, MEM_Y0, MEM_X1 - MEM_X0, MEM_Y1 - MEM_Y0),
        ("OPT_IO", OPT_X0, GPU_Y0, OPT_X1 - OPT_X0, GPU_Y1 - GPU_Y0),
        ("GPU0",   GPU_X0, GPU_Y0, GPU_X1 - GPU_X0, GPU_Y1 - GPU_Y0),
    ]
    top_p = {"MEM0": P_MEM, "OPT_IO": P_OPT, "GPU0": P_GPU}
    bot_p = {"MEM0": 0.0, "OPT_IO": 0.0, "GPU0": 0.0}
    top = tile([(n, x, y, w, h, top_p[n]) for n, x, y, w, h in rects])
    bot = [(("LOGIC0" if n == "MEM0" else ("FILL_UNDER_" + n if n in bot_p else n)),
            x, y, w, h, (P_LOGIC if n == "MEM0" else 0.0)) for n, x, y, w, h, p in top]

    pic_act = [("COMB_SRC",) + COMB + (P_COMB,), ("PIC_ROUTE",) + ROUTE + (0.0,),
               ("BRIDGE",) + BRIDGE + (0.0,), ("PIC_MRR",) + MRR + (0.0,),
               ("PIC_WG_S",) + WG_S + (0.0,), ("PIC_WG_N",) + WG_N + (0.0,)]
    pic = tile(pic_act)
    pic_zero = [(n, x, y, w, h, 0.0) for n, x, y, w, h, p in pic]

    for o, fn in (("memW", lambda b: b), ("memE", mirror)):
        t, b, pl = fn(top), fn(bot), fn(pic)
        check(t, P_GPU + P_MEM + P_OPT); check(b, P_LOGIC); check(pl, P_COMB)
        note = "memory column at LOW x (west)" if o == "memW" else "MIRRORED in x: memory column at HIGH x (east)"
        gpu_a = (GPU_X1 - GPU_X0) * (GPU_Y1 - GPU_Y0) / 1e6
        write(f"die_top_bridge_{o}.flp",
              f"// die_top_bridge_{o}.flp -- co-planar bridge, TOP tier ({note}).\n"
              f"// Derived from die_top_S_v2.flp. Same canvas {CANVAS_X}x{CANVAS_Y}, same 2 mm seam,\n"
              f"// same MEM0 tile. OPT_IO (Hsueh OJSSCS'25 Table 1: 30.6 W) carved from GPU0's\n"
              f"// seam-facing edge as {OPT_X1-OPT_X0}x{GPU_Y1-GPU_Y0} um = {(OPT_X1-OPT_X0)*(GPU_Y1-GPU_Y0)/1e6:.2f} mm^2\n"
              f"// -> {P_OPT/((OPT_X1-OPT_X0)*(GPU_Y1-GPU_Y0)/1e6):.3f} W/mm^2 (paper 0.93). GPU0 keeps 230 W over {gpu_a:.1f} mm^2\n"
              f"// = {P_GPU/gpu_a*100:.1f} W/cm^2 (v2: 36.6). Mono3D column unchanged at 119.6 W/cm^2.\n"
              f"// Generated by gen_bridge_flps.py -- regenerate, do not hand-edit.\n\n", t)
        write(f"die_bot_bridge_{o}.flp",
              f"// die_bot_bridge_{o}.flp -- co-planar bridge, BOTTOM tier ({note}).\n"
              f"// Block boundaries IDENTICAL to die_top_bridge_{o}.flp (cell-aligned Tmaps).\n"
              f"// LOGIC0 {P_LOGIC} W (Stratum Sec. 6.2.3) under MEM0; all else passive. The silicon\n"
              f"// under GPU0/OPT_IO/seam is the documented 3D-ICE per-layer-material artefact.\n"
              f"// Generated by gen_bridge_flps.py.\n\n", b)
        write(f"pic_plane_bridge_{o}.flp",
              f"// pic_plane_bridge_{o}.flp -- 20 um GLASS readout plane inside the interposer ({note}).\n"
              f"// Pattern: pic-sohrab/pic_plane.flp. Powered: COMB_SRC {P_COMB} W (Hsueh Fig. 9 pump, all -> heat).\n"
              f"// 0 W REGION MARKERS (their Tflp is the temperature the optics see):\n"
              f"//   PIC_ROUTE  400 um lane from the comb, running under the FULL MEM0 tile to the seam\n"
              f"//   BRIDGE     the seam under the memory span (EMIB-style bridge footprint)\n"
              f"//   PIC_MRR    under OPT_IO: ring modulators / detectors\n"
              f"//   PIC_WG_S/N seam + OPT_IO lanes below/above the memory span\n"
              f"// Lateral gradient = max(PIC_ROUTE) - min(PIC_ROUTE), and PIC_MRR max - min.\n"
              f"// Generated by gen_bridge_flps.py.\n\n", pl)
    check(pic_zero, 0.0)
    write("pic_plane_zero.flp",
          "// pic_plane_zero.flp -- readout plane with ALL blocks at 0 W, for the anchor runs\n"
          "// (static-anchor / flow-anchor use the unchanged v2 die floorplans + this plane, so the\n"
          "// only change vs stratum_S_v2_liquid.stk is one extra node plane inside the glass).\n"
          "// Generated by gen_bridge_flps.py.\n\n", pic_zero)
    print("OK: 7 floorplans written, all tiling/overlap/bounds/power checks passed")
    print(f"  GPU0 {P_GPU/gpu_a*100:.2f} W/cm^2 over {gpu_a:.2f} mm^2; OPT_IO {P_OPT/33.36:.3f} W/mm^2; top tier {P_GPU+P_MEM+P_OPT} W")


if __name__ == "__main__":
    main()
