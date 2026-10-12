#!/usr/bin/env python3
"""
build_embedded_stks.py -- cost-aware interlayer-cooling package.

COMPOSITION: the validated co-planar bridge ABOVE the cavity, the validated glass
microchannel + Cu-TGV primitive AS the cavity, an embedded accelerator/memory tier below it,
and the photonic readout plane at the bottom. Above IPOSER_TGV the stack is byte-identical
to static-standard; the cavity block and the three layers under it are lifted verbatim from
hfp_chiplet_4rm_tgvwall_v4.stk, the file carrying the 0.69 C Icepak checkpoint.

The bridge's IPOSER_CAV_L was a 100 um solid-glass placeholder documented as "no interlayer
cavity in this package". It becomes the cavity, at exactly the validated 100 um height.

FROZEN PRIMITIVE -- what is reused unchanged and what is a documented transfer:
  reused: channel/wall 100/100 um, height 100 um, TGV-composite walls, h = 1.27e-8 on all
          faces, water Cp 4.18e-12, per-channel velocity 2.006 m/s.
  transfer 1: 197 channels here vs 130 in the anchor. Flow is set by VELOCITY match, not by
          copying the absolute rate: 197 x 1.204 = 237.2 mL/min (anchor 130 x 1.204 = 156.5).
  transfer 2: channel length 31.8 mm vs 17.4 mm. At Re ~ 200 the thermal entry length is
          ~7 mm, so the developing fraction falls from ~40% to ~22% and the frozen mean
          h_eff is slightly OPTIMISTIC here. Report as a transfer, like the wall-material
          transfer that held to 3.59 C, not as a validated point.
  NOT done: no pin-fin cavity and no cavity flow sweep beyond a single labelled DTM probe.
          The pin-fin coefficient is computed internally from a Darcy velocity, carries a
          -3.63 C bias, and its flow dependence is unverified (Sec. IV-A). Sweeping flow on
          pin-fins would sweep an unvalidated correlation. The microchannel primitive takes
          a DECLARED h, and its advection is verified (1/Q ordering to 1%, energy balance to
          0.08%), so it is the only safe embedded workhorse.

WARM CONDITIONS ARE REAL RUNS HERE. With a cavity present the coolant heat capacity enters
the advection terms, so PG30 cannot be applied as an offset the way it can to a pure Robin
package. 318 K remains an exact offset from the 308 K runs.
"""
import os
OUT = "outputs-emb"
CFGS = ["E0", "E1", "E2", "E4", "H1", "H1M2"]
NSTACK = {"E0": 0, "E1": 1, "E2": 2, "E4": 4, "H1": 0, "H1M2": 2}
PEMB = {"E0": 0.0, "E1": 144.67, "E2": 289.34, "E4": 578.68, "H1": 140.70, "H1M2": 430.04}
PG30 = 0.735
Q_NOM = 237.2          # mL/min, velocity-matched to the 2.006 m/s anchor over 197 channels

MATERIALS = """
material SILICON :
    thermal conductivity     1.30e-04 ;
    volumetric heat capacity 1.75e-12 ;
material SILICON_PIM :               // as in hfp_chiplet_4rm_tgvwall_v4.stk
    thermal conductivity     1.30e-04 ;
    volumetric heat capacity 1.628e-12 ;
material TIM :
    thermal conductivity     4.00e-06 ;
    volumetric heat capacity 4.00e-12 ;
material COPPER :
    thermal conductivity     4.00e-04 ;
    volumetric heat capacity 3.45e-12 ;
material HYBRID_BOND :
    thermal conductivity     1.21e-04 ;
    volumetric heat capacity 2.14e-12 ;
material UBUMP_UF :
    thermal conductivity     2.00e-05 ;
    volumetric heat capacity 2.50e-12 ;
material GLASS :
    thermal conductivity     1.40e-06 ;
    volumetric heat capacity 1.60e-12 ;
material TGV_GLASS_COMPOSITE :
    thermal conductivity     1.00e-06, 1.00e-06, 7.9204e-05 ;
    volumetric heat capacity 1.96e-12 ;
material SINTER_AG :                 // die attach, from the validated HyFlexPIM stack
    thermal conductivity     2.00e-04 ;
    volumetric heat capacity 2.50e-12 ;
"""

