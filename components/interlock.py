"""
Interlock Mechanism — Golden Tower
===================================
Male/female interlock geometry that:
- Enforces correct 52.524° rotational offset between segments
- Cannot be assembled at the wrong angle
- Provides splash-resistant seal (O-ring groove)

Note: For iteration 1, interlock geometry is built inline within
segment.py. This module provides standalone interlock parts for
testing and visualization purposes.
"""

from build123d import *
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from tower_params import *

# Interlock ring dimensions
MALE_RING_OR = 29.0  # mm
FEMALE_BORE_IR = SUPPLY_TUBE_OD / 2  # 16 mm
FEMALE_BORE_OR = MALE_RING_OR + INTERLOCK_CLEARANCE  # 29.3 mm


def build_male_interlock() -> Part:
    """Build the male (top) interlock ring for a segment."""
    with BuildPart() as male:
        # Main ring
        Cylinder(
            radius=MALE_RING_OR,
            height=INTERLOCK_HEIGHT,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )
        # Supply tube wall
        Cylinder(
            radius=SUPPLY_TUBE_OD / 2,
            height=INTERLOCK_HEIGHT,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )
        # Central tube bore
        Cylinder(
            radius=SUPPLY_TUBE_ID / 2,
            height=INTERLOCK_HEIGHT,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
            mode=Mode.SUBTRACT,
        )
        # Alignment key tab
        key_x = MALE_RING_OR + INTERLOCK_KEY_DEPTH / 2
        with Locations([Pos(key_x, 0, INTERLOCK_HEIGHT / 2)]):
            Box(
                INTERLOCK_KEY_DEPTH,
                INTERLOCK_KEY_WIDTH,
                INTERLOCK_HEIGHT,
                align=(Align.CENTER, Align.CENTER, Align.CENTER),
            )
    return male.part


def build_female_interlock() -> Part:
    """Build the female (bottom) interlock socket for a segment."""
    with BuildPart() as female:
        # Outer ring representing the segment base material
        Cylinder(
            radius=FEMALE_BORE_OR + WALL_THICKNESS * 3,
            height=INTERLOCK_HEIGHT,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )
        # Bore for male ring
        with BuildSketch(Plane.XY):
            Circle(radius=FEMALE_BORE_OR)
            Circle(radius=FEMALE_BORE_IR, mode=Mode.SUBTRACT)
        extrude(amount=INTERLOCK_HEIGHT, mode=Mode.SUBTRACT)
        # Key slot
        slot_x = FEMALE_BORE_OR + INTERLOCK_KEY_DEPTH / 2
        with Locations([Pos(slot_x, 0, INTERLOCK_HEIGHT / 2)]):
            Box(
                INTERLOCK_KEY_DEPTH + INTERLOCK_CLEARANCE * 2,
                INTERLOCK_KEY_WIDTH + INTERLOCK_CLEARANCE * 2,
                INTERLOCK_HEIGHT,
                align=(Align.CENTER, Align.CENTER, Align.CENTER),
                mode=Mode.SUBTRACT,
            )
        # Central tube bore
        Cylinder(
            radius=SUPPLY_TUBE_ID / 2,
            height=INTERLOCK_HEIGHT,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
            mode=Mode.SUBTRACT,
        )
    return female.part


if __name__ == "__main__":
    male = build_male_interlock()
    female = build_female_interlock()
    stl_dir = os.path.join(os.path.dirname(__file__), '..', 'exports', 'stl')
    export_stl(male, os.path.join(stl_dir, 'interlock_male.stl'))
    export_stl(female, os.path.join(stl_dir, 'interlock_female.stl'))
    print(f"Male interlock volume: {male.volume:.1f} mm³")
    print(f"Female interlock volume: {female.volume:.1f} mm³")
