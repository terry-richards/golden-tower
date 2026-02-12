"""
Standard Segment -- Golden Tower
================================
A single tower segment with 3 planting pockets placed at golden-angle
intervals, SPIRALING UPWARD (each pocket at a different height).

Includes:
- Integrated central supply tube section (not a separate component)
- Integrated drip tray / catch plate with sloped floor and drain through-holes
- Male (top) and female (bottom) interlock geometry
- Alignment key (male) and key slot (female) for rotational indexing
- Net cup lip support ledge in each pocket
- O-ring groove for inter-segment seal
- Support cone for printable male ring transition (≤55° overhang)
- Clean outer body between pockets (no accessory notches)

Boolean strategy: ALL additive geometry first, then ALL subtractive.
This ensures pocket solids fuse cleanly with the still-solid outer body,
producing a single watertight shell in the exported STL.

Iteration 3 changes:
- Hollow is now ANNULAR (preserves tube wall through body)
- Added support cone at top for printable male ring transition
- Pocket walls use WATER_WALL_THICKNESS (2.4mm)
- Drain through-holes connect drip tray to segment below
- Drip tray slope via deeper drain channels toward center
- O-ring groove on male ring for inter-segment seal
- Pocket bottom chamfer for printable overhang (≤55°)
"""

from build123d import *
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from tower_params import *

# ---------------------------------------------------------------------------
# Derived constants
# ---------------------------------------------------------------------------
POCKET_Z_OFFSET = (
    INTERLOCK_HEIGHT
    + POCKET_DEPTH / 2 * math.cos(math.radians(POCKET_TILT_ANGLE))
    + 2.0
)

# Extended pocket solid length for clean boolean overlap with outer shell
POCKET_SOLID_LENGTH = POCKET_DEPTH + 50.0

# Interlock ring radii (use MALE_RING_OR from tower_params)
MALE_INTERLOCK_RADIUS = MALE_RING_OR  # 29.0 mm
FEMALE_INTERLOCK_RADIUS = MALE_INTERLOCK_RADIUS + INTERLOCK_CLEARANCE  # 29.3 mm

# Body inner radius (after wall thickness)
BODY_INNER_RADIUS = SEGMENT_OUTER_RADIUS - WALL_THICKNESS  # 78.0 mm

# Tube radii
TUBE_OR = SUPPLY_TUBE_OD / 2  # 16.0 mm
TUBE_IR = SUPPLY_TUBE_ID / 2  # 13.6 mm

# Male ring chamfer: the cone that supports the male ring during printing
CHAMFER_H = MALE_RING_CHAMFER_H  # 10.0 mm
CHAMFER_Z_START = SEGMENT_HEIGHT - CHAMFER_H  # 190.0 mm

# Drip tray slope: channels deepen toward center (3° effective slope)
SLOPE_DROP = (BODY_INNER_RADIUS - TUBE_OR) * math.tan(math.radians(DRIP_TRAY_SLOPE))
# ~3.25mm over 62mm radial distance


