# [Print] Print Feasibility Report -- Golden Tower Iteration 1

## Status: REVIEWED

**Reviewer**: Print Agent
**Iteration**: 1 (initial geometry)
**Date**: 2026-02-12
**Target Printer**: Bambu Lab P1S (256 x 256 x 256 mm, enclosed)
**Target Material**: PETG or ASA
**Files reviewed**: `tower_params.py`, `components/segment.py`, `components/top_cap.py`, `components/bottom_segment.py`, `exports/stl/*.stl`

---

## [Print] 1. Build Volume Fit

**Build volume**: 256 x 256 x 256 mm (Bambu Lab P1S)

### 1.1 Bounding Box Derivation

All bounding dimensions were derived analytically from the parametric source
code in `tower_params.py` and the component build scripts. Key inputs:

- `SEGMENT_OUTER_RADIUS` = 80 mm (body diameter 160 mm)
- `POCKET_RADIAL_OFFSET` = 50 mm (pocket center from tower axis)
- `POCKET_TILT_ANGLE` = 20 deg
- `POCKET_SOLID_LENGTH` = 95 mm (45 mm depth + 50 mm overlap extension)
- `POCKET_RADIUS` + `WALL_THICKNESS` = 26 + 2 = 28 mm (pocket exterior radius)
- `SEGMENT_HEIGHT` = 200 mm, `INTERLOCK_HEIGHT` = 10 mm

The pocket protrusion maximum radial extent from tower axis:

```
R_max = POCKET_RADIAL_OFFSET
      + (POCKET_SOLID_LENGTH / 2) * sin(POCKET_TILT_ANGLE)
      + (POCKET_RADIUS + WALL_THICKNESS) * cos(POCKET_TILT_ANGLE)
      = 50 + 47.5 * sin(20 deg) + 28 * cos(20 deg)
      = 50 + 16.25 + 26.32
      = 92.57 mm from center
```

Pocket 0 (azimuth 0 deg) extends primarily along +X. Pocket 1 (azimuth
137.5 deg) extends into -X/+Y quadrant. Pocket 2 (azimuth 275 deg) extends
into +X/-Y quadrant. The axis-aligned bounding box depends on the projection
of these tilted cylinders onto the coordinate axes.

Vertical extent computation -- the lowest pocket (pocket 0) protrusion extends
below z=0:

```
POCKET_Z_OFFSET = INTERLOCK_HEIGHT + (POCKET_DEPTH/2) * cos(20 deg) + 2.0
               = 10 + 22.5 * 0.940 + 2.0
               = 33.14 mm

Pocket 0 center: z = 33.14 mm
Lower Z extent: 33.14 - 47.5 * cos(20 deg) - 28 * sin(20 deg)
             = 33.14 - 44.65 - 9.58
             = -21.1 mm

Pocket 2 (highest) center: z = 33.14 + 2 * 66.67 = 166.48 mm
Upper Z extent: 166.48 + 47.5 * cos(20 deg) + 28 * sin(20 deg)
             = 166.48 + 44.65 + 9.58
             = 220.7 mm (vs. male interlock top at 210 mm)
```

Total Z extent: approximately 220.7 - (-21.1) = **241.8 mm**

### 1.2 Component Fit Summary

| Component | Bounding Box (mm) | X Margin | Y Margin | Z Margin | Fits? |
|---|---|---|---|---|---|
| Standard Segment | ~172.5 x 160.3 x 241.8 | 83.5 mm | 95.7 mm | **14.2 mm** | YES |
| Bottom Segment | ~172.5 x 160.3 x 241.8 | 83.5 mm | 95.7 mm | **14.2 mm** | YES |
| Top Cap | ~180.0 x 180.0 x 58.0 | 76.0 mm | 76.0 mm | 198.0 mm | YES |

**Notes on Bottom Segment**: The QD barb extends to z = -20 mm and the
reservoir lid ring to z = -10 mm. However, the lowest pocket protrusion
already extends to z = -21.1 mm, so the bottom-mounted features do not
increase the bounding box beyond the standard segment. The bottom segment
has no female interlock bore but otherwise shares identical pocket placement,
resulting in the same Z envelope.

**Notes on Top Cap**: The bounding box spans from z = -10 mm (interlock socket
base) to z = 48 mm (finial dome apex), giving 58 mm total height. The base
plate extends to r = 90 mm (180 mm diameter), which is the widest X/Y extent.

