"""
Standard Segment -- Golden Tower
================================
A single tower segment with 3 planting pockets placed at golden-angle
intervals, SPIRALING UPWARD (each pocket at a different height).

Includes:
- Integrated central supply tube section (not a separate component)
- Integrated drip tray / catch plate for overflow capture
- Male (top) and female (bottom) interlock geometry
- Alignment key (male) and key slot (female) for rotational indexing
- Net cup lip support ledge in each pocket
- Clean outer body between pockets (no accessory notches)

Boolean strategy: ALL additive geometry first, then ALL subtractive.
This ensures pocket solids fuse cleanly with the still-solid outer body,
producing a single watertight shell in the exported STL.
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

# Interlock ring radii
MALE_INTERLOCK_RADIUS = 29.0  # mm -- outer radius of male ring
FEMALE_INTERLOCK_RADIUS = MALE_INTERLOCK_RADIUS + INTERLOCK_CLEARANCE  # 29.3 mm


def build_segment() -> Part:
    """Build a standard tower segment with 3 planting pockets spiraling
    upward, integrated supply tube, drip tray, and interlock.

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
            radius=SUPPLY_TUBE_OD / 2,
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

        # 5. Planting pocket protrusions + lip flanges (3 pockets)
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

            # Solid pocket protrusion (cup exterior) -- extended for overlap
            with Locations([pocket_loc]):
                Cylinder(
                    radius=POCKET_RADIUS + WALL_THICKNESS,
                    height=POCKET_SOLID_LENGTH,
                    align=(Align.CENTER, Align.CENTER, Align.CENTER),
                )

            # Lip support flange at the outer (mouth) end of the pocket
            lip_z_local = POCKET_DEPTH / 2 - NET_CUP_LIP_HEIGHT / 2
            lip_loc = pocket_loc * Pos(0, 0, lip_z_local)
            lip_locs.append(lip_loc)
            with Locations([lip_loc]):
                Cylinder(
                    radius=NET_CUP_LIP_OD / 2 + WALL_THICKNESS,
                    height=NET_CUP_LIP_HEIGHT,
                    align=(Align.CENTER, Align.CENTER, Align.CENTER),
                )

        # ==================================================================
        # PHASE 2: ALL SUBTRACTIVE GEOMETRY
        # ==================================================================

        # 6. Hollow out interior, leaving floor at DRIP_TRAY_DEPTH
        with Locations([Pos(0, 0, DRIP_TRAY_DEPTH)]):
            Cylinder(
                radius=SEGMENT_OUTER_RADIUS - WALL_THICKNESS,
                height=SEGMENT_HEIGHT - DRIP_TRAY_DEPTH,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
                mode=Mode.SUBTRACT,
            )

        # 7. Hollow the supply tube (ID bore, full length)
        Cylinder(
            radius=SUPPLY_TUBE_ID / 2,
            height=tube_height,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
            mode=Mode.SUBTRACT,
        )

        # 8. Female interlock bore at bottom (annular cut)
        with BuildSketch(Plane.XY):
            Circle(radius=FEMALE_INTERLOCK_RADIUS)
            Circle(radius=SUPPLY_TUBE_OD / 2, mode=Mode.SUBTRACT)
        extrude(amount=INTERLOCK_HEIGHT, mode=Mode.SUBTRACT)

        # 9. Matching key slot in the female bore (slightly wider)
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

        # 10. Pocket bores and lip counterbores
        for i in range(NODES_PER_SEGMENT):
            pocket_loc = pocket_locs[i]
            lip_loc = lip_locs[i]

            # Pocket bore (cup interior) -- shifted outward for thick inner wall
            bore_loc = pocket_loc * Pos(0, 0, WALL_THICKNESS / 2)
            with Locations([bore_loc]):
                Cylinder(
                    radius=POCKET_RADIUS,
                    height=POCKET_DEPTH - WALL_THICKNESS,
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

    return seg.part


if __name__ == "__main__":
    segment = build_segment()
    export_stl(segment, os.path.join(os.path.dirname(__file__), '..', 'exports', 'stl', 'segment.stl'))
    export_step(segment, os.path.join(os.path.dirname(__file__), '..', 'exports', 'step', 'segment.step'))
    print(f"Segment volume: {segment.volume:.1f} mm\u00b3")
    bb = segment.bounding_box()
    print(f"Bounding box: {bb.min} to {bb.max}")
