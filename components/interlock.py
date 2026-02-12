"""
Interlock System — Golden Tower (Blender)
==========================================
Run: blender --background --python components/interlock.py

Implements the male/female interlock mechanism:
- Male interlock: protruding ring with alignment key at top of each segment
- Female interlock: receiving groove with keyway at bottom of each segment
- Alignment key enforces correct 52.524° rotational offset between segments
- Engagement depth per tower_params.INTERLOCK_DEPTH
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


def build_male_interlock():
    """Build the male interlock ring with alignment key.

    Returns:
        bpy.types.Object: The male interlock mesh object.
    """
    raise NotImplementedError(
        "Architect agent: implement male interlock geometry using bpy/bmesh. "
        "See .copilot-instructions.md §9 for Blender design patterns."
    )


def build_female_interlock():
    """Build the female interlock groove with keyway.

    Returns:
        bpy.types.Object: The female interlock mesh object.
    """
    raise NotImplementedError(
        "Architect agent: implement female interlock geometry using bpy/bmesh. "
        "See .copilot-instructions.md §9 for Blender design patterns."
    )


def export_interlock(male_obj, female_obj):
    stl_dir = os.path.join(os.path.dirname(__file__), '..', 'exports', 'stl')
    blend_dir = os.path.join(os.path.dirname(__file__), '..', 'exports', 'blend')
    os.makedirs(stl_dir, exist_ok=True)
    os.makedirs(blend_dir, exist_ok=True)

    # Export male
    bpy.ops.object.select_all(action='DESELECT')
    male_obj.select_set(True)
    bpy.context.view_layer.objects.active = male_obj
    stl_path = os.path.join(stl_dir, 'interlock_male.stl')
    bpy.ops.wm.stl_export(filepath=stl_path, export_selected_objects=True)
    print(f'Exported STL: {stl_path}')

    # Export female
    bpy.ops.object.select_all(action='DESELECT')
    female_obj.select_set(True)
    bpy.context.view_layer.objects.active = female_obj
    stl_path = os.path.join(stl_dir, 'interlock_female.stl')
    bpy.ops.wm.stl_export(filepath=stl_path, export_selected_objects=True)
    print(f'Exported STL: {stl_path}')

    # Save .blend with both
    blend_path = os.path.join(blend_dir, 'interlock.blend')
    bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(blend_path))
    print(f'Saved .blend: {blend_path}')


if __name__ == '__main__':
    clear_scene()
    male = build_male_interlock()
    female = build_female_interlock()
    export_interlock(male, female)
