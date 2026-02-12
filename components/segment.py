"""
Standard Segment — Golden Tower (Blender)
==========================================
Run: blender --background --python components/segment.py

A single tower segment with 3 planting pockets placed at golden-angle
intervals, SPIRALING UPWARD (each pocket at a different height).

Includes:
- Outer cylindrical body
- Integrated central supply tube section (not a separate component)
- Integrated drip tray / catch plate with sloped floor and drain through-holes
- Male (top) and female (bottom) interlock geometry
- Alignment key (male) and key slot (female) for rotational indexing
- Net cup lip support ledge in each pocket
- O-ring groove for inter-segment seal
- Clean outer body between pockets (no accessory notches)
"""

import bpy
import bmesh
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from tower_params import *

GOLDEN_ANGLE_RAD = math.radians(GOLDEN_ANGLE_DEG)


def clear_scene():
    """Remove all default objects."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()


def build_segment():
    """Build a standard tower segment.

    Construction strategy:
    1. Create outer cylinder body
    2. Create inner hollow (annular space preserving supply tube wall)
    3. Create integrated supply tube (tube wall from supply tube OD to ID)
    4. Add floor/drip tray at bottom
    5. Create 3 planting pockets spiraling upward at golden-angle spacing
    6. Boolean-subtract pocket bores and supply tube bore
    7. Add male interlock ring at top, female socket at bottom
    8. Add alignment key/slot
    9. Add O-ring groove

    Returns:
        bpy.types.Object: The completed segment mesh object.
    """
    raise NotImplementedError(
        "Architect agent: implement segment geometry using bpy/bmesh. "
        "See .copilot-instructions.md §9 for Blender design patterns. "
        "Study the reference STL cross-sections before building."
    )


def export_segment(obj):
    """Export segment to STL and save .blend file."""
    stl_dir = os.path.join(os.path.dirname(__file__), '..', 'exports', 'stl')
    blend_dir = os.path.join(os.path.dirname(__file__), '..', 'exports', 'blend')
    os.makedirs(stl_dir, exist_ok=True)
    os.makedirs(blend_dir, exist_ok=True)

    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    stl_path = os.path.join(stl_dir, 'segment.stl')
    bpy.ops.wm.stl_export(filepath=stl_path, export_selected_objects=True)
    print(f'Exported STL: {stl_path}')

    blend_path = os.path.join(blend_dir, 'segment.blend')
    bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(blend_path))
    print(f'Saved .blend: {blend_path}')


if __name__ == '__main__':
    clear_scene()
    obj = build_segment()
    export_segment(obj)
