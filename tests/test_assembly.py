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

    def test_nodes_spiral_upward(self):
        """Each successive node within a segment must be at a greater height.
        The pockets must NOT be in a flat ring."""
        for i in range(NODES_PER_SEGMENT):
            z_i = i * NODE_VERTICAL_PITCH
            if i > 0:
                z_prev = (i - 1) * NODE_VERTICAL_PITCH
                assert z_i > z_prev, (
                    f"Node {i} (z={z_i}) not above node {i-1} (z={z_prev})"
                )

    def test_segment_height_width_ratio(self):
        """Segment height:width ratio must be >= 1.0 for pleasing upward sweep."""
        ratio = SEGMENT_HEIGHT / SEGMENT_OUTER_DIAMETER
        assert ratio >= 1.0, (
            f"H:W ratio {ratio:.2f} < 1.0 — pockets won't spiral upward visually"
        )

    def test_continuous_helix_across_segments(self):
        """The last pocket in segment N and the first pocket in segment N+1
        must maintain the golden-angle offset and consistent vertical pitch."""
        import math
        # Last node of segment 0
        last_z_seg0 = (NODES_PER_SEGMENT - 1) * NODE_VERTICAL_PITCH
        last_angle_seg0 = (NODES_PER_SEGMENT - 1) * GOLDEN_ANGLE_DEG
        # First node of segment 1
        first_z_seg1 = SEGMENT_HEIGHT  # segment 1 starts at top of segment 0
        first_angle_seg1 = NODES_PER_SEGMENT * GOLDEN_ANGLE_DEG
        # Angular step should be golden angle
        angular_step = first_angle_seg1 - last_angle_seg0
        assert abs(angular_step - GOLDEN_ANGLE_DEG) < 0.01, (
            f"Cross-segment angular step {angular_step:.3f}° != golden angle"
        )
        # Vertical step should equal NODE_VERTICAL_PITCH
        vertical_step = first_z_seg1 - last_z_seg0
        assert abs(vertical_step - NODE_VERTICAL_PITCH) < 0.01, (
            f"Cross-segment vertical step {vertical_step:.1f}mm != pitch {NODE_VERTICAL_PITCH:.1f}mm"
        )
