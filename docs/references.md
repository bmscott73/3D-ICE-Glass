# Academic and calibration references

The [input index](case-index.md) maps each `.stk` and `.flp` to these sources. An architectural source motivates geometry/power organization; a cooling source supplies a boundary primitive. These links do not make every archived sensitivity case an independent validation.

## Underlying thermal engine

The [EPFL repository](https://github.com/esl-epfl/3d-ice) requests acknowledgement of all four engine publications:

1. K. Zhu, D. Huang, L. Costero, and D. Atienza, **3D-ICE 4.0: Accurate and efficient thermal modeling for 2.5D/3D heterogeneous chiplet systems**, DATE 2026. [Conference paper](https://past.date-conference.com/proceedings-archive/2026/DATA/740.pdf), [author preprint](https://arxiv.org/abs/2512.05823).
2. F. Terraneo, A. Leva, W. Fornaciari, M. Zapater, and D. Atienza, **3D-ICE 3.0: Efficient Nonlinear MPSoC Thermal Simulation With Pluggable Heat Sink Models**, IEEE TCAD, 41(4), 1062–1075, 2022; early access 2021. [DOI](https://doi.org/10.1109/TCAD.2021.3074613).
3. A. Sridhar, A. Vincenzi, D. Atienza, and T. Brunschwiler, **3D-ICE: A Compact Thermal Model for Early-Stage Design of Liquid-Cooled ICs**, IEEE Transactions on Computers, 63(10), 2576–2589, 2014. [DOI](https://doi.org/10.1109/TC.2013.127).
4. A. Sridhar, A. Vincenzi, M. Ruggiero, T. Brunschwiler, and D. Atienza, **3D-ICE: Fast compact transient thermal modeling for 3D ICs with inter-tier liquid cooling**, ICCAD 2010, 463–470. [DOI](https://doi.org/10.1109/ICCAD.2010.5653749).

## Architecture sources

<a id="stratum"></a>
### Stratum memory/logic organization

Y. Pan et al., **Stratum: System-Hardware Co-Design with Tiered Monolithic 3D-Stackable DRAM for Efficient MoE Serving**, MICRO 2025. [Publisher](https://doi.org/10.1145/3725843.3756043), [author preprint](https://arxiv.org/abs/2510.05245). Used for the Mono3D-DRAM/NMP organization and the Stratum-derived glass models; glass-package cooling remains a 3D-ICE-Glass modeling contribution.

<a id="hyflex"></a>
### HyFlexPIM

C. E. Song, P. Bhatnagar, Z. Xia, N. S. Kim, T. Rosing, and M. Kang, **Hybrid SLC-MLC RRAM Mixed-Signal Processing-in-Memory Architecture for Transformer Acceleration via Gradient Redistribution**, ISCA 2025. [Publisher](https://doi.org/10.1145/3695053.3731109), [author preprint](https://arxiv.org/abs/2506.00020). Architecture and duty-weighted spatial power organization for the PIM models.

<a id="panel"></a>
### Panel-scale photonic architecture

T.-C. Hsueh, B. Lin, Z. Chen, and Y. Fainman, **Panel-Scale Reconfigurable Photonic Interconnects for Scalable AI Computation**, IEEE Open Journal of the Solid-State Circuits Society, 2025. [Author preprint](https://arxiv.org/abs/2508.06079), [author research page](https://lin.ucsd.edu/projects). The released 89.8 × 24.4 mm row is a reduced neighborhood containing one prefill node and two decode nodes, not the entire proposed panel.

<a id="glass"></a>
### Glass thermal floorplanning

H. Sharma, J. R. Doppa, U. Y. Ogras, and P. P. Pande, **Designing high-performance and thermally feasible multi-chiplet architectures enabled by non-bendable glass interposer**, ACM TECS, 2025. [DOI](https://doi.org/10.1145/3762644). Background for glass-aware architecture exploration; the individual material and via-fraction choices remain explicit assumptions in this release.

<a id="pic"></a>
### Photonic package-field comparison

S. S. Sofla et al., **Physics-Informed Neural Network Approach for Fast Prediction of Temperature Distribution and Hot Spots in Co-Packaged Optics**, ECTC 2026, 1019–1026. [Author institution record](https://pure.psu.edu/en/publications/physics-informed-neural-network-approach-for-fast-prediction-of-t/), [DOI](https://doi.org/10.1109/ECTC51846.2026.00170). This release uses the reference package field as a range/trend check. It does not reproduce an intra-PIC device-resolved map or assert a universal optical failure temperature.

## Cooling anchors

<a id="ttv"></a>
### Two-phase copper test vehicle

A. Narayanan, Q. Wang, S. Ozguc, and R. W. Bonner III, **Investigation of server-level direct-to-chip two-phase cooling solution for high-power GPUs**, ASME InterPACK 2024, V001T02A009. [DOI](https://doi.org/10.1115/IPACK2024-141261). The imported model checks a copper case/saturation abstraction; the local baseline is the 700 W closure. See its detailed [stack comments](../validation/Baselines/H100/ttv_interpack.stk).

<a id="plate"></a>
### Single-phase H200-class plate specification

ToneCooling, **NVIDIA H200 Liquid Cold Plate GPU + Switch Cooling Board**, manufacturer specification. [Product/specification page](https://tonecooling.com/liquid-cold-plates/nvidia-h200-liquid-cold-plate/). The manuscript accessed this specification on August 24, 2026; its current page was checked on October 11, 2026. Treat the 700 W / 38 °C / below-65 °C condition as a specification check, rather than an independent temperature measurement. The effective 40,800 W/m²K coefficient is the reduced-order input recorded by the research models.

<a id="glass-cooling"></a>
### Glass microchannels and direct-contact copper pillars

J. W. Kim, R. Bhattacharjee, and M. Swaminathan, **Advanced glass package with direct-contact copper pillar and monolithically integrated microfluidic channels for 3D system integration**, ESTC 2026, as cited in the supplied manuscript [21]. The manuscript labels this reference “to appear”; no final public DOI was supplied or verified. The [Cu-pillar inputs](../validation/supplemental/cu-pillar/) are included. The separate 248 W/cm² glass-microchannel test vehicle was not located; package-scale HyFlexPIM models must not be substituted for it.

<a id="silicon-cooling"></a>
### Silicon interlayer cooling

R. Miyazawa, H. Mori, A. Jain, M. Farooq, and T. Hisada, **CFD Simulation Analysis of Inter/Intra Chip Liquid Cooling for 3D Stacked ICs**, ITherm 2023. [DOI](https://doi.org/10.1109/ITHERM55368.2023.10177558). The supplemental directory retains the calibrated-lid model and 19–22 mL/min sensitivity cases. The exact variant used for the manuscript's 86.51 °C checkpoint is not inferred from the target temperature.

<a id="air"></a>
### Secondary forced-air sink

Advanced Thermal Solutions, **ATS-NVP-3275-C5-R0**, datasheet Rev. R9, February 2025. [Manufacturer datasheet](https://www.qats.com/DataSheet/ATS-NVP-3275-C5-R0). The 100 × 87 × 16 mm sink's ducted resistance table motivates the 3/4 m/s boundary cases.

<a id="hausen"></a>
### Correlation comparison

H. Hausen, **Darstellung des Wärmeüberganges in Rohren durch verallgemeinerte Potenzbeziehungen**, VDI Beiheft Verfahrenstechnik, no. 4, 1943, as cited in the supplied manuscript [24]. The [released comparison stacks](../validation/supplemental/coefficient-comparison/) encode the circular, square-duct, and conjugate-CFD closures. Read the exact active coefficients rather than rounded discussion values.

## Property envelope and optical context

The supplied manuscript cites the **Open Compute Project Guidelines for using propylene glycol based heat transfer fluids in single-phase cold plate based liquid cooled racks** (2024), **Dow DOWFROST aqueous-solution physical properties** (2024), Dittus–Boelter (1930), and Padmaraju/Bergman, **Resolving the thermal challenges for silicon microring resonator devices**, *Nanophotonics* (2014). The exact property ratios and transfer restrictions used here are stated in [calibration.md](calibration.md); vendor property curves are not bundled, and the demo's tracking-rate line is a configurable illustrative reference.