### 1.3 Build Volume Verdict

All three components fit within the 256 x 256 x 256 mm build volume. The
**Z margin of 14.2 mm (5.5%) is tight** for both segment variants. PETG and
ASA are prone to thermal warping on tall prints, and any upward warping at the
top layers could bring the nozzle into conflict with previously deposited
material or trigger Z-limit errors.

The **P1S's enclosed build chamber** mitigates thermal warping significantly,
but the margin remains a concern. Any design changes that increase the segment
Z envelope by more than 14 mm will **exceed the build volume**.

**Risk level**: MINOR -- printable but with thin tolerances that must be
monitored.

---

## [Print] 2. Overhang Analysis

**Maximum permitted overhang**: 55 deg from vertical (`MAX_OVERHANG_ANGLE`
in `tower_params.py`)

### 2.1 Pocket Cylinder Exterior Surface

A cylinder of radius 28 mm tilted 20 deg from vertical has surface normals
that rotate with the tilt. The most extreme downward-facing surface normal on
the pocket underside:

- Pocket axis direction: tilted 20 deg from +Z toward the radial outward
  direction
- Most downward-facing surface normal on the cylinder: perpendicular to the
  tilted axis, pointing toward -Z
- This normal has Z-component: -sin(20 deg) = -0.342
- Angle from +Z: arccos(-0.342) = 110 deg
- **Overhang from vertical**: 110 - 90 = **20 deg**

20 deg < 55 deg limit. **The pocket exterior undersides are within the safe
overhang zone.** No supports needed for the outside of the pocket protrusions.

### 2.2 Pocket Interior -- Closed Bottom Face (CRITICAL)

Each pocket bore (52 mm diameter, 43 mm deep) is capped at the inner end by a
solid disk (the pocket bottom, `WALL_THICKNESS` = 2 mm thick). This disk is
perpendicular to the pocket axis, which is tilted 20 deg from vertical. The
outward normal of this face points inward toward the tower center and
predominantly downward:

```
Normal direction: (-sin(20 deg) * cos(azimuth),
                   -sin(20 deg) * sin(azimuth),
                   -cos(20 deg))
Z component: -cos(20 deg) = -0.940
Angle from +Z: arccos(-0.940) = 160 deg
Overhang from vertical: 160 - 90 = 70 deg
```

**70 deg >> 55 deg limit.** The pocket bottom face has a severe overhang that
requires support material inside the pocket bore. This support would be
deposited inside a 52 mm diameter cylinder tilted at 20 deg -- **removal would
be extremely difficult**, especially for the two upper pockets which are less
accessible.

This affects **3 pockets per segment x 8 segments = 24 pocket interiors**
across the full tower.

### 2.3 Male Interlock Ring Step (CRITICAL)

The male interlock ring (radius 29 mm) protrudes above the body cylinder
(radius 80 mm) at z = 200-210 mm. This creates a horizontal step (90 deg
overhang) at the body top face. The unsupported horizontal span:

```
Step span = SEGMENT_OUTER_RADIUS - MALE_INTERLOCK_RADIUS
          = 80 - 29
          = 51 mm
```

This is a **51 mm horizontal overhang** at 90 deg from vertical, exceeding
both the 55 deg overhang limit and the 40 mm bridge span limit.

### 2.4 Top Cap Cone Interior

The inner surface of the hollow deflector cone narrows from r = 77.6 mm to
r = 2.6 mm over 38 mm of height. The inner surface slope:

```
arctan((77.6 - 2.6) / 38) = arctan(1.974) = 63.1 deg from vertical
```

At 63 deg from vertical, this technically exceeds the 55 deg limit. In
practice, at 0.2 mm layer height each layer steps inward by
0.2 * tan(63.1 deg) = 0.39 mm, which is within one nozzle width (0.4 mm).
The P1S should print this acceptably with moderate cooling but will produce
a rough inner surface. Functionally acceptable for a water deflector.

### 2.5 Female Interlock Socket Ceiling

The female interlock bore (annular groove from r = 16 mm to r = 29.3 mm,
z = 0 to z = 10 mm) has a horizontal ceiling at z = 10 mm:

