"""
Top Cap — Golden Tower
=======================
Deflects water from the central supply tube outward and down onto the
topmost segment's planting pockets.  Serves as an aesthetic finial.

Geometry (z = 0 is base-plate bottom):
  z = -INTERLOCK_HEIGHT … 0             female interlock socket
  z = 0 … WALL_THICKNESS                base plate disc
  z = WALL_THICKNESS … CAP_HEIGHT       deflector cone (hollow)
  z = CAP_HEIGHT … CAP_HEIGHT + dome_r  finial dome
"""

import os, sys, math

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from tower_params import *
from build123d import *


def build_top_cap() -> Part:
    """Build the top cap / water deflector.

    Returns:
        Part: watertight solid of the complete top cap
    """
    # ── Derived dimensions ──────────────────────────────────────────
    cap_outer_r = SEGMENT_OUTER_RADIUS + CAP_OVERHANG            # 90 mm
    tube_hole_r = SUPPLY_TUBE_ID / 2                              # 14 mm
    socket_inner_r = SUPPLY_TUBE_OD / 2                           # 16 mm
    socket_outer_r = 29.3                                         # receives male ring @ 29.0
    finial_base_r = 5.0                                           # cone apex radius
    finial_dome_r = 8.0                                           # hemisphere radius
    lip_height = 5.0                                              # outer rim height
    cone_base_r = SEGMENT_OUTER_RADIUS                            # 80 mm
    cone_top_r = finial_base_r                                    # 5 mm
    cone_h = CAP_HEIGHT - WALL_THICKNESS                          # 38 mm
    inner_cone_base_r = cone_base_r - WATER_WALL_THICKNESS        # 77.6 mm
    inner_cone_top_r = max(cone_top_r - WATER_WALL_THICKNESS, 0.5)  # 2.6 mm
    n_channels = 6
    # Channel inner edge starts 2mm outside tube bore to avoid coincident faces
    ch_inner_r = tube_hole_r + 2.0                               # 16 mm
    ch_outer_r = cap_outer_r - WALL_THICKNESS                    # 88 mm
    channel_length = ch_outer_r - ch_inner_r                     # 72 mm
    channel_center_r = (ch_inner_r + ch_outer_r) / 2             # 52 mm

    with BuildPart() as cap:
        # ── 1. Base plate ────────────────────────────────────────────
        # Solid disc from r=0 to cap_outer_r, z=0 to WALL_THICKNESS
        Cylinder(
            cap_outer_r,
            WALL_THICKNESS,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )

        # ── 2. Deflector cone (solid outer) ──────────────────────────
        # Base at z=WALL_THICKNESS (r=80), apex at z=CAP_HEIGHT (r=5)
        # Extended 1mm into base plate for volumetric overlap
        with Locations([Pos(0, 0, WALL_THICKNESS - 1.0)]):
            Cone(
                cone_base_r,
                cone_top_r,
                cone_h + 1.0,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )

        # ── 3. Outer lip / rim ──────────────────────────────────────
        # Raised ring at outer edge of base plate to contain water
        with BuildSketch(Plane.XY):
            Circle(cap_outer_r)
            Circle(cap_outer_r - WALL_THICKNESS, mode=Mode.SUBTRACT)
        extrude(amount=lip_height)

        # ── 4. Finial dome ───────────────────────────────────────────
        # Hemisphere sitting on the cone apex for aesthetics
        # Shifted 1mm into cone for volumetric overlap
        with Locations([Pos(0, 0, CAP_HEIGHT - 1.0)]):
            Sphere(
                finial_dome_r,
                arc_size1=0,
                arc_size2=90,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )

        # ── 5. Female interlock socket ───────────────────────────────
        # Below the base plate: two concentric ring walls with an
        # annular groove between them for the male interlock ring.
        # Extended 1mm above z=0 for volumetric overlap with base plate.

        #   Outer socket wall ring (r = socket_outer_r … +WALL_THICKNESS)
        with BuildSketch(Plane.XY.offset(-INTERLOCK_HEIGHT)):
            Circle(socket_outer_r + WALL_THICKNESS)
            Circle(socket_outer_r, mode=Mode.SUBTRACT)
        extrude(amount=INTERLOCK_HEIGHT + 1.0)

        #   Inner tube wall ring (r = tube_hole_r … socket_inner_r)
        with BuildSketch(Plane.XY.offset(-INTERLOCK_HEIGHT)):
            Circle(socket_inner_r)
            Circle(tube_hole_r, mode=Mode.SUBTRACT)
        extrude(amount=INTERLOCK_HEIGHT + 1.0)

        # ── SUBTRACTIONS ─────────────────────────────────────────────

        # ── 6. Hollow out the cone ───────────────────────────────────
        with Locations([Pos(0, 0, WALL_THICKNESS)]):
            Cone(
                inner_cone_base_r,
                inner_cone_top_r,
                cone_h,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
                mode=Mode.SUBTRACT,
            )

        # ── 7. Central tube bore ─────────────────────────────────────
        # Cut through base plate so water can enter the cone interior.
        # Extends from bottom of socket to just above base plate.
        with Locations([Pos(0, 0, -INTERLOCK_HEIGHT)]):
            Cylinder(
                tube_hole_r,
                INTERLOCK_HEIGHT + WALL_THICKNESS + 1,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
                mode=Mode.SUBTRACT,
            )

        # ── 8. Water channels (6 radial grooves) ────────────────────
        # Cut from base plate, avoiding coincident faces at plate-cone boundary.
        # Channels are as deep as the plate minus 0.5mm to keep a thin floor.
        ch_depth = min(CHANNEL_DEPTH, WALL_THICKNESS - 0.5)
        for i in range(n_channels):
            angle_deg = i * (360.0 / n_channels)
            angle_rad = math.radians(angle_deg)
            cx = channel_center_r * math.cos(angle_rad)
            cy = channel_center_r * math.sin(angle_rad)
            with Locations([Pos(cx, cy, WALL_THICKNESS - ch_depth)]):
                Box(
                    channel_length,
                    CHANNEL_WIDTH,
                    ch_depth,
                    rotation=(0, 0, angle_deg),
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                    mode=Mode.SUBTRACT,
                )

    return cap.part


if __name__ == "__main__":
    cap = build_top_cap()
    export_stl(
        cap,
        os.path.join(os.path.dirname(__file__), "..", "exports", "stl", "top_cap.stl"),
    )
    export_step(
        cap,
        os.path.join(os.path.dirname(__file__), "..", "exports", "step", "top_cap.step"),
    )
    print(f"Top cap volume: {cap.volume:.1f} mm\u00b3")
