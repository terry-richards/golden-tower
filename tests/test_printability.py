"""Tests for 3D printing feasibility."""

import pytest
import sys
sys.path.insert(0, '..')
from tower_params import *


class TestBuildVolume:
    """Verify all components fit within printer build volume."""

    def test_segment_fits_xy(self):
        """Segment outer diameter must fit within build plate."""
        assert SEGMENT_OUTER_DIAMETER <= min(BUILD_VOLUME_X, BUILD_VOLUME_Y), (
            f"Segment OD {SEGMENT_OUTER_DIAMETER}mm exceeds build plate "
            f"{min(BUILD_VOLUME_X, BUILD_VOLUME_Y)}mm"
        )

    def test_segment_fits_z(self):
        """Segment height + interlock must fit within build height."""
        total_z = SEGMENT_HEIGHT + INTERLOCK_HEIGHT
        assert total_z <= BUILD_VOLUME_Z, (
            f"Segment total height {total_z}mm exceeds build height {BUILD_VOLUME_Z}mm"
        )

    def test_cap_fits_xy(self):
        """Top cap with overhang must fit within build plate."""
        cap_od = SEGMENT_OUTER_DIAMETER + 2 * CAP_OVERHANG
        assert cap_od <= min(BUILD_VOLUME_X, BUILD_VOLUME_Y), (
            f"Cap OD {cap_od}mm exceeds build plate"
        )


class TestWallThickness:
    """Verify minimum wall thickness requirements."""

    def test_min_wall_thickness(self):
        """General wall thickness ≥ 1.6mm (2 perimeters × 0.4mm nozzle × 2)."""
        min_wall = MIN_PERIMETERS * NOZZLE_DIAMETER * 2
        assert WALL_THICKNESS >= min_wall, (
            f"Wall thickness {WALL_THICKNESS}mm < minimum {min_wall}mm"
        )

    def test_water_wall_thickness(self):
        """Water-contact walls ≥ 2.4mm (3 perimeters)."""
        min_water_wall = WATER_PERIMETERS * NOZZLE_DIAMETER * 2
        assert WATER_WALL_THICKNESS >= min_water_wall - 0.001, (
            f"Water wall {WATER_WALL_THICKNESS}mm < minimum {min_water_wall}mm"
        )

    def test_central_tube_wall(self):
        """Central tube wall must meet minimum thickness."""
        assert CENTRAL_TUBE_WALL >= WALL_THICKNESS, (
            f"Tube wall {CENTRAL_TUBE_WALL}mm < min {WALL_THICKNESS}mm"
        )


class TestParametricConsistency:
    """Verify parametric values are self-consistent."""

    def test_pocket_fits_in_segment(self):
        """Pocket must not protrude beyond segment outer radius."""
        pocket_outer_edge = POCKET_RADIAL_OFFSET + POCKET_RADIUS
        assert pocket_outer_edge <= SEGMENT_OUTER_RADIUS, (
            f"Pocket extends to {pocket_outer_edge}mm, segment radius is {SEGMENT_OUTER_RADIUS}mm"
        )

    def test_pocket_clears_tube(self):
        """Pocket inner edge must clear the central tube."""
        pocket_inner_edge = POCKET_RADIAL_OFFSET - POCKET_RADIUS
        tube_clearance = CENTRAL_TUBE_OD / 2 + WALL_THICKNESS
        assert pocket_inner_edge >= tube_clearance, (
            f"Pocket inner edge at {pocket_inner_edge}mm, "
            f"tube clearance needs {tube_clearance}mm"
        )

    def test_net_cup_fits_pocket(self):
        """Net cup must fit inside pocket with clearance."""
        assert POCKET_DIAMETER >= NET_CUP_OD, (
            f"Pocket {POCKET_DIAMETER}mm < net cup {NET_CUP_OD}mm"
        )