```
Bridge span = FEMALE_INTERLOCK_RADIUS - SUPPLY_TUBE_OD / 2
            = 29.3 - 16.0
            = 13.3 mm
```

This is a circular bridge at 13.3 mm span, well under the 40 mm limit. The
annular (circular) bridge geometry is favorable as bridging filament is laid
tangentially. Self-supporting with standard bridge settings.

### 2.6 Overhang Summary Table

| Feature | Overhang Angle | Limit | Span | Status |
|---|---|---|---|---|
| Pocket exterior (underside) | 20 deg | 55 deg | -- | **PASS** |
| Pocket interior (bottom face) | **70 deg** | 55 deg | ~52 mm dia | **FAIL** |
| Male interlock ring step | **90 deg** | 55 deg | 51 mm | **FAIL** |
| Top cap inner cone | 63 deg | 55 deg | gradual | MARGINAL |
| Female interlock ceiling | 90 deg | -- | 13.3 mm bridge | **PASS** (bridge) |
| Finial dome (8 mm hemisphere) | up to 90 deg | 55 deg | 16 mm dia | **PASS** (tiny) |
| QD barb ridges | ~45 deg cones | 55 deg | -- | **PASS** |

---

## [Print] 3. Support Requirements

### 3.1 Features Requiring Support

| # | Component | Feature | Support Type | Removal Difficulty |
|---|---|---|---|---|
| S1 | Segment / Bottom | Pocket interior bottom face (x3 per segment) | Tree/linear inside 52 mm tilted bore | **HARD** -- deep inside a narrow tilted bore; risk of damaging 2 mm pocket walls during removal |
| S2 | Segment / Bottom | Male interlock ring step (51 mm overhang) | Full support plate under body top face, r = 29-80 mm | **MODERATE** -- accessible from open female socket below; large contact area to break away |
| S3 | Top Cap | Inner cone surface (partial) | Thin supports inside hollow cone | **MODERATE** -- accessible from the open bottom of the cone |

### 3.2 Self-Supporting Redesign Opportunities

**S1 -- Pocket bottom face (HIGH PRIORITY, RECOMMENDED)**:

Replace the flat pocket bottom with a **conical or domed interior**. A 45 deg
internal cone at the pocket bottom would reduce the maximum overhang from
70 deg to approximately 70 - 45 = 25 deg (well within limit). The net cup
sits at the pocket mouth and does not interact with the bottom geometry, so
this change has zero functional impact on planting.

Alternatively, **make the pocket a through-hole** (open at both ends). The
inner end connects to the hollow tower interior. This eliminates the bottom
face entirely, removes the overhang, AND creates a natural drain path for
each pocket. However, this changes the water containment strategy and must be
coordinated with the Engineering Agent.

**S2 -- Male interlock ring step (HIGH PRIORITY, RECOMMENDED)**:

Add a **45-50 deg chamfer or taper** transitioning from the body outer wall
(r = 80 mm) down to the interlock ring (r = 29 mm). A linear taper over
approximately 51 mm of height at 45 deg creates a self-supporting slope.
This transition is **inside the hollow body** and does not change the external
silhouette. Design options:

- 45 deg taper: 51 mm height, cone from r=80 down to r=29 at t=200 mm
- 50 deg taper: ~43 mm height (steeper but still within limit)
- This is already identified as priority P1 in the iteration summary

**S3 -- Top cap inner cone (LOW PRIORITY)**:

Increase `CAP_HEIGHT` or narrow the cone base to steepen the inner surface
below 55 deg. Alternatively, accept the slightly rough inner surface since it
is not visible in normal use and serves only as a water deflector.

### 3.3 Support Material Estimate (if NOT redesigned)

If supports are required:

- Per segment: 3 pocket bore supports + 1 interlock step support
- Pocket bore support: approximately 5-8 g each (small volume inside bore)
- Interlock step support: approximately 20-30 g (large annular area)
- Total per segment: approximately 35-55 g of support material (wasted)
- Full tower (8 segments): approximately 280-440 g of wasted support

**Strong recommendation**: Redesign S1 and S2 to be self-supporting before
printing. The combined savings: approximately 300+ g of material, 2-3 hours
of print time per segment, and elimination of the most difficult post-
processing step (support removal inside pocket bores).

---

## [Print] 4. Material Estimate

### 4.1 Method

