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

Iteration 3 changes (mirrored from segment.py):
- Hollow is ANNULAR (preserves tube wall through body)
- Support cone at top for printable male ring transition
- Pocket walls use WATER_WALL_THICKNESS (2.4mm)
- Drain through-holes connect drip tray to segment below
- Drip tray slope via deeper drain channels toward center
- O-ring groove on male ring for inter-segment seal
- Pocket bottom chamfer for printable overhang

Boolean strategy: ALL additive geometry first, then ALL subtractive.
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

# Interlock ring radii
MALE_INTERLOCK_RADIUS = MALE_RING_OR  # 29.0 mm
FEMALE_INTERLOCK_RADIUS = MALE_INTERLOCK_RADIUS + INTERLOCK_CLEARANCE  # 29.3 mm

# Body inner radius
BODY_INNER_RADIUS = SEGMENT_OUTER_RADIUS - WALL_THICKNESS  # 78.0 mm

# Tube radii
TUBE_OR = SUPPLY_TUBE_OD / 2  # 16.0 mm
TUBE_IR = SUPPLY_TUBE_ID / 2  # 13.6 mm

# Male ring chamfer
CHAMFER_H = MALE_RING_CHAMFER_H  # 10.0 mm
CHAMFER_Z_START = SEGMENT_HEIGHT - CHAMFER_H  # 190.0 mm

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
            radius=TUBE_OR,
            height=tube_top,
            align=_align_bot(),
        )

        # 3. MALE INTERLOCK RING  (z = SEGMENT_HEIGHT .. + INTERLOCK_HEIGHT)
        with Locations([Pos(0, 0, SEGMENT_HEIGHT)]):
            Cylinder(
                radius=MALE_INTERLOCK_RADIUS,
                height=INTERLOCK_HEIGHT,
                align=_align_bot(),
            )

        # 4. Alignment key tab on the male ring
        key_x = MALE_INTERLOCK_RADIUS + INTERLOCK_KEY_DEPTH / 2 - 0.5
        key_z = SEGMENT_HEIGHT + INTERLOCK_HEIGHT / 2
        with Locations([Pos(key_x, 0, key_z)]):
            Box(
                INTERLOCK_KEY_DEPTH + 1.0,
                INTERLOCK_KEY_WIDTH,
                INTERLOCK_HEIGHT,
                align=(Align.CENTER, Align.CENTER, Align.CENTER),
            )

        # 5. Support cone for male ring — printable transition
        with Locations([Pos(0, 0, CHAMFER_Z_START)]):
            Cone(
                bottom_radius=TUBE_OR,
                top_radius=MALE_INTERLOCK_RADIUS,
                height=CHAMFER_H + 1.0,
                align=_align_bot(),
            )

        # 6. PLANTING POCKETS (3 pockets at golden-angle spiral positions)
        pocket_locs = []
        lip_locs = []
        for i in range(NODES_PER_SEGMENT):
            angle_deg = i * GOLDEN_ANGLE_DEG
            angle_rad = math.radians(angle_deg)
            z_center = POCKET_Z_OFFSET + i * NODE_VERTICAL_PITCH

            px = POCKET_RADIAL_OFFSET * math.cos(angle_rad)
            py = POCKET_RADIAL_OFFSET * math.sin(angle_rad)

            pocket_loc = Pos(px, py, z_center) * Rot(0, POCKET_TILT_ANGLE, angle_deg)
            pocket_locs.append(pocket_loc)

            # Solid pocket body — WATER_WALL_THICKNESS
            with Locations([pocket_loc]):
                Cylinder(
                    radius=POCKET_RADIUS + WATER_WALL_THICKNESS,
                    height=POCKET_SOLID_LENGTH,
                    align=(Align.CENTER, Align.CENTER, Align.CENTER),
                )

            # Flare cone at pocket-body junction
            flare_loc = pocket_loc * Pos(0, 0, -5.0)
            with Locations([flare_loc]):
                Cone(
                    bottom_radius=POCKET_RADIUS + WATER_WALL_THICKNESS + 5.0,
                    top_radius=POCKET_RADIUS + WATER_WALL_THICKNESS,
                    height=12.0,
                    align=(Align.CENTER, Align.CENTER, Align.CENTER),
                )

            # Lip support flange at the outer end of the pocket
            lip_z_local = POCKET_DEPTH / 2 - NET_CUP_LIP_HEIGHT / 2
            lip_loc = pocket_loc * Pos(0, 0, lip_z_local)
            lip_locs.append(lip_loc)
            with Locations([lip_loc]):
                Cylinder(
                    radius=NET_CUP_LIP_OD / 2 + WATER_WALL_THICKNESS,
                    height=NET_CUP_LIP_HEIGHT,
                    align=(Align.CENTER, Align.CENTER, Align.CENTER),
                )

        # 7. QD FITTING BARB (shaft + ridges, extends downward from z=0)
        barb_or = QD_FITTING_BARB_OD / 2   # 6.35 mm
        with Locations([Pos(0, 0, -QD_BARB_LENGTH)]):
            Cylinder(
                radius=barb_or,
                height=QD_BARB_LENGTH + 1.0,
                align=_align_bot(),
            )
        # Barb ridges
        for j in range(QD_BARB_RIDGE_COUNT):
            ridge_z = -QD_BARB_LENGTH + 4.0 + j * QD_BARB_RIDGE_SPACING
            with Locations([Pos(0, 0, ridge_z)]):
                Cone(
                    bottom_radius=barb_or + QD_BARB_RIDGE_HEIGHT,
                    top_radius=barb_or,
                    height=2.0,
                    align=_align_bot(),
                )

        # 8. RESERVOIR LID RING  (extends downward from z=0)
        with Locations([Pos(0, 0, -LID_RING_HEIGHT)]):
            Cylinder(
                radius=LID_RING_OD / 2,
                height=LID_RING_HEIGHT + 1.0,
                align=_align_bot(),
            )

        # 9. BAYONET LUGS
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

        # 10. HOLLOW INTERIOR — annular cut preserving tube wall
        #     Lower zone: r=tube_OD/2 to body_inner, z=DTD to chamfer start
        with BuildSketch(Plane.XY.offset(DRIP_TRAY_DEPTH)):
            Circle(radius=BODY_INNER_RADIUS)
            Circle(radius=TUBE_OR, mode=Mode.SUBTRACT)
        extrude(amount=CHAMFER_Z_START - DRIP_TRAY_DEPTH, mode=Mode.SUBTRACT)

        #     Upper zone: r=male_ring_OR to body_inner, z=chamfer start to top
        with BuildSketch(Plane.XY.offset(CHAMFER_Z_START)):
            Circle(radius=BODY_INNER_RADIUS)
            Circle(radius=MALE_INTERLOCK_RADIUS, mode=Mode.SUBTRACT)
        extrude(amount=CHAMFER_H, mode=Mode.SUBTRACT)

        # 11. SUPPLY TUBE BORE (hollow)
        Cylinder(
            radius=TUBE_IR,
            height=tube_top,
            align=_align_bot(),
            mode=Mode.SUBTRACT,
        )

        # 12. QD BARB BORE (from bottom of barb up through segment floor)
        barb_ir = QD_FITTING_ID / 2         # 4.7625 mm
        with Locations([Pos(0, 0, -QD_BARB_LENGTH)]):
            Cylinder(
                radius=barb_ir,
                height=QD_BARB_LENGTH + DRIP_TRAY_DEPTH + 1.0,
                align=_align_bot(),
                mode=Mode.SUBTRACT,
            )

        # 13. LID RING BORE (hollow center)
        with Locations([Pos(0, 0, -LID_RING_HEIGHT)]):
            Cylinder(
                radius=LID_RING_ID / 2,
                height=LID_RING_HEIGHT,
                align=_align_bot(),
                mode=Mode.SUBTRACT,
            )

        # 14. O-ring groove on male ring exterior
        oring_z = SEGMENT_HEIGHT + INTERLOCK_HEIGHT / 2
        oring_groove_or = MALE_INTERLOCK_RADIUS + 0.1
        oring_groove_ir = MALE_INTERLOCK_RADIUS - ORING_GROOVE_DEPTH
        with BuildSketch(Plane.XY.offset(oring_z - ORING_GROOVE_WIDTH / 2)):
            Circle(radius=oring_groove_or)
            Circle(radius=oring_groove_ir, mode=Mode.SUBTRACT)
        extrude(amount=ORING_GROOVE_WIDTH, mode=Mode.SUBTRACT)

        # 15. POCKET BORES, lip counterbores, and bottom chamfers
        for i in range(NODES_PER_SEGMENT):
            pocket_loc = pocket_locs[i]
            lip_loc = lip_locs[i]

            # Pocket bore
            bore_loc = pocket_loc * Pos(0, 0, WATER_WALL_THICKNESS / 2)
            with Locations([bore_loc]):
                Cylinder(
                    radius=POCKET_RADIUS,
                    height=POCKET_DEPTH - WATER_WALL_THICKNESS,
                    align=(Align.CENTER, Align.CENTER, Align.CENTER),
                    mode=Mode.SUBTRACT,
                )

            # Net cup lip counterbore
            with Locations([lip_loc]):
                Cylinder(
                    radius=NET_CUP_LIP_OD / 2,
                    height=NET_CUP_LIP_HEIGHT,
                    align=(Align.CENTER, Align.CENTER, Align.CENTER),
                    mode=Mode.SUBTRACT,
                )

            # Pocket bottom chamfer
            chamfer_r = POCKET_RADIUS * 0.85
            chamfer_len = POCKET_RADIUS * 0.5
            bottom_loc = pocket_loc * Pos(0, 0, -(POCKET_DEPTH / 2 - WATER_WALL_THICKNESS / 2))
            with Locations([bottom_loc]):
                Cone(
                    bottom_radius=0.1,
                    top_radius=chamfer_r,
                    height=chamfer_len,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                    mode=Mode.SUBTRACT,
                )

        # 16. Drip tray drain channels (3 radial grooves toward center)
        ch_r_inner = TUBE_OR + 2.0
        ch_r_outer = BODY_INNER_RADIUS - 2.0
        ch_r_mid = (ch_r_inner + ch_r_outer) / 2
        ch_length = ch_r_outer - ch_r_inner
        ch_avg_depth = (DRIP_TRAY_DEPTH - 2.5 + DRIP_TRAY_DEPTH - 1.0) / 2

        for k in range(3):
            ch_angle_deg = k * 120.0
            ch_angle_rad = math.radians(ch_angle_deg)
            ch_x = ch_r_mid * math.cos(ch_angle_rad)
            ch_y = ch_r_mid * math.sin(ch_angle_rad)

            with Locations([Pos(ch_x, ch_y, DRIP_TRAY_DEPTH - ch_avg_depth / 2) * Rot(0, 0, ch_angle_deg)]):
                Box(
                    ch_length,
                    DRIP_TRAY_DRAIN_WIDTH,
                    ch_avg_depth,
                    align=(Align.CENTER, Align.CENTER, Align.CENTER),
                    mode=Mode.SUBTRACT,
                )

        # 17. Drain through-holes
        for k in range(3):
            dh_angle_deg = k * 120.0
            dh_angle_rad = math.radians(dh_angle_deg)
            dh_x = DRAIN_HOLE_RADIAL_POS * math.cos(dh_angle_rad)
            dh_y = DRAIN_HOLE_RADIAL_POS * math.sin(dh_angle_rad)

            with Locations([Pos(dh_x, dh_y, 0)]):
                Cylinder(
                    radius=DRAIN_HOLE_DIAMETER / 2,
                    height=DRIP_TRAY_DEPTH + 1.0,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                    mode=Mode.SUBTRACT,
                )

    return bottom.part


if __name__ == "__main__":
    print("Building bottom segment...")
    part = build_bottom_segment()

    print(f"  Volume:      {part.volume:.1f} mm^3")
    bb = part.bounding_box()
    print(f"  Bounding box: {bb.min} -> {bb.max}")
    print(f"  Valid solid:  {part.is_valid}")

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
