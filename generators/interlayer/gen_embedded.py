#!/usr/bin/env python3
"""
gen_embedded.py -- embedded-tier floorplans for the cost-aware interlayer-cooling package.

Canvas 39600 x 31800, 100 um grid (MANDATORY: the HyFlexPIM analog strip is 1300 um and its
edges sit on 100 um; the 4rm cavity also forces 100 um columns).

The embedded tier sits BELOW the glass cavity. Lateral rules:
  - No embedded block is placed under the TOP-tier Mono3D column (x 2000..13000). Stacking
    two 119.6 W/cm^2 columns is the one thing the cavity should not be asked to fix.
  - Stack slots are symmetric about y = 15900 (the flow axis midline), so S0/S2 vs S1/S3
    is a controlled upstream/downstream pair, exactly like the v2 anchor's symmetric fills.
  - Slot order is fixed: E1 uses S0, E2 uses S0+S1, E4 uses S0..S3, and HyFlexPIM configs
    reuse S0+S1 unchanged. N is the only variable across the sweep.

A Mono3D stack is ONE source block at 144.67 W / 121 mm^2 = 119.6 W/cm^2. The two tiers are
lumped because the hybrid-bonded pair measured isothermal to 0.22 K in the dual-plate runs.
"""
import re

CX, CY, GRID = 39600, 31800, 100
P_M3D = 144.67                      # 102 W DRAM + 42.67 W NMP logic, lumped
M3D_W = M3D_H = 11000

# stack slots, all at x >= 16400 (clear of the top-tier memory column), y-symmetric about 15900
SLOTS = [("S0", 28400, 3000), ("S1", 28400, 17800), ("S2", 16400, 3000), ("S3", 16400, 17800)]
HFP_X, HFP_Y = 1000, 7200           # HyFlexPIM 26100 x 17400, unrotated: flow +y, rows in series
HFP_SRC = "hfp_chiplet_duty.flp"


def hfp_blocks():
    txt = open(HFP_SRC).read()
    b = re.findall(r"^(\w+)\s*:\s*\n\s*position\s+(\d+),\s*(\d+)\s*;\s*\n\s*"
                   r"dimension\s+(\d+),\s*(\d+)\s*;\s*\n\s*power values\s+([\d.]+)\s*;", txt, re.M)
    out = [(f"HFP_{n}", HFP_X + int(x), HFP_Y + int(y), int(w), int(h), float(p)) for n, x, y, w, h, p in b]
    assert abs(sum(o[5] for o in out) - 140.70) < 1e-6, "HyFlexPIM power != 140.70 W"
    assert sum(o[3] * o[4] for o in out) == 26100 * 17400, "HyFlexPIM does not tile its own chiplet"
    return out


def tile(actives):
    ys = sorted({0, CY} | {a[2] for a in actives} | {a[2] + a[4] for a in actives})
    for a in actives:
        for y0, y1 in zip(ys, ys[1:]):
            inter = max(0, min(a[2] + a[4], y1) - max(a[2], y0))
            assert inter in (0, y1 - y0), f"{a[0]} straddles band {y0}-{y1}"
    out, n = [], 0
    for y0, y1 in zip(ys, ys[1:]):
        row = sorted([a for a in actives if a[2] <= y0 and a[2] + a[4] >= y1], key=lambda a: a[1])
        x = 0
        for a in row:
            if a[1] > x:
                out.append((f"FILL_{n}", x, y0, a[1] - x, y1 - y0, 0.0)); n += 1
            x = a[1] + a[3]
        if x < CX:
            out.append((f"FILL_{n}", x, y0, CX - x, y1 - y0, 0.0)); n += 1
    return out + list(actives)