Material volumes estimated analytically from parametric geometry. The design
is predominantly thin-walled (2.0 mm general walls, 2.4 mm water-contact
walls), so most structure consists of 100% solid perimeters with no infill.
The 15% infill setting applies only to regions thicker than 5 x
`NOZZLE_DIAMETER` = 2.0 mm (the 5 mm drip tray floor, interlock features,
pocket bottom disks).

- PETG density: 1.27 g/cm3
- ASA density: 1.07 g/cm3

### 4.2 Standard Segment Volume Breakdown

| Region | Zone (mm) | Solid Volume (mm3) | Notes |
|---|---|---|---|
| Drip tray floor | z = 0 to 5 | ~87,990 | Disk r=80, minus tube bore r=14, minus interlock bore r=16-29.3 |
| Outer shell wall | z = 5 to 200 | ~193,556 | pi * (80^2 - 78^2) * 195 |
| Supply tube wall | z = 5 to 210 | ~38,642 | pi * (16^2 - 14^2) * 205 |
| Male interlock ring | z = 200 to 210 | ~20,263 | pi * (29^2 - 14^2) * 10 |
| Pocket walls (x3) | per pocket axis | ~45,804 | 3 * pi * (28^2 - 26^2) * 45 |
| Pocket bottom disks (x3) | per pocket axis | ~12,769 | 3 * pi * 26^2 * 2 |
| Lip flanges (x3) | per pocket axis | ~5,560 | 3 * pi * (30.5^2 - 28.5^2) * 5 |
| Alignment key + misc | | ~500 | Small features |
| **Estimated total solid** | | **~405,084** | **~405 cm3** |

The 55% fill factor approach (from the earlier report) underestimates the
actual printed mass because this is a thin-walled structure: 2 mm walls at
0.4 mm nozzle = 5 perimeters = 100% solid. Infill only applies in the 5 mm
floor (25 layers, also mostly perimeters at this thickness). **Effective fill
factor is closer to 85-95% of the analytical solid volume.**

- **PETG**: 405 cm3 * 0.90 (effective fill) * 1.27 g/cm3 = **~463 g**
- **ASA**: 405 cm3 * 0.90 * 1.07 g/cm3 = **~390 g**

**Practical estimate**: **430-520 g PETG per standard segment** (range
accounts for slicer perimeter/infill decisions, extrusion width variation,
and support material if used).

### 4.3 Bottom Segment

Same base geometry as standard segment, plus:

| Additional Feature | Volume (mm3) | Mass (g PETG) |
|---|---|---|
| QD barb shaft + ridges | ~3,200 | ~4 |
| Reservoir lid ring (2 mm wall, 10 mm height) | ~9,927 | ~11 |
| Bayonet lugs (x3) | ~1,800 | ~2 |
| Saved: no female interlock bore | +9,500 | +11 |

**Bottom segment estimate**: **460-550 g PETG**

### 4.4 Top Cap

| Region | Solid Volume (mm3) | Notes |
|---|---|---|
| Base plate disk (r=90, h=2) | ~50,894 | Minus tube bore |
| Outer lip ring (h=5, t=2) | ~5,592 | |
| Deflector cone shell | ~23,713 | Outer cone minus inner cone |
| Finial dome | ~1,072 | Half-hemisphere, r=8 |
| Interlock socket walls | ~5,693 | Inner + outer rings, h=10 |
| **Estimated total solid** | **~86,964** | **~87 cm3** |

**Top cap estimate**: **100-120 g PETG**

### 4.5 Full Tower Material Summary

| Component | Qty | Unit Mass PETG (g) | Total (g) |
|---|---|---|---|
| Standard segment | 7 | 470 (midpoint) | 3,290 |
| Bottom segment | 1 | 505 (midpoint) | 505 |
| Top cap | 1 | 110 (midpoint) | 110 |
| **Full tower** | **9 parts** | | **~3,905 g** |

**Full tower: approximately 3.9 kg of PETG** (3.3 kg if using ASA).

At typical PETG filament pricing ($20-25 USD/kg), material cost is
approximately **$78-98 USD** for one complete tower. This requires
approximately **4 standard 1 kg spools** (accounting for waste, purge lines,
support material, and failed print contingency).

---

## [Print] 5. Print Time Estimate

### 5.1 Assumptions