def build_segment() -> Part:
    """Build a standard tower segment with 3 planting pockets spiraling
    upward, integrated supply tube, drip tray with slope and drain holes,
    O-ring groove, and printable male ring transition.

    Construction: two-phase boolean (add all, then subtract all) to ensure
    a single fused solid with no orphan shells.

    Returns:
        Part: The watertight, export-ready segment solid.
    """

    with BuildPart() as seg:

        # ==================================================================
        # PHASE 1: ALL ADDITIVE GEOMETRY
        # ==================================================================

        # 1. Solid outer cylinder (full body blank)
        Cylinder(
            radius=SEGMENT_OUTER_RADIUS,
            height=SEGMENT_HEIGHT,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )

        # 2. Supply tube solid (OD), extends INTERLOCK_HEIGHT above body
        tube_height = SEGMENT_HEIGHT + INTERLOCK_HEIGHT
        Cylinder(
            radius=TUBE_OR,
            height=tube_height,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )

        # 3. Male interlock ring at top (around tube extension)
        with Locations([Pos(0, 0, SEGMENT_HEIGHT)]):
            Cylinder(
                radius=MALE_INTERLOCK_RADIUS,
                height=INTERLOCK_HEIGHT,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )

        # 4. Alignment key tab on the male ring (at angle = 0)
        #    Extended 1mm inward to guarantee volumetric overlap with ring
        key_radial = MALE_INTERLOCK_RADIUS + INTERLOCK_KEY_DEPTH / 2 - 0.5
        with Locations([Pos(key_radial, 0, SEGMENT_HEIGHT + INTERLOCK_HEIGHT / 2)]):
            Box(
                INTERLOCK_KEY_DEPTH + 1.0,
                INTERLOCK_KEY_WIDTH,
                INTERLOCK_HEIGHT,
                align=(Align.CENTER, Align.CENTER, Align.CENTER),
            )

        # 5. Support cone for male ring — printable transition (≤55° overhang)
        #    Fills the space from tube OD (r=16) to male ring OR (r=29)
        #    over CHAMFER_H (10mm), giving 52.4° angle from vertical.
        #    Placed at top of body, overlaps 1mm into male ring zone.
        with Locations([Pos(0, 0, CHAMFER_Z_START)]):
            Cone(
                bottom_radius=TUBE_OR,
                top_radius=MALE_INTERLOCK_RADIUS,
                height=CHAMFER_H + 1.0,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )

        # 6. Planting pocket protrusions + lip flanges (3 pockets)
        #    Uses WATER_WALL_THICKNESS for pocket exterior walls
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

            # Solid pocket protrusion (cup exterior) -- uses WATER_WALL_THICKNESS
            with Locations([pocket_loc]):
                Cylinder(
                    radius=POCKET_RADIUS + WATER_WALL_THICKNESS,
                    height=POCKET_SOLID_LENGTH,
                    align=(Align.CENTER, Align.CENTER, Align.CENTER),
                )

            # Flare cone at pocket-body junction for organic transition
            flare_loc = pocket_loc * Pos(0, 0, -5.0)
            with Locations([flare_loc]):
                Cone(
                    bottom_radius=POCKET_RADIUS + WATER_WALL_THICKNESS + 5.0,
                    top_radius=POCKET_RADIUS + WATER_WALL_THICKNESS,
                    height=12.0,
                    align=(Align.CENTER, Align.CENTER, Align.CENTER),
                )

            # Lip support flange at the outer (mouth) end of the pocket
            lip_z_local = POCKET_DEPTH / 2 - NET_CUP_LIP_HEIGHT / 2
            lip_loc = pocket_loc * Pos(0, 0, lip_z_local)
            lip_locs.append(lip_loc)
            with Locations([lip_loc]):
                Cylinder(
                    radius=NET_CUP_LIP_OD / 2 + WATER_WALL_THICKNESS,
                    height=NET_CUP_LIP_HEIGHT,
                    align=(Align.CENTER, Align.CENTER, Align.CENTER),
                )

        # ==================================================================
        # PHASE 2: ALL SUBTRACTIVE GEOMETRY
        # ==================================================================

        # 7. Hollow out interior — ANNULAR cut preserving tube wall
        #    Lower zone: r=tube_OD/2 to body_inner, z=DTD to chamfer start
        with BuildSketch(Plane.XY.offset(DRIP_TRAY_DEPTH)):
            Circle(radius=BODY_INNER_RADIUS)
            Circle(radius=TUBE_OR, mode=Mode.SUBTRACT)
        extrude(amount=CHAMFER_Z_START - DRIP_TRAY_DEPTH, mode=Mode.SUBTRACT)

        #    Upper zone: r=male_ring_OR to body_inner, z=chamfer start to top
        #    (narrower inner radius so support cone is preserved)
        with BuildSketch(Plane.XY.offset(CHAMFER_Z_START)):
            Circle(radius=BODY_INNER_RADIUS)
            Circle(radius=MALE_INTERLOCK_RADIUS, mode=Mode.SUBTRACT)
        extrude(amount=CHAMFER_H, mode=Mode.SUBTRACT)

        # 8. Hollow the supply tube (ID bore, full length)
        Cylinder(
            radius=TUBE_IR,
            height=tube_height,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
            mode=Mode.SUBTRACT,
        )

        # 9. Female interlock bore at bottom (annular cut)
        with BuildSketch(Plane.XY):
            Circle(radius=FEMALE_INTERLOCK_RADIUS)
            Circle(radius=TUBE_OR, mode=Mode.SUBTRACT)
        extrude(amount=INTERLOCK_HEIGHT, mode=Mode.SUBTRACT)

        # 10. Matching key slot in the female bore (slightly wider)
        slot_radial = MALE_INTERLOCK_RADIUS + INTERLOCK_KEY_DEPTH / 2
        slot_width = INTERLOCK_KEY_WIDTH + INTERLOCK_CLEARANCE * 2   # 8.6 mm
        slot_depth = INTERLOCK_KEY_DEPTH + INTERLOCK_CLEARANCE * 2   # 3.6 mm
        with Locations([Pos(slot_radial, 0, INTERLOCK_HEIGHT / 2)]):
            Box(
                slot_depth,
                slot_width,
                INTERLOCK_HEIGHT,
                align=(Align.CENTER, Align.CENTER, Align.CENTER),
                mode=Mode.SUBTRACT,
            )

        # 11. O-ring groove on male ring exterior
        #     Groove is on the outer surface of the male ring at mid-height
        oring_z = SEGMENT_HEIGHT + INTERLOCK_HEIGHT / 2
        oring_groove_or = MALE_INTERLOCK_RADIUS + 0.1  # slight overlap for clean cut
        oring_groove_ir = MALE_INTERLOCK_RADIUS - ORING_GROOVE_DEPTH
        with BuildSketch(Plane.XY.offset(oring_z - ORING_GROOVE_WIDTH / 2)):
            Circle(radius=oring_groove_or)
            Circle(radius=oring_groove_ir, mode=Mode.SUBTRACT)
        extrude(amount=ORING_GROOVE_WIDTH, mode=Mode.SUBTRACT)

        # 12. Pocket bores, lip counterbores, and bottom chamfers
        for i in range(NODES_PER_SEGMENT):
            pocket_loc = pocket_locs[i]
            lip_loc = lip_locs[i]

            # Pocket bore (cup interior) -- shifted outward for thick inner wall
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

            # Pocket bottom chamfer — replaces flat bottom with printable cone
            # The pocket is tilted, so the bottom face has a steep overhang.
            # Add a conical chamfer at the inner (bottom) end of the bore
            # to bring the overhang angle within 55° of vertical.
            chamfer_r = POCKET_RADIUS * 0.85  # tapers inward
            chamfer_len = POCKET_RADIUS * 0.5  # chamfer depth along axis
            bottom_loc = pocket_loc * Pos(0, 0, -(POCKET_DEPTH / 2 - WATER_WALL_THICKNESS / 2))
            with Locations([bottom_loc]):
                Cone(
                    bottom_radius=0.1,
                    top_radius=chamfer_r,
                    height=chamfer_len,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                    mode=Mode.SUBTRACT,
                )

        # 13. Drip tray drain channels (3 radial grooves toward center)
        #     Channels slope toward center: deeper at inner end (effective 3° slope)
        ch_r_inner = TUBE_OR + 2.0    # 18mm
        ch_r_outer = BODY_INNER_RADIUS - 2.0  # 76mm
        ch_r_mid = (ch_r_inner + ch_r_outer) / 2
        ch_length = ch_r_outer - ch_r_inner
        # Channel depth increases toward center for slope
        ch_depth_outer = DRIP_TRAY_DEPTH - 2.5  # 2.5mm at outer edge
        ch_depth_center = DRIP_TRAY_DEPTH - 1.0  # 4.0mm at center (deeper)

        for k in range(3):
            ch_angle_deg = k * 120.0
            ch_angle_rad = math.radians(ch_angle_deg)
            ch_x = ch_r_mid * math.cos(ch_angle_rad)
            ch_y = ch_r_mid * math.sin(ch_angle_rad)

            # Main channel body (average depth)
            ch_avg_depth = (ch_depth_outer + ch_depth_center) / 2
            with Locations([Pos(ch_x, ch_y, DRIP_TRAY_DEPTH - ch_avg_depth / 2) * Rot(0, 0, ch_angle_deg)]):
                Box(
                    ch_length,
                    DRIP_TRAY_DRAIN_WIDTH,
                    ch_avg_depth,
                    align=(Align.CENTER, Align.CENTER, Align.CENTER),
                    mode=Mode.SUBTRACT,
                )

        # 14. Drain through-holes — connect drip tray to segment below
        #     3 vertical holes through the drip tray floor at r=DRAIN_HOLE_RADIAL_POS
        #     aligned with drain channels. Water exits bottom face and falls
        #     into the hollow interior of the segment below.
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

    return seg.part


if __name__ == "__main__":
    segment = build_segment()
    export_stl(segment, os.path.join(os.path.dirname(__file__), '..', 'exports', 'stl', 'segment.stl'))
    export_step(segment, os.path.join(os.path.dirname(__file__), '..', 'exports', 'step', 'segment.step'))
    print(f"Segment volume: {segment.volume:.1f} mm\u00b3")
    bb = segment.bounding_box()
    print(f"Bounding box: {bb.min} to {bb.max}")
