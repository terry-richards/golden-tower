"""
Top Cap — Golden Tower (Blender)
=================================
Run: blender --background --python components/top_cap.py

Deflects water from the central supply tube outward and down onto the
topmost segment's planting pockets. Serves as an aesthetic finial.

Geometry:
- Female interlock socket at bottom (receives male ring from top segment)
- Base plate disc
- Deflector cone (routes water from tube bore outward)
- Water distribution channels
- Finial dome for aesthetics
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


def build_top_cap():
    """Build the top cap / water deflector.

    Returns:
        bpy.types.Object: The completed top cap mesh object.
    """
    raise NotImplementedError(
        "Architect agent: implement top cap geometry using bpy/bmesh. "
        "See .copilot-instructions.md §9 for Blender design patterns."
    )


def export_top_cap(obj):
    stl_dir = os.path.join(os.path.dirname(__file__), '..', 'exports', 'stl')
    blend_dir = os.path.join(os.path.dirname(__file__), '..', 'exports', 'blend')
    os.makedirs(stl_dir, exist_ok=True)
    os.makedirs(blend_dir, exist_ok=True)

    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    stl_path = os.path.join(stl_dir, 'top_cap.stl')
    bpy.ops.wm.stl_export(filepath=stl_path, export_selected_objects=True)
    print(f'Exported STL: {stl_path}')

    blend_path = os.path.join(blend_dir, 'top_cap.blend')
    bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(blend_path))
    print(f'Saved .blend: {blend_path}')


if __name__ == '__main__':
    clear_scene()
    obj = build_top_cap()
    export_top_cap(obj)