DIMS = """
dimensions :
    chip length 39600, width 31800 ;
    cell length 100,   width 100 ;   // FORCED: the 4rm cavity tiles the LENGTH at 100 um,
    non-uniform false ;              // and the HyFlexPIM analog strip is only 1300 um wide.
"""

LAYERS = """
layer CP_BASE_L :            // 2 mm Cu cold-plate base; h_cp on its OUTER face
    height   2000 ;
    material COPPER ;
layer TIM_L :
    height   20 ;
    material TIM ;
layer HB_L :
    height   1 ;
    material HYBRID_BOND ;
layer UBUMP_L :
    height   40 ;
    material UBUMP_UF ;
layer IPOSER_TGV_L :         // chip-side RDL + Cu-TGV field; also the cavity's upper wall
    height   110 ;
    material TGV_GLASS_COMPOSITE ;
layer TGVS_L :               // VERBATIM from hfp_chiplet_4rm_tgvwall_v4.stk
    height   100 ;
    material TGV_GLASS_COMPOSITE ;
layer ATTACH_L :             // VERBATIM: sinter-Ag die attach
    height   20 ;
    material SINTER_AG ;
layer IPOSER_CORE_L :
    height   150 ;
    material GLASS ;

die DIE_TOP_D :
    layer  145 SILICON ;
    source   5 SILICON ;
die DIE_BOT_D :
    source   5 SILICON ;
    layer   95 SILICON ;
die DIE_EMB_D :              // embedded tier; source depth as in the validated PIM die
    layer   50 SILICON_PIM ;
    source    5 SILICON_PIM ;
    layer   45 SILICON_PIM ;
die PIC_PLANE_D :
    source  20 GLASS ;
"""

def channel(q, h, cp, tin):
    return f"""
microchannel 4rm :                   // VALIDATED glass uCH + Cu-TGV primitive
    height 100 ;
    channel length 100 ;
    wall length 100 ;
    first wall length 200 ;          // 200 + 197x100 + 196x100 + 100 = 39600 -> 197 channels
    last wall length 100 ;
    wall material TGV_GLASS_COMPOSITE ;
    coolant flow rate {q:g} ;               // TOTAL over 197 channels; per-channel 2.006 m/s
    coolant heat transfer coefficient
        side   {h:.4g},
        top    {h:.4g},
        bottom {h:.4g} ;
    coolant volumetric heat capacity {cp:.4g} ;
    coolant incoming temperature {tin} ;
"""

def outs(tag):
    o = f"""
solver :
    steady ;
    initial temperature 300.0 ;
    numofcores 12 ;

output :
"""
    for d in ("DIE_TOP", "DIE_BOT", "DIE_EMB", "PIC_PLANE"):
        for m in ("maximum", "average", "minimum"):
            o += f'    Tflp( {d}, "{OUT}/{tag}_{d.lower()}_{m[:3]}.txt", {m}, final ) ;\n'
    for d in ("DIE_TOP", "DIE_EMB", "PIC_PLANE", "CP_BASE", "EMB_CH"):
        o += f'    Tmap( {d}, "{OUT}/{tag}_{d.lower()}_tmap.txt", final ) ;\n'
    return o

