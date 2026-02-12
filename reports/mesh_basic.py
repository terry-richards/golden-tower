#!/usr/bin/env python3
"""Minimal STL mesh analysis."""
import struct, os

stl_dir = '/home/tmr/src/learn/golden-tower/exports/stl'
for f in sorted(os.listdir(stl_dir)):
    if not f.endswith('.stl'):
        continue
    path = os.path.join(stl_dir, f)
    size = os.path.getsize(path)
    with open(path, 'rb') as fh:
        header = fh.read(80)
        n_faces = struct.unpack('<I', fh.read(4))[0]
    n_verts = n_faces * 3
    expected_size = 84 + 50 * n_faces
    print(f"{f}: faces={n_faces}, vertices~={n_verts}, size={size}B, expected={expected_size}B, match={size==expected_size}")
