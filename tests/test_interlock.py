"""Tests for interlock mechanism fit and alignment."""

import math
import pytest
import sys
sys.path.insert(0, '..')
from tower_params import *


class TestInterlockGeometry:
    """Verify interlock parametric values are valid."""

    def test_clearance_positive(self):
        """Interlock clearance must be positive."""
        assert INTERLOCK_CLEARANCE > 0

    def test_clearance_reasonable(self):
        """Clearance should be 0.1-0.5mm for FDM printing."""
        assert 0.1 <= INTERLOCK_CLEARANCE <= 0.5, (
            f"Clearance {INTERLOCK_CLEARANCE}mm outside reasonable FDM range"
        )

    def test_engagement_depth(self):
        """Interlock engagement must be at least 5mm for stability."""
        assert INTERLOCK_HEIGHT >= 5.0

    def test_rotation_angle_not_symmetric(self):
        """Interlock rotation must not be a divisor of 360° to prevent
        assembly at wrong angle."""
        rotation = INTERLOCK_ROTATION_DEG
        # Check it's not a clean divisor
        assert 360.0 % rotation > 0.1, (
            f"Rotation {rotation}° is a clean divisor of 360° — "
            "segments could be assembled at wrong angle"
        )

    def test_key_dimensions(self):
        """Key width and depth must be printable."""
        assert INTERLOCK_KEY_WIDTH >= 2 * NOZZLE_DIAMETER
        assert INTERLOCK_KEY_DEPTH >= 2 * LAYER_HEIGHT
