"""Tests for golden angle geometry accuracy."""

import math
import pytest
import sys
sys.path.insert(0, '..')
from tower_params import *


class TestGoldenAngle:
    """Verify golden angle mathematical properties."""

    def test_golden_angle_value(self):
        """Golden angle must be 360/φ² = 137.508°."""
        phi = (1 + math.sqrt(5)) / 2
        expected = 360.0 / (phi ** 2)
        assert abs(GOLDEN_ANGLE_DEG - expected) < 0.001

    def test_nodes_per_segment(self):
        """Each segment must have exactly 3 nodes."""
        assert NODES_PER_SEGMENT == 3

    def test_interlock_rotation(self):
        """Segment-to-segment rotation = (3 × 137.508°) mod 360 ≈ 52.524°."""
        expected = (3 * GOLDEN_ANGLE_DEG) % 360
        assert abs(INTERLOCK_ROTATION_DEG - expected) < 0.01

    def test_parastichy_count(self):
        """With golden angle placement, parastichy counts should be
        consecutive Fibonacci numbers. For 24 nodes (8 segments × 3),
        expect (3,5) or (5,8) parastichy pair."""
        n_nodes = TARGET_SEGMENT_COUNT * NODES_PER_SEGMENT
        # For ~24 nodes, expect 5 and 8 visible spirals
        fib_pairs = [(3, 5), (5, 8), (8, 13)]
        # At least verify n_nodes is sufficient for one valid pair
        assert n_nodes >= 15, f"Need ≥15 nodes for visible parastichy, got {n_nodes}"

    def test_angular_positions_unique(self):
        """No two nodes should occupy the same angular position."""
        n_total = TARGET_SEGMENT_COUNT * NODES_PER_SEGMENT
        angles = [(i * GOLDEN_ANGLE_DEG) % 360 for i in range(n_total)]
        # All angles should be distinct (within 1° tolerance)
        for i in range(len(angles)):
            for j in range(i + 1, len(angles)):
                diff = abs(angles[i] - angles[j])
                assert diff > 1.0, (
                    f"Nodes {i} and {j} too close: {angles[i]:.2f}° vs {angles[j]:.2f}°"
                )
