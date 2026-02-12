"""Tests for full tower assembly validation."""

import math
import pytest
import sys
sys.path.insert(0, '..')
from tower_params import *


class TestAssembly:
    """Verify full tower assembly dimensions."""

    def test_total_height_reasonable(self):
        """Assembled tower should be 1-2 meters tall."""
        assert 500 <= TOTAL_TOWER_HEIGHT <= 2000, (
            f"Tower height {TOTAL_TOWER_HEIGHT}mm outside 500-2000mm range"
        )

    def test_segment_count(self):
        """Target segment count should be 6-10."""
        assert 6 <= TARGET_SEGMENT_COUNT <= 10

    def test_total_pockets(self):
        """Total planting positions should be useful (18-30)."""
        total = TARGET_SEGMENT_COUNT * NODES_PER_SEGMENT
        assert 18 <= total <= 30, f"Total pockets: {total}"

    def test_pocket_angular_separation(self):
        """Adjacent pockets (by height) should have enough angular
        separation that plants don't crowd each other."""
        # Minimum angular separation between vertically adjacent pockets
        min_angular_sep = 30.0  # degrees
        assert GOLDEN_ANGLE_DEG > min_angular_sep

    def test_vertical_pocket_spacing(self):
        """Vertical distance between pockets should allow plant growth."""
        min_vertical = 25.0  # mm between pocket centers
        assert NODE_VERTICAL_PITCH >= min_vertical, (
            f"Vertical pitch {NODE_VERTICAL_PITCH}mm < minimum {min_vertical}mm"
        )
