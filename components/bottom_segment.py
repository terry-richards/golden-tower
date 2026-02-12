"""
Bottom Segment -- Golden Tower
==============================
Variant of the standard segment that includes:
- Same body as standard segment (outer cylinder, hollow interior, floor,
  integrated supply tube, male interlock at top, 3 planting pockets)
- NO female interlock at the bottom
- QD fitting barb protruding downward from the supply tube bore
- Bayonet lugs for reservoir lid attachment
- Reservoir lid ring at the bottom

The bottom segment sits on a reservoir.  The QD barb connects to the pump
hose, the lid ring rests on the reservoir rim, and the bayonet lugs lock
the assembly in place.

Boolean strategy: ALL additive geometry first, then ALL subtractive.
This ensures pocket solids fuse cleanly with the still-solid outer body,
producing a single watertight shell in the exported STL.
"""

import os
import sys
import math

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from tower_params import *
from build123d import *


# ---------------------------------------------------------------------------
# Derived constants (must match segment.py pocket placement exactly)
# ---------------------------------------------------------------------------
POCKET_Z_OFFSET = (
    INTERLOCK_HEIGHT
    + POCKET_DEPTH / 2 * math.cos(math.radians(POCKET_TILT_ANGLE))
    + 2.0
)

# Extended pocket solid length for proper boolean overlap with outer shell
POCKET_SOLID_LENGTH = POCKET_DEPTH + 50.0

# Male interlock outer radius -- as specified for standard segment
MALE_RING_OR = 29.0

# QD barb geometry
QD_BARB_LENGTH = 20.0           # mm, extends downward from z=0
QD_BARB_RIDGE_COUNT = 3         # number of barb ridges
QD_BARB_RIDGE_HEIGHT = 0.8      # mm, radial protrusion of each ridge
QD_BARB_RIDGE_SPACING = 6.0     # mm, center-to-center along barb axis

# Bayonet lug geometry
LUG_WIDTH = 15.0                # mm, tangential (arc-wise) extent
LUG_DEPTH = 5.0                 # mm, radial extent
LUG_HEIGHT = 8.0                # mm, extends downward from z=0

# Reservoir lid ring
LID_RING_HEIGHT = 10.0          # mm, extends downward from z=0
LID_RING_OD = RESERVOIR_LID_OD  # 160 mm
LID_RING_ID = SEGMENT_OUTER_DIAMETER - 2 * WALL_THICKNESS  # 156 mm


def _align_bot():
    """Shorthand: align MIN on Z so the bottom face sits at the location z."""
    return (Align.CENTER, Align.CENTER, Align.MIN)