def check(blocks, p_expect, label):
    area = 0
    for name, x, y, w, h, p in blocks:
        assert 0 <= x and 0 <= y and x + w <= CX and y + h <= CY, f"{label}/{name} out of bounds"
        assert w > 0 and h > 0, f"{label}/{name} degenerate"
        for v in (x, y, w, h):
            assert v % GRID == 0, f"{label}/{name} off the {GRID} um grid: {v}"
        area += w * h
    for i, a in enumerate(blocks):
        for b in blocks[i + 1:]:
            if a[1] < b[1] + b[3] and b[1] < a[1] + a[3] and a[2] < b[2] + b[4] and b[2] < a[2] + a[4]:
                raise AssertionError(f"{label}: overlap {a[0]} / {b[0]}")
    assert area == CX * CY, f"{label}: tiling gap {area} != {CX*CY}"
    tot = sum(b[5] for b in blocks)
    assert abs(tot - p_expect) < 1e-6, f"{label}: power {tot:.3f} != {p_expect:.3f}"
    # No embedded Mono3D stack may sit under the TOP-tier Mono3D column: superposing two
    # 119.6 W/cm^2 columns across a 100 um cavity is the one case the cavity should not be
    # asked to fix, and it would confound the capacity sweep.
    # HyFlexPIM is EXEMPT and does overlap the column (it is 26.1 mm wide; clearing the
    # column and leaving room for stacks beside it is geometrically impossible). Its
    # background is 3 W/cm^2 digital, so the superposition is mild, and whether the cavity
    # decouples the two tiers there is a RESULT of config H1, not an assumption.
    for name, x, y, w, h, p in blocks:
        if p > 0 and name.startswith("EMB_M3D"):
            assert x >= 13000, f"{label}/{name} sits under the top-tier Mono3D column"


def write(path, header, blocks, p_expect):
    check(blocks, p_expect, path)
    with open(path, "w") as f:
        f.write(header)
        for name, x, y, w, h, p in blocks:
            f.write(f"{name} :\n    position  {x}, {y} ;\n    dimension {w}, {h} ;\n    power values {p:g} ;\n\n")


CFG = {  # name -> (n_stacks, hyflexpim?)
    "E0": (0, False), "E1": (1, False), "E2": (2, False), "E4": (4, False),
    "H1": (0, True), "H1M2": (2, True),
}

def main():
    hfp = hfp_blocks()
    for name, (n, use_hfp) in CFG.items():
        act = []
        if use_hfp: act += hfp
        for i in range(n):
            sn, sx, sy = SLOTS[i]
            act.append((f"EMB_M3D_{i}", sx, sy, M3D_W, M3D_H, P_M3D))
        blocks = tile(act)
        p = n * P_M3D + (140.70 if use_hfp else 0.0)
        emb_area = n * M3D_W * M3D_H / 1e6 + (454.14 if use_hfp else 0.0)
        hdr = (f"// die_emb_{name}.flp -- EMBEDDED TIER, below the glass microchannel cavity.\n"
               f"// Config {name}: {n} Mono3D stack(s){' + HyFlexPIM chiplet' if use_hfp else ''}.\n"
               f"// Embedded power {p:.2f} W over {emb_area:.2f} mm^2. Top tier adds 405.27 W.\n"
               f"// Mono3D stack = ONE block at 144.67 W / 121 mm^2 = 119.6 W/cm^2 (102 W DRAM +\n"
               f"//   42.67 W NMP logic lumped; the hybrid-bonded pair measured isothermal to\n"
               f"//   0.22 K in the dual-plate runs, so resolving the two tiers buys nothing here).\n"
               f"// HyFlexPIM blocks are hfp_chiplet_duty.flp VERBATIM, translated to ({HFP_X}, {HFP_Y}):\n"
               f"//   140.70 W duty-weighted, 6 analog strips at 190 W/cm^2, unrotated so the coolant\n"
               f"//   still flows +y with the PU rows in series, as in the validated chiplet.\n"
               f"// Slot order is fixed across configs (S0, S1, S2, S3) so N is the only variable.\n"
               f"// Slots are y-symmetric about 15900: S0/S2 vs S1/S3 is a controlled upstream/\n"
               f"//   downstream pair. No powered block sits under the top-tier Mono3D column.\n"
               f"// Generated by gen_embedded.py -- regenerate, do not hand-edit.\n\n")
        write(f"die_emb_{name}.flp", hdr, blocks, p)
        print(f"  {name:5s} {n} stack(s){' + HFP' if use_hfp else '     '}  "
              f"embedded {p:7.2f} W  total {p+405.27:7.2f} W  area {emb_area:6.2f} mm^2")
    print("OK: 6 embedded floorplans written; tiling / overlap / bounds / grid / power / "
          "no-column-stacking all asserted")

if __name__ == "__main__":
    main()
