#!/usr/bin/env python3
"""Analyze STL mesh metrics and write results to a file."""
import trimesh
import os

stl_dir = '/home/tmr/src/learn/golden-tower/exports/stl'
out_path = '/home/tmr/src/learn/golden-tower/reports/mesh_results.txt'

lines = []
for f in sorted(os.listdir(stl_dir)):
    if not f.endswith('.stl'):
        continue
    m = trimesh.load(os.path.join(stl_dir, f))
    ext = m.bounding_box.extents
    lines.append(f"{f}:")
    lines.append(f"  watertight={m.is_watertight}")
    lines.append(f"  volume={m.volume:.0f} mm3")
    lines.append(f"  extents=({ext[0]:.1f}, {ext[1]:.1f}, {ext[2]:.1f}) mm")
    lines.append(f"  faces={len(m.faces)}")
    lines.append(f"  vertices={len(m.vertices)}")
    lines.append(f"  winding_consistent={m.is_winding_consistent}")
    lines.append("")

with open(out_path, 'w') as fh:
    fh.write('\n'.join(lines))
print("Done:", out_path)