def build_bottom_segment() -> Part:
    """Build the bottom segment with QD fitting barb, bayonet lugs,
    reservoir lid ring, and standard pockets + male interlock.

    Two-phase boolean (add all, then subtract all) for watertight STL.
    """

    with BuildPart() as bottom:
        # ==================================================================
        # PHASE 1: ALL ADDITIVE GEOMETRY
        # ==================================================================

        # 1. OUTER SHELL  (z = 0 .. SEGMENT_HEIGHT)
        Cylinder(
            radius=SEGMENT_OUTER_RADIUS,
            height=SEGMENT_HEIGHT,
            align=_align_bot(),
        )

        # 2. INTEGRATED SUPPLY TUBE (solid wall, z=0 through male interlock)
        tube_top = SEGMENT_HEIGHT + INTERLOCK_HEIGHT  # 210 mm
        Cylinder(
            radius=SUPPLY_TUBE_OD / 2,
            height=tube_top,
            align=_align_bot(),
        )

        # 3. MALE INTERLOCK RING  (z = SEGMENT_HEIGHT .. + INTERLOCK_HEIGHT)
        with Locations([Pos(0, 0, SEGMENT_HEIGHT)]):
            Cylinder(
                radius=MALE_RING_OR,
                height=INTERLOCK_HEIGHT,
                align=_align_bot(),
            )

        # 4. Alignment key tab on the male ring
        #    Extended 1mm inward to guarantee volumetric overlap with ring
        key_x = MALE_RING_OR + INTERLOCK_KEY_DEPTH / 2 - 0.5
        key_z = SEGMENT_HEIGHT + INTERLOCK_HEIGHT / 2
        with Locations([Pos(key_x, 0, key_z)]):
            Box(
                INTERLOCK_KEY_DEPTH + 1.0,
                INTERLOCK_KEY_WIDTH,
                INTERLOCK_HEIGHT,
                align=(Align.CENTER, Align.CENTER, Align.CENTER),
            )

        # 5. PLANTING POCKETS  (3 pockets at golden-angle spiral positions)
        pocket_locs = []
        for i in range(NODES_PER_SEGMENT):
            angle_deg = i * GOLDEN_ANGLE_DEG
            angle_rad = math.radians(angle_deg)
            z_center = POCKET_Z_OFFSET + i * NODE_VERTICAL_PITCH

            px = POCKET_RADIAL_OFFSET * math.cos(angle_rad)
            py = POCKET_RADIAL_OFFSET * math.sin(angle_rad)

            pocket_loc = Pos(px, py, z_center) * Rot(0, POCKET_TILT_ANGLE, angle_deg)
            pocket_locs.append((pocket_loc, angle_rad))

            # Solid pocket body (cup wall) -- extended for shell overlap
            with Locations([pocket_loc]):
                Cylinder(
                    radius=POCKET_RADIUS + WALL_THICKNESS,
                    height=POCKET_SOLID_LENGTH,
                    align=(Align.CENTER, Align.CENTER, Align.CENTER),
                )

        # 6. QD FITTING BARB (shaft + ridges, extends downward from z=0)
        #    Extend 1mm above z=0 for volumetric overlap with supply tube
        barb_or = QD_FITTING_BARB_OD / 2   # 6.35 mm
        with Locations([Pos(0, 0, -QD_BARB_LENGTH)]):
            Cylinder(
                radius=barb_or,
                height=QD_BARB_LENGTH + 1.0,
                align=_align_bot(),
            )
        # Barb ridges (truncated cones for hose grip)
        for j in range(QD_BARB_RIDGE_COUNT):
            ridge_z = -QD_BARB_LENGTH + 4.0 + j * QD_BARB_RIDGE_SPACING
            with Locations([Pos(0, 0, ridge_z)]):
                Cone(
                    bottom_radius=barb_or + QD_BARB_RIDGE_HEIGHT,
                    top_radius=barb_or,
                    height=2.0,
                    align=_align_bot(),
                )

        # 7. RESERVOIR LID RING  (extends downward from z=0)
        #    Extend 1mm above z=0 for volumetric overlap with outer cylinder
        with Locations([Pos(0, 0, -LID_RING_HEIGHT)]):
            Cylinder(
                radius=LID_RING_OD / 2,
                height=LID_RING_HEIGHT + 1.0,
                align=_align_bot(),
            )

        # 8. BAYONET LUGS  (3 tabs on the lid ring extending downward)
        #    Extend 1mm above z=0 for volumetric overlap with lid ring/body
        for k in range(LID_BAYONET_LUGS):
            lug_angle_deg = k * (360.0 / LID_BAYONET_LUGS)
            lug_angle_rad = math.radians(lug_angle_deg)
            lug_r = LID_RING_OD / 2 - LUG_DEPTH / 2
            lug_x = lug_r * math.cos(lug_angle_rad)
            lug_y = lug_r * math.sin(lug_angle_rad)
            with Locations([Pos(lug_x, lug_y, -LUG_HEIGHT) * Rot(0, 0, lug_angle_deg)]):
                Box(
                    LUG_DEPTH,
                    LUG_WIDTH,
                    LUG_HEIGHT + 1.0,
                    align=_align_bot(),
                )

        # ==================================================================
        # PHASE 2: ALL SUBTRACTIVE GEOMETRY
        # ==================================================================

        # 9. HOLLOW INTERIOR  (leave floor of DRIP_TRAY_DEPTH at the bottom)
        with Locations([Pos(0, 0, DRIP_TRAY_DEPTH)]):
            Cylinder(
                radius=SEGMENT_OUTER_RADIUS - WALL_THICKNESS,
                height=SEGMENT_HEIGHT - DRIP_TRAY_DEPTH,
                align=_align_bot(),
                mode=Mode.SUBTRACT,
            )

        # 10. SUPPLY TUBE BORE (hollow)
        Cylinder(
            radius=SUPPLY_TUBE_ID / 2,
            height=tube_top,
            align=_align_bot(),
            mode=Mode.SUBTRACT,
        )

        # 11. QD BARB BORE (from bottom of barb up through segment floor)
        barb_ir = QD_FITTING_ID / 2         # 4.7625 mm
        with Locations([Pos(0, 0, -QD_BARB_LENGTH)]):
            Cylinder(
                radius=barb_ir,
                height=QD_BARB_LENGTH + DRIP_TRAY_DEPTH + 1.0,
                align=_align_bot(),
                mode=Mode.SUBTRACT,
            )

        # 12. LID RING BORE (hollow center)
        with Locations([Pos(0, 0, -LID_RING_HEIGHT)]):
            Cylinder(
                radius=LID_RING_ID / 2,
                height=LID_RING_HEIGHT,
                align=_align_bot(),
                mode=Mode.SUBTRACT,
            )

        # 13. POCKET BORES  (cup interiors)
        for i in range(NODES_PER_SEGMENT):
            pocket_loc, angle_rad = pocket_locs[i]

            # Bore shifted outward by WALL_THICKNESS/2 along tilted axis
            tilt_rad = math.radians(POCKET_TILT_ANGLE)
            bore_shift = WALL_THICKNESS / 2
            angle_deg = i * GOLDEN_ANGLE_DEG
            ar = math.radians(angle_deg)
            px = POCKET_RADIAL_OFFSET * math.cos(ar)
            py = POCKET_RADIAL_OFFSET * math.sin(ar)
            z_center = POCKET_Z_OFFSET + i * NODE_VERTICAL_PITCH

            dx = bore_shift * math.sin(tilt_rad) * math.cos(ar)
            dy = bore_shift * math.sin(tilt_rad) * math.sin(ar)
            dz = bore_shift * math.cos(tilt_rad)

            bore_loc = (
                Pos(px + dx, py + dy, z_center + dz)
                * Rot(0, POCKET_TILT_ANGLE, angle_deg)
            )
            with Locations([bore_loc]):
                Cylinder(
                    radius=POCKET_RADIUS,
                    height=POCKET_DEPTH - WALL_THICKNESS,
                    align=(Align.CENTER, Align.CENTER, Align.CENTER),
                    mode=Mode.SUBTRACT,
                )

    return bottom.part


if __name__ == "__main__":
    print("Building bottom segment...")
    part = build_bottom_segment()

    # Report geometry
    print(f"  Volume:      {part.volume:.1f} mm^3")
    bb = part.bounding_box()
    print(f"  Bounding box: {bb.min} -> {bb.max}")
    print(f"  Valid solid:  {part.is_valid}")

    # Ensure export directories exist
    base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
    stl_dir = os.path.join(base_dir, "exports", "stl")
    step_dir = os.path.join(base_dir, "exports", "step")
    os.makedirs(stl_dir, exist_ok=True)
    os.makedirs(step_dir, exist_ok=True)

    stl_path = os.path.join(stl_dir, "bottom_segment.stl")
    step_path = os.path.join(step_dir, "bottom_segment.step")

    export_stl(part, stl_path)
    print(f"  Exported STL:  {stl_path}")

    export_step(part, step_path)
    print(f"  Exported STEP: {step_path}")

    print("Done.")