def stk(tag, cfg, h_cp, h_ch, cp, tin, q, note):
    ptot = 405.27 + PEMB[cfg]
    qcp = q * cp * 1e12 / 60.0
    q_ch = PEMB[cfg] / 197.0
    hdr = f"""// ============================================================
// {tag}.stk -- COST-AWARE INTERLAYER-COOLING GLASS PACKAGE, config {cfg}
// {note}
//
// D2C plate | Cu base | TIM | xPU + OPT_IO + Mono3D (co-planar bridge, VERBATIM)
//   | ubump | Cu-TGV RDL | GLASS uCH CAVITY | TGV | sinter-Ag | EMBEDDED TIER | PIC | glass
//
// Embedded tier: {NSTACK[cfg]} Mono3D stack(s){' + HyFlexPIM chiplet' if cfg.startswith('H') else ''} = {PEMB[cfg]:.2f} W.
// Package total {ptot:.2f} W ({100*PEMB[cfg]/ptot:.1f}% embedded).
// Cavity: 197 channels, {q:g} mL/min, h = {h_ch:.4g}, Cp = {cp:.4g}, inlet {tin} K.
//   Expected cavity outlet rise if it took ALL the heat: {ptot/qcp:.2f} K (Q*Cp = {qcp:.2f} W/K).
//   It will not: the top tier also sees the plate. Measured split is the point of the run.
// Plate: h_cp = {h_cp:.4g}, reference {tin} K.
// Grid 396 x 318 x 18 layers = 2,266,704 nodes. This is 29% above the largest stack that
//   has factored here (1.76M, flow-anchor at sane flow). See README if SuperLU_MT refuses.
// NOTE: per-channel heat load is {q_ch:.2f} W vs 1.08 W at the anchor, so the coolant BULK
//   RISE, not the wall coefficient, is expected to bind at high N. That is a real capacity
//   limit and it is what makes flow the DTM lever.
// Generated by build_embedded_stks.py.
// ============================================================
"""
    top = f"""
top heat sink :
    heat transfer coefficient {h_cp:.4g} ;
    temperature {tin} ;
"""
    stack = f"""
stack :
    layer   CP_BASE     CP_BASE_L ;
    layer   TIM_TOP     TIM_L ;
    die     DIE_TOP     DIE_TOP_D   floorplan "die_top_bridge.flp" ;
    layer   HB_IFACE    HB_L ;
    die     DIE_BOT     DIE_BOT_D   floorplan "die_bot_bridge.flp" ;
    layer   UBUMP       UBUMP_L ;
    layer   IPOSER_TGV  IPOSER_TGV_L ;
    channel EMB_CH ;
    layer   TGVS        TGVS_L ;
    layer   ATTACH      ATTACH_L ;
    die     DIE_EMB     DIE_EMB_D   floorplan "die_emb_{cfg}.flp" ;
    die     PIC_PLANE   PIC_PLANE_D floorplan "pic_plane_bridge.flp" ;
    layer   IPOSER_CORE IPOSER_CORE_L ;
"""
    return hdr + MATERIALS + top + channel(q, h_ch, cp, tin) + DIMS + LAYERS + stack + outs(tag)

def main():
    os.makedirs("runs", exist_ok=True)
    f = {}
    for c in CFGS:
        f[f"emb-{c}-std"] = stk(f"emb-{c}-std", c, 4.08e-8, 1.27e-8, 4.18e-12, 300.0, Q_NOM,
            "STANDARD: validated water plate + validated water cavity, 300 K. The capacity baseline.")
    for c in ("E0", "E2", "E4", "H1M2"):
        f[f"emb-{c}-warm"] = stk(f"emb-{c}-warm", c, 4.08e-8 * PG30, 1.27e-8 * PG30, 3.95e-12, 308.0, Q_NOM,
            "WARM: 35 C inlet, PG30 in BOTH loops (h x0.735, Cp 3.95e-12). A real run, not an "
            "offset: the cavity's Cp enters the advection terms. 318 K follows by exact offset.")
    f["emb-E4-std-q2x"] = stk("emb-E4-std-q2x", "E4", 4.08e-8, 1.27e-8, 4.18e-12, 300.0, 2 * Q_NOM,
        "DTM PROBE: cavity flow doubled to 474.4 mL/min (4.01 m/s). LABELLED SENSITIVITY -- this "
        "leaves the anchored velocity, so h is no longer the calibrated value. Use it to size the "
        "advective term for the DTM study, NOT as a feasibility claim. A second Icepak anchor at "
        "this velocity would promote it.")
    for t, txt in f.items():
        open(f"runs/{t}.stk", "w").write(txt)
    print(f"wrote {len(f)} stacks to runs/")
    for t in f: print("  ", t)

if __name__ == "__main__":
    main()
