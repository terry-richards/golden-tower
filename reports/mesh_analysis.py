#!/usr/bin/env python3
"""Analyze STL mesh metrics using trimesh."""
import trimesh
import os

stl_dir = '/home/tmr/src/learn/golden-tower/exports/stl'
for f in sorted(os.listdir(stl_dir)):
    if f.endswith('.stl'):
        m = trimesh.load(os.path.join(stl_dir, f))
        ext = m.bounding_box.extents
        print(f"{f}:")
        print(f"  watertight={m.is_watertight}")
        print(f"  volume={m.volume:.0f} mm3")
        print(f"  extents=({ext[0]:.1f}, {ext[1]:.1f}, {ext[2]:.1f}) mm")
        print(f"  faces={len(m.faces)}")
        print(f"  vertices={len(m.vertices)}")
        print()