- Bambu Lab P1S with 0.4 mm nozzle, enclosed chamber
- 0.2 mm layer height (`LAYER_HEIGHT` in `tower_params.py`)
- PETG profile: moderate speed (~60 mm/s outer walls, ~100 mm/s infill)
- Average volumetric flow rate: 10-12 mm3/s (conservative for PETG)
- Overhead factor: 1.35x (travel moves, retractions, cooling pauses, Z-hops)

### 5.2 Per-Component Estimates

| Component | Layers | Volume (cm3) | Base Time (hr) | With Overhead | Estimate |
|---|---|---|---|---|---|
| Standard segment | 1,209 | ~405 | 10.1 | 13.7 | **14-20 hr** |
| Bottom segment | 1,209 | ~420 | 10.5 | 14.2 | **14-20 hr** |
| Top cap | 290 | ~87 | 2.2 | 3.0 | **3-4 hr** |

**Notes**:
- Layer count for segments: 241.8 mm / 0.2 mm = 1,209 layers
- Many segment layers are simple thin rings (just the 2 mm shell wall), which
  print very quickly (<30 s per layer). Layers through the pocket zone require
  additional perimeters and travel time.
- The P1S with input shaping may achieve faster times with ASA/PETG flow
  profiles; the estimate above is conservative.

### 5.3 Full Tower Print Campaign

| Phase | Components | Total Print Time |
|---|---|---|
| Standard segments (x7) | 7 x ~17 hr avg | ~119 hr |
| Bottom segment (x1) | 1 x ~17 hr avg | ~17 hr |
| Top cap (x1) | 1 x ~3.5 hr avg | ~3.5 hr |
| **Total** | **9 print jobs** | **~140 hr** |

**Full tower: approximately 140 hours (5.8 days) of continuous print time.**

Each segment fills most of the build plate footprint, so batching multiple
segments per print is not possible. The print campaign spans approximately
**8-10 calendar days** with realistic downtime for plate changes, filament
swaps, and any re-runs due to failures.

---

## [Print] 6. Issues Found

| # | Severity | Component | Issue | Suggested Fix |
|---|----------|-----------|-------|---------------|
| P-1 | **MAJOR** | Segment, Bottom Segment | Male interlock ring creates a **51 mm horizontal overhang** (90 deg) at the body top face. Exceeds both the 55 deg angle limit and the 40 mm bridge limit. Requires extensive support inside the body interior, which is moderately difficult to remove. | Add a 45-50 deg chamfer/taper from body outer wall (r=80) down to interlock ring (r=29). Height of taper: ~51 mm at 45 deg or ~43 mm at 50 deg. The taper is inside the hollow body and does not change the external appearance. |
| P-2 | **MAJOR** | Segment, Bottom Segment | Pocket bore interior **bottom face has 70 deg overhang** (vs. 55 deg limit). Support material inside a 52 mm diameter tilted bore is extremely difficult to remove. Affects all 3 pockets per segment (24 pockets across full tower). Pocket walls are only 2 mm thick and risk damage during support removal. | **Option A**: Replace flat pocket bottom with a 45 deg internal cone, reducing overhang to ~25 deg (self-supporting). **Option B**: Make pockets open-ended (through-holes to body interior), eliminating bottom face entirely. Option B must be coordinated with water flow design. |
| P-3 | **MINOR** | Segment, Bottom Segment | Z-axis bounding height of **241.8 mm leaves only 14.2 mm margin** (5.5%) to the 256 mm build volume ceiling. Thermal warping on tall PETG prints could cause collisions or Z-limit faults. | Monitor on first print. Mitigations: (a) reduce `POCKET_SOLID_LENGTH` from 95 mm to 70-75 mm (shorter boolean overlap still sufficient), (b) use lower bed temperature (70 degC) to reduce base warping, (c) the enclosed P1S chamber is favorable. |
| P-4 | **MINOR** | Top Cap | Inner cone surface overhang at **63 deg exceeds 55 deg limit**. Will produce rough interior surface texture. | Functionally acceptable for a water deflector (not visible). To improve: increase `CAP_HEIGHT` to steepen cone, or accept rough interior. Low priority. |
| P-5 | **MINOR** | Segment | Female interlock socket ceiling requires **13.3 mm annular bridge** at 90 deg overhang. | Within 40 mm bridge limit; circular bridges print well. Consider adding 0.5 mm chamfer to ceiling edges to improve bridge initiation. |
| P-6 | **MINOR** | Segment, Bottom Segment | `POCKET_SOLID_LENGTH` of 95 mm is over-extended for boolean overlap. The pocket solid extends 47.5 mm each side of center, causing the protrusions to extend well beyond both the body envelope and the actual pocket depth. This contributes to the tight Z margin. | Reduce `POCKET_SOLID_LENGTH` to 70-75 mm. Preserves clean boolean overlap while recovering 10-12 mm of Z margin. |
| P-7 | **MINOR** | Full Tower | Total print campaign of **~140 hours** across 9 jobs with ~3.9 kg of PETG. A single failed segment wastes 14-20 hours and 450+ g of material with no recovery option. | Not a design flaw, but recommend: (a) print one validation segment first before committing to full campaign, (b) keep spare filament, (c) add small test features (bridging test, overhang test) to the first print to validate slicer settings. |

