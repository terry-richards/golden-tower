"""
Build Tower — Golden Tower
============================
Main build script that generates all tower components, exports STL/STEP
files, and validates the geometry.

Usage:
    source venv/bin/activate
    python build_tower.py
"""

import os
import sys
import time

# Ensure project root is on path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'components'))

from build123d import export_stl, export_step
from tower_params import *

# Output directories
STL_DIR = os.path.join(PROJECT_ROOT, 'exports', 'stl')
STEP_DIR = os.path.join(PROJECT_ROOT, 'exports', 'step')

os.makedirs(STL_DIR, exist_ok=True)
os.makedirs(STEP_DIR, exist_ok=True)


def build_and_export_all():
    """Build all tower components and export STL/STEP files."""
    results = {}

    # ── Standard Segment ──
    print("Building standard segment...")
    t0 = time.time()
    from components.segment import build_segment
    segment = build_segment()
    dt = time.time() - t0
    export_stl(segment, os.path.join(STL_DIR, 'segment.stl'))
    export_step(segment, os.path.join(STEP_DIR, 'segment.step'))
    bb = segment.bounding_box()
    print(f"  Volume: {segment.volume:.1f} mm³")
    print(f"  Bbox: {bb.min} to {bb.max}")
    print(f"  Build time: {dt:.1f}s")
    results['segment'] = segment

    # ── Top Cap ──
    print("\nBuilding top cap...")
    t0 = time.time()
    from components.top_cap import build_top_cap
    top_cap = build_top_cap()
    dt = time.time() - t0
    export_stl(top_cap, os.path.join(STL_DIR, 'top_cap.stl'))
    export_step(top_cap, os.path.join(STEP_DIR, 'top_cap.step'))
    bb = top_cap.bounding_box()
    print(f"  Volume: {top_cap.volume:.1f} mm³")
    print(f"  Bbox: {bb.min} to {bb.max}")
    print(f"  Build time: {dt:.1f}s")
    results['top_cap'] = top_cap

    # ── Bottom Segment ──
    print("\nBuilding bottom segment...")
    t0 = time.time()
    from components.bottom_segment import build_bottom_segment
    bottom = build_bottom_segment()
    dt = time.time() - t0
    export_stl(bottom, os.path.join(STL_DIR, 'bottom_segment.stl'))
    export_step(bottom, os.path.join(STEP_DIR, 'bottom_segment.step'))
    bb = bottom.bounding_box()
    print(f"  Volume: {bottom.volume:.1f} mm³")
    print(f"  Bbox: {bb.min} to {bb.max}")
    print(f"  Build time: {dt:.1f}s")
    results['bottom_segment'] = bottom

    # ── Summary ──
    print("\n" + "=" * 60)
    print("BUILD COMPLETE")
    print("=" * 60)
    stl_files = [f for f in os.listdir(STL_DIR) if f.endswith('.stl')]
    step_files = [f for f in os.listdir(STEP_DIR) if f.endswith('.step')]
    print(f"STL files: {len(stl_files)} in {STL_DIR}")
    for f in sorted(stl_files):
        size = os.path.getsize(os.path.join(STL_DIR, f))
        print(f"  {f} ({size / 1024:.1f} KB)")
    print(f"STEP files: {len(step_files)} in {STEP_DIR}")
    for f in sorted(step_files):
        size = os.path.getsize(os.path.join(STEP_DIR, f))
        print(f"  {f} ({size / 1024:.1f} KB)")

    return results


def validate_meshes():
    """Run basic mesh validation on all exported STLs."""
    import trimesh
    print("\n" + "=" * 60)
    print("MESH VALIDATION")
    print("=" * 60)

    stl_files = [f for f in os.listdir(STL_DIR) if f.endswith('.stl')]
    all_valid = True
    for f in sorted(stl_files):
        path = os.path.join(STL_DIR, f)
        mesh = trimesh.load(path)
        wt = mesh.is_watertight
        vol = mesh.volume
        ext = mesh.bounding_box.extents
        status = "OK" if wt else "FAIL"
        if not wt:
            all_valid = False
        print(f"  {f}: watertight={status}, volume={vol:.0f}mm³, "
              f"extents=[{ext[0]:.1f} x {ext[1]:.1f} x {ext[2]:.1f}]")

    return all_valid


if __name__ == "__main__":
    results = build_and_export_all()
    valid = validate_meshes()
    if not valid:
        print("\nWARNING: Some meshes are not watertight!")
        sys.exit(1)
    else:
        print("\nAll meshes valid.")
