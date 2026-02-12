# Golden Tower — Modular Hydroponic Grow Tower

A 3D-printable, modular hydroponic grow tower where planting pockets
spiral upward following the **golden angle** (137.508°), producing the
same elegant phyllotactic pattern found in sunflowers, pinecones, and
artichokes.

## Quick Start

```bash
cd /home/tmr/src/learn/golden-tower
source venv/bin/activate
python build_tower.py
```

## Architecture

- **Segments** stack and interlock, each rotated 52.524° from the one below
- **3 planting pockets** per segment at golden-angle spacing, **spiraling upward**
  (each pocket at a different height within the segment)
- **Integrated supply tube** built into each segment carries nutrient solution up
- **Top cap** deflects water outward and down through the pocket spiral
- **Integrated drip trays** in each segment catch overflow and route it downward
- **Bottom segment** connects to a pump via standard quick-disconnect
- **Clean outer body** — no accessory notches or grip features between pockets

## Design Philosophy

The golden angle ensures maximum light exposure per plant and even
nutrient distribution. The spiral pattern is not just mathematical —
it's the same strategy plants evolved over millions of years.

## File Structure

| Path | Purpose |
|---|---|
| `tower_params.py` | All parametric dimensions (single source of truth) |
| `build_tower.py` | Main build script — generates all components |
| `components/` | Individual component build123d scripts |
| `tests/` | Automated geometry, print, and assembly tests |
| `exports/stl/` | Exported STL files for printing |
| `exports/step/` | Exported STEP files for CAD interchange |
| `reports/` | Agent review reports per iteration |
| `slicer/profiles/` | Recommended slicer configurations |

## Bill of Materials (per tower)

| Item | Qty | Spec |
|---|---|---|
| Standard Segment (3D printed) | 8 | PETG, ~4hr each |
| Bottom Segment (3D printed) | 1 | PETG, ~5hr |
| Top Cap (3D printed) | 1 | PETG, ~2hr |
| 2" Net Cups | 24 | Standard hydroponic |
| O-rings (AS568-228) | 8 | Inter-segment seals |
| 3/8" Quick-Disconnect | 1 | Garden hose QD |
| Submersible Pump | 1 | 1-4 L/min, 12V or mains |
| Reservoir | 1 | 10-20L bucket with lid |

## Assembly

1. Attach QD fitting to bottom segment
2. Place bottom segment on reservoir lid
3. Stack standard segments, rotating each to lock (supply tube aligns automatically)
4. Place top cap
5. Insert net cups with growing medium
6. Connect pump and fill reservoir

## License

Proprietary — designed by autonomous agent swarm.