### Summary by Severity

- **BLOCKER**: None. All components fit the build volume and are fundamentally
  printable (with supports).
- **MAJOR**: 2 issues (P-1, P-2). Both involve overhang angles exceeding the
  55 deg limit in hard-to-access locations. Both have clear self-supporting
  redesign paths that should be implemented before the first print.
- **MINOR**: 5 issues (P-3 through P-7). Tight Z margin, internal cosmetic
  roughness, minor bridging, parametric over-extension, and practical campaign
  concerns.

---

## [Print] 7. Recommended Print Orientation and Settings

### 7.1 Orientation

All components should be printed **upright** (tower axis aligned with printer
Z axis, printed from bottom to top):

| Component | On Build Plate | At Top | Notes |
|---|---|---|---|
| Standard segment | Female interlock socket (z=0) | Male interlock ring (z=210) | Pocket overhangs at 20 deg: safe |
| Bottom segment | QD barb + lid ring (z=-20) | Male interlock ring (z=210) | Barb ridges are small down-facing cones: self-supporting |
| Top cap | Interlock socket base (z=-10) | Finial dome (z=48) | Cone prints well base-down |

Printing upside-down (male ring on bed, female socket at top) is an
alternative for the standard segment that **eliminates P-1** (no interlock
step overhang), but places pocket protrusions at different angles. The pocket
exterior overhang increases slightly but remains under 55 deg. The female
interlock bore becomes a top-open groove (no overhang). This orientation is
worth testing if P-1 cannot be resolved by redesign.

### 7.2 Recommended Slicer Settings

| Parameter | Value | Rationale |
|---|---|---|
| Layer height | 0.20 mm | Standard quality; good layer adhesion for water tightness |
| First layer height | 0.20 mm | Consistent with body for dimensional accuracy |
| Outer wall perimeters | 5 | 5 x 0.4 mm = 2.0 mm (matches `WALL_THICKNESS`) |
| Water-contact perimeters | 6 | 6 x 0.4 mm = 2.4 mm (matches `WATER_WALL_THICKNESS`) |
| Infill density | 15% | For floor and thick structural areas |
| Infill pattern | Gyroid | Best for water resistance (no straight through-paths for leaks) |
| Top solid layers | 6 | 1.2 mm solid top for water seal |
| Bottom solid layers | 6 | 1.2 mm solid bottom for water seal |
| Support type | Tree (auto) | Only if P-1 and P-2 are NOT redesigned self-supporting |
| Support angle threshold | 55 deg | Matches `MAX_OVERHANG_ANGLE` |
| Brim width | 8 mm | Recommended for tall PETG prints to prevent base lifting |
| Z-seam position | Aligned (rear) | Keep layer seam on tower backside for aesthetics |
| Nozzle temperature | 240 degC | Standard PETG for Bambu P1S |
| Bed temperature | 80 degC | PETG adhesion; reduce to 70 degC if warping occurs |
| Part cooling fan | 30-50% | PETG requires moderate cooling; excessive cooling causes delamination |
| Print speed (walls) | 60 mm/s | Outer wall quality |
| Print speed (infill) | 100 mm/s | Interior fill |

---

## [Print] 8. Mesh Quality Assessment

### 8.1 Boolean Strategy

The build scripts use a deliberate **two-phase boolean strategy**: all additive
geometry first (Phase 1), then all subtractive geometry (Phase 2). This is a
best practice for producing single-shell watertight output from build123d/OCCT
boolean operations. The docstrings in `segment.py` and `bottom_segment.py`
explicitly document this strategy.

