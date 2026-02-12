"""
Bottom Segment — Golden Tower (Blender)
========================================
Run: blender --background --python components/bottom_segment.py

Variant of standard segment that includes:
- Same body, pockets, supply tube, drip tray as standard segment
- NO female interlock at the bottom
- QD fitting barb protruding downward for pump connection
- Bayonet lugs for reservoir lid attachment
- Reservoir lid ring at the bottom
"""

import bpy
import bmesh
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from tower_params import *


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()


def build_bottom_segment():
    """Build the bottom segment with QD fitting and lid attachment.

    Returns:
        bpy.types.Object: The completed bottom segment mesh object.
    """
    raise NotImplementedError(
        "Architect agent: implement bottom segment geometry using bpy/bmesh. "
        "See .copilot-instructions.md §9 for Blender design patterns."
    )


def export_bottom_segment(obj):
    stl_dir = os.path.join(os.path.dirname(__file__), '..', 'exports', 'stl')
    blend_dir = os.path.join(os.path.dirname(__file__), '..', 'exports', 'blend')
    os.makedirs(stl_dir, exist_ok=True)
    os.makedirs(blend_dir, exist_ok=True)

    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    stl_path = os.path.join(stl_dir, 'bottom_segment.stl')
    bpy.ops.wm.stl_export(filepath=stl_path, export_selected_objects=True)
    print(f'Exported STL: {stl_path}')

    blend_path = os.path.join(blend_dir, 'bottom_segment.blend')
    bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(blend_path))
    print(f'Saved .blend: {blend_path}')


if __name__ == '__main__':
    clear_scene()
    obj = build_bottom_segment()
    export_bottom_segment(obj)
