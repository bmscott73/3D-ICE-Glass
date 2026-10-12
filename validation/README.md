# Paper validation checkpoints

Each Table II row has its own inputs, reference, expected value, physical observation plane, and numerical tolerance.

```bash
python3 tools/reproduce.py
python3 tools/reproduce.py --recorded
```

The release checks reproduce all ten model values within **0.10 K**, and the eight-scalar aggregate is **2.598%**, rounded to **2.6%**. H200 is a specification check and the photonic row is a range comparison; both are excluded from that aggregate.

| Checkpoint | Model / reference (°C) | Metric | Evidence |
|---|---:|---|---|
| [H100-scale copper TTV](h100-ttv/README.md) | 64.83 / 64.90 | case surface | held-out power prediction |
| [H200-scale plate boundary](h200-plate/README.md) | 61.73 / 65.00 | max plate contact | specification consistency |
| [Stratum-L cold plate](stratum-l/README.md) | 80.97 / 86.00 | die peak | architecture cross-validation |
| [Stratum-S cold plate](stratum-s/README.md) | 55.47 / 55.18 | die peak | matched CFD cross-validation |
| [Glass microchannel + Cu-TGV](glass-microchannel/README.md) | 86.41 / 83.30 | die peak | experimental comparison with assumed HTC |
| [Cu-pillar pin-fin vehicle](cu-pillar/README.md) | 77.63 / 78.60 | die peak | experimental comparison |
| [Silicon interlayer microchannels](silicon-interlayer/README.md) | 86.51 / 84.70 | bottom-die peak | flow-conditioned CFD comparison |
| [HyFlexPIM Cu-pillar pin-fin](hyflex-pinfin/README.md) | 52.17 / 55.80 | die peak | CFD cross-validation |
| [HyFlexPIM microchannel + Cu-TGV](hyflex-microchannel/README.md) | 97.51 / 98.20 | die peak | anchored CFD comparison |
| [Photonic PIC map](photonic/README.md) | 41.84 / 40.00 | PIC peak | range / topology comparison |

[Checked summary CSV](summary.csv) · [Checked release result and hashes](verified-results.json) · [Reference/fit assumptions](../docs/calibration.md) · [Execution and archive notes](../docs/reproduction-status.md).

The numerical tolerance checks repeatability of a released model. It is separate from experimental agreement. The silicon row uses the original 22 mL/min/layer condition; its folder preserves the declared-flow baseline and sweep so that the condition remains explicit. Raw baseline fields and old exploratory inputs are stored in the byte-identical archive release.
