"""
Standard Segment — Golden Tower
================================
A single tower segment with 3 planting pockets placed at golden-angle
intervals, SPIRALING UPWARD (each pocket at a different height).

Includes:
- Integrated central supply tube section (not a separate component)
- Integrated drip tray / catch plate for overflow capture
- Male (top) and female (bottom) interlock geometry
- Clean outer body (no accessory notches)
"""

# TODO: Architect Agent — implement initial geometry
# See tower_params.py for all dimensions
# See .copilot-instructions.md §2 for full specification
# CRITICAL: Each of the 3 pockets must be at a DIFFERENT height within
# the segment, creating a continuous upward spiral.

from build123d import *
import math
import sys
sys.path.insert(0, '..')
from tower_params import *


def build_segment() -> Part:
    """Build a standard tower segment with 3 planting pockets spiraling upward,
    integrated supply tube, drip tray, and interlock."""
    raise NotImplementedError("Architect Agent: implement segment geometry")


def build_pocket(z_offset: float, angle: float) -> Part:
    """Build a single planting pocket at a specific height and angle.

    Args:
        z_offset: Height of pocket center within segment
        angle: Rotation angle (radians) around central axis
    """
    raise NotImplementedError("Architect Agent: implement pocket geometry")


def build_drip_tray() -> Part:
    """Build the integrated drip tray / catch plate."""
    raise NotImplementedError("Architect Agent: implement drip tray")


def build_supply_tube_section() -> Part:
    """Build the integrated supply tube section for this segment."""
    raise NotImplementedError("Architect Agent: implement supply tube section")


if __name__ == "__main__":
    from ocp_vscode import show
    segment = build_segment()
    show(segment)
