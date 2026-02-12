"""
Standard Segment — Golden Tower
================================
A single tower segment with 3 planting pockets placed at golden-angle
intervals. Includes male (top) and female (bottom) interlock geometry.
"""

# TODO: Architect Agent — implement initial geometry
# See tower_params.py for all dimensions
# See .copilot-instructions.md §2 for full specification

from build123d import *
import math
import sys
sys.path.insert(0, '..')
from tower_params import *


def build_segment() -> Part:
    """Build a standard tower segment with 3 planting pockets."""
    raise NotImplementedError("Architect Agent: implement segment geometry")


def build_pocket() -> Part:
    """Build a single planting pocket (tilted, sized for 2" net cup)."""
    raise NotImplementedError("Architect Agent: implement pocket geometry")


if __name__ == "__main__":
    from ocp_vscode import show
    segment = build_segment()
    show(segment)
