"""Tests for mesh watertightness (run after STL export)."""

import pytest
import os
import sys
sys.path.insert(0, '..')
from tower_params import *

STL_DIR = os.path.join(os.path.dirname(__file__), '..', 'exports', 'stl')


def get_stl_files():
    """Collect all STL files from exports directory."""
    if not os.path.exists(STL_DIR):
        return []
    return [
        os.path.join(STL_DIR, f)
        for f in os.listdir(STL_DIR)
        if f.endswith('.stl')
    ]


@pytest.mark.skipif(
    not get_stl_files(),
    reason="No STL files exported yet"
)
class TestWatertight:
    """Verify exported meshes are valid for 3D printing."""

    @pytest.fixture(params=get_stl_files() or ['placeholder'],
                    ids=lambda p: os.path.basename(p))
    def mesh(self, request):
        if request.param == 'placeholder':
            pytest.skip("No STL files")
        import trimesh
        return trimesh.load(request.param)

    def test_is_watertight(self, mesh):
        """Mesh must be watertight (no holes)."""
        assert mesh.is_watertight, "Mesh is not watertight"

    def test_is_volume(self, mesh):
        """Mesh must have positive volume."""
        assert mesh.volume > 0, f"Mesh volume is {mesh.volume}"

    def test_no_degenerate_faces(self, mesh):
        """No zero-area faces."""
        import numpy as np
        areas = mesh.area_faces
        assert np.all(areas > 0), "Mesh has degenerate (zero-area) faces"

    def test_consistent_normals(self, mesh):
        """Face normals should be consistently oriented."""
        # trimesh checks this via is_winding_consistent
        assert mesh.is_winding_consistent, "Mesh has inconsistent face normals"