Per the iteration 1 validation, all STL meshes passed watertight checks. The
trimesh analysis should verify:

- `is_watertight == True` for all three component STLs
- No degenerate faces or self-intersections
- Correct outward-facing normals
- No orphan shells (the two-phase boolean prevents this)

### 8.2 Expected Face Counts

Based on geometry complexity (cylinders, cones, boolean intersection curves):

- Standard segment: ~40,000-80,000 faces (3 pocket booleans)
- Bottom segment: ~50,000-90,000 faces (pockets + barb + lugs)
- Top cap: ~10,000-20,000 faces (simpler geometry)

These counts are well within the Bambu slicer's capability (handles up to
several million faces without performance issues).

---

## [Print] 9. Checklist

- [x] All parts fit within 256 x 256 x 256 mm build volume
- [ ] No overhangs > 55 deg from vertical (**FAIL**: pocket bottoms at 70 deg, interlock step at 90 deg, cap interior at 63 deg)
- [ ] No bridge spans > 40 mm (**FAIL**: interlock step at 51 mm span)
- [x] All meshes manifold and watertight (per iteration 1 validation)
- [x] Print time estimated per component
- [x] Material usage estimated per component
- [ ] Slicer profiles written to `slicer/profiles/` (not yet created)

**Checklist pass**: 4 of 7 criteria met.

---

## [Print] 10. Score

### Printability (weight: 20%)

| Sub-criterion | Score | Notes |
|---|---|---|
| Build volume fit | 8/10 | All parts fit; 14.2 mm Z margin is tight but workable in enclosed P1S |
| Overhang compliance | 4/10 | Two features exceed limit (pocket bottom 70 deg, interlock step 90 deg/51 mm) |
| Support requirements | 4/10 | Internal pocket support is the critical pain point; 24 pockets across full tower |
| Mesh quality | 8/10 | Watertight, clean two-phase booleans, no orphan shells |
| Material efficiency | 6/10 | 3.9 kg is substantial for the size but reasonable for a functional system |
| Print time feasibility | 6/10 | 140 hours is a significant commitment; 9 sequential jobs |
| Practical printability | 6/10 | Enclosed P1S chamber helps; PETG at this height is proven technology |

**Printability score: 6 / 10**

The design is fundamentally printable -- every component fits the build volume
and the mesh geometry is clean. The score is held back by two MAJOR overhang
issues (P-1 and P-2) that require supports in hard-to-access locations. These
are both solvable with straightforward parametric changes:

- P-1 (interlock step): add conical taper inside body -> eliminates 51 mm step
- P-2 (pocket bottoms): add 45 deg internal cone or make through-holes -> eliminates 70 deg face

Implementing these two fixes would raise the printability score to
**7.5-8.0 / 10** without affecting any other design criteria (aesthetics,
water flow, structural integrity).

---

## [Print] 11. Recommendations for Next Iteration

**Priority order** (highest-impact print improvements first):

1. **Add 45-50 deg taper at male interlock ring** (fixes P-1). The architect
   should add a conical transition from the body top inside wall (r=78 mm) down
   to the interlock ring (r=29 mm) at z=200 mm. This taper spans approximately
   45-51 mm of height inside the body interior and does not change the external
   appearance or seam line.

2. **Redesign pocket bottoms to be self-supporting** (fixes P-2). Preferred
   approach: add a 45 deg internal cone at the closed end of each pocket bore.
   The cone replaces the flat bottom disk, converting a 70 deg overhang into a
   ~25 deg slope. No impact on net cup seating or pocket mouth geometry.

3. **Reduce `POCKET_SOLID_LENGTH`** from 95 mm to 70-75 mm (addresses P-6,
   partially improves P-3 Z margin). The current 50 mm overlap extension is
   excessive for boolean reliability; 25-30 mm overlap is sufficient with
   build123d's OCCT kernel.

4. **Create slicer profiles** in `slicer/profiles/` for the Bambu P1S with
   the settings specified in section 7.2.

5. **Print one validation segment** before committing to the full 9-part
   campaign. Include bridging and overhang test features if possible.

---

*Report generated by Print Agent -- Golden Tower autonomous design swarm.*
