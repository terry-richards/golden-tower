"""
Visual Validation Pipeline — Golden Tower (Blender)
====================================================
Renders multi-view PNGs, cross-section images, and dimensional analysis
for every exported STL using Blender's EEVEE renderer.

This is the primary feedback mechanism for the agent swarm — without these
renders, iteration is blind.

Usage (MUST run via Blender):
    blender --background --python validate_visual.py
    blender --background --python validate_visual.py -- segment.stl
    blender --background --python validate_visual.py -- --all

Outputs to exports/renders/:
    {name}_front.png         — Front view (XZ)
    {name}_right.png         — Right side view (YZ)
    {name}_top.png           — Top-down view (XY)
    {name}_perspective.png   — 3/4 isometric view
    {name}_cross_NNpct.png   — Cross-section at N% height
    {name}_analysis.txt      — Dimensional analysis
"""

import bpy
import bmesh
import mathutils
import math
import os
import sys

# ── Parse arguments (after '--' in blender command line) ──────────
argv = sys.argv
if '--' in argv:
    argv = argv[argv.index('--') + 1:]
else:
    argv = []

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
from tower_params import *

STL_DIR = os.path.join(SCRIPT_DIR, 'exports', 'stl')
RENDER_DIR = os.path.join(SCRIPT_DIR, 'exports', 'renders')
os.makedirs(RENDER_DIR, exist_ok=True)


def clear_scene():
    """Remove all objects from the scene."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    # Remove orphan data
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)
    for block in bpy.data.cameras:
        if block.users == 0:
            bpy.data.cameras.remove(block)
    for block in bpy.data.lights:
        if block.users == 0:
            bpy.data.lights.remove(block)


def setup_material(obj, color=(0.29, 0.56, 0.85, 1.0)):
    """Apply a clean material to the object for rendering."""
    mat = bpy.data.materials.new(name='TowerMaterial')
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes['Principled BSDF']
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Roughness'].default_value = 0.35
    bsdf.inputs['Metallic'].default_value = 0.0
    obj.data.materials.clear()
    obj.data.materials.append(mat)


def setup_render(resolution_x=1200, resolution_y=900):
    """Configure EEVEE render settings."""
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.resolution_x = resolution_x
    scene.render.resolution_y = resolution_y
    scene.render.image_settings.file_format = 'PNG'
    scene.render.film_transparent = True

    # World background
    world = bpy.data.worlds.get('World')
    if world is None:
        world = bpy.data.worlds.new('World')
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get('Background')
    if bg:
        bg.inputs[0].default_value = (0.95, 0.95, 0.95, 1.0)
        bg.inputs[1].default_value = 0.5


def add_camera(location, target=(0, 0, 0)):
    """Add a camera pointing at the target location."""
    bpy.ops.object.camera_add(location=location)
    cam = bpy.context.active_object
    direction = mathutils.Vector(target) - mathutils.Vector(location)
    cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = cam
    return cam


def add_lighting():
    """Add good lighting for visualization."""
    # Key light (sun)
    bpy.ops.object.light_add(type='SUN', location=(200, -200, 400))
    key = bpy.context.active_object
    key.data.energy = 3.0
    key.rotation_euler = (math.radians(45), 0, math.radians(45))

    # Fill light
    bpy.ops.object.light_add(type='SUN', location=(-200, 100, 200))
    fill = bpy.context.active_object
    fill.data.energy = 1.0
    fill.rotation_euler = (math.radians(60), 0, math.radians(-135))


def remove_cameras_and_lights():
    """Remove all cameras and lights (keep mesh objects)."""
    for obj in list(bpy.data.objects):
        if obj.type in ('CAMERA', 'LIGHT'):
            bpy.data.objects.remove(obj, do_unlink=True)


def import_stl(stl_path):
    """Import an STL and return the object."""
    bpy.ops.wm.stl_import(filepath=stl_path)
    obj = bpy.context.selected_objects[0]
    # Smooth shading for better renders
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.shade_smooth()
    return obj


def render_view(obj, name, view_name, cam_location, target=None):
    """Render a single view to PNG."""
    if target is None:
        # Target center of object bounding box
        bbox_center = 0.125 * sum(
            (mathutils.Vector(corner) for corner in obj.bound_box),
            mathutils.Vector()
        )
        target = obj.matrix_world @ bbox_center
        target = (target.x, target.y, target.z)

    remove_cameras_and_lights()
    add_camera(cam_location, target)
    add_lighting()

    filepath = os.path.join(RENDER_DIR, f'{name}_{view_name}.png')
    bpy.context.scene.render.filepath = filepath
    bpy.ops.render.render(write_still=True)
    print(f'  Rendered: {filepath}')
    return filepath


def render_all_views(obj, name):
    """Render front, right, top, and perspective views."""
    dims = obj.dimensions
    max_dim = max(dims.x, dims.y, dims.z)
    dist = max_dim * 2.5
    center_z = dims.z / 2 + obj.location.z
    target = (0, 0, center_z)

    renders = []

    # Front (looking along -Y)
    renders.append(render_view(obj, name, 'front',
                               cam_location=(0, -dist, center_z), target=target))

    # Right (looking along +X)
    renders.append(render_view(obj, name, 'right',
                               cam_location=(dist, 0, center_z), target=target))

    # Top (looking down -Z)
    renders.append(render_view(obj, name, 'top',
                               cam_location=(0, 0, center_z + dist), target=target))

    # Perspective (isometric 3/4 view)
    renders.append(render_view(obj, name, 'perspective',
                               cam_location=(dist * 0.7, -dist * 0.7, center_z + dist * 0.5),
                               target=target))

    return renders


def render_cross_sections(obj, name, n_sections=5):
    """Slice the mesh at key Z-heights and render cross-section views.

    Uses bpy.ops.mesh.bisect to create actual cross-section geometry,
    then renders each slice from above.
    """
    dims = obj.dimensions
    z_min = min(v[2] for v in obj.bound_box) + obj.location.z
    z_max = max(v[2] for v in obj.bound_box) + obj.location.z
    z_range = z_max - z_min

    fractions = [0.05, 0.25, 0.50, 0.75, 0.95]
    z_heights = [z_min + z_range * f for f in fractions]

    cross_renders = []

    for i, (frac, z) in enumerate(zip(fractions, z_heights)):
        # Duplicate the object
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.duplicate()
        dup = bpy.context.active_object

        # Enter edit mode and bisect — keep a thin 2mm slice
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')

        # Remove everything below z - 1mm
        bpy.ops.mesh.bisect(
            plane_co=(0, 0, z - 1.0),
            plane_no=(0, 0, 1),
            clear_inner=True,
            clear_outer=False,
        )

        # Remove everything above z + 1mm
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.bisect(
            plane_co=(0, 0, z + 1.0),
            plane_no=(0, 0, 1),
            clear_inner=False,
            clear_outer=True,
        )

        bpy.ops.object.mode_set(mode='OBJECT')

        # Cross-section material (orange)
        setup_material(dup, color=(0.9, 0.4, 0.1, 1.0))

        # Render from above
        remove_cameras_and_lights()
        view_dist = max(dims.x, dims.y) * 1.5
        add_camera(
            location=(0, 0, z + view_dist),
            target=(0, 0, z)
        )
        add_lighting()

        setup_render(800, 800)
        filepath = os.path.join(RENDER_DIR,
                                f'{name}_cross_{frac*100:.0f}pct_z{z:.0f}mm.png')
        bpy.context.scene.render.filepath = filepath
        bpy.ops.render.render(write_still=True)
        print(f'  Cross-section at Z={z:.1f}mm ({frac*100:.0f}%): {filepath}')
        cross_renders.append(filepath)

        # Delete the duplicate
        bpy.data.objects.remove(dup, do_unlink=True)

    # Reset render resolution
    setup_render()
    return cross_renders


def analyze_mesh(obj, name):
    """BMesh-based dimensional analysis — volume, manifold, overhang angles."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)

    lines = []
    lines.append(f'=== Dimensional Analysis: {name} ===')
    lines.append(f'')

    dims = obj.dimensions
    bbox = obj.bound_box
    x_vals = [v[0] for v in bbox]
    y_vals = [v[1] for v in bbox]
    z_vals = [v[2] for v in bbox]

    lines.append(f'Bounding Box:')
    lines.append(f'  X: {min(x_vals):.1f} to {max(x_vals):.1f} ({dims.x:.1f} mm)')
    lines.append(f'  Y: {min(y_vals):.1f} to {max(y_vals):.1f} ({dims.y:.1f} mm)')
    lines.append(f'  Z: {min(z_vals):.1f} to {max(z_vals):.1f} ({dims.z:.1f} mm)')
    lines.append(f'')

    volume = bm.calc_volume()
    lines.append(f'Volume: {volume:.0f} mm³ ({volume / 1000:.1f} cm³)')

    area = sum(f.calc_area() for f in bm.faces)
    lines.append(f'Surface Area: {area:.0f} mm²')

    non_manifold = [e for e in bm.edges if not e.is_manifold]
    lines.append(f'Manifold: {"Yes" if len(non_manifold) == 0 else f"NO — {len(non_manifold)} non-manifold edges"}')
    lines.append(f'Faces: {len(bm.faces)}, Vertices: {len(bm.verts)}, Edges: {len(bm.edges)}')
    lines.append(f'')

    # Fill ratio
    envelope_vol = math.pi * (SEGMENT_OUTER_RADIUS ** 2) * SEGMENT_HEIGHT
    fill_pct = volume / envelope_vol * 100 if envelope_vol > 0 else 0
    lines.append(f'Fill ratio vs {SEGMENT_OUTER_DIAMETER}mm x {SEGMENT_HEIGHT}mm '
                 f'cylinder: {fill_pct:.1f}%')
    lines.append(f'')

    # Dimensional checks
    lines.append(f'Dimensional Checks:')
    lines.append(f'  Expected outer diameter: {SEGMENT_OUTER_DIAMETER:.0f} mm')
    xy_span = max(dims.x, dims.y)
    lines.append(f'  Actual XY span: {xy_span:.1f} mm')
    delta = xy_span - SEGMENT_OUTER_DIAMETER
    lines.append(f'  Delta: {delta:+.1f} mm '
                 f'{"(pockets protrude — expected)" if delta > 0 else "(within envelope)"}')
    lines.append(f'')
    lines.append(f'  Expected height: ~{SEGMENT_HEIGHT:.0f} mm '
                 f'(+{INTERLOCK_HEIGHT:.0f}mm interlock)')
    lines.append(f'  Actual Z span: {dims.z:.1f} mm')
    lines.append(f'')

    # Overhang analysis
    lines.append(f'Face angle distribution (from build plate / horizontal):')
    up = mathutils.Vector((0, 0, 1))
    angle_buckets = {'0-30deg': 0, '30-45deg': 0, '45-55deg': 0, '55-70deg': 0, '70-90deg': 0}
    for face in bm.faces:
        # angle from vertical
        angle_from_vert = math.degrees(face.normal.angle(up, 0))
        # overhang angle from horizontal = 90 - angle_from_vertical
        if angle_from_vert <= 30:
            angle_buckets['0-30deg'] += 1
        elif angle_from_vert <= 45:
            angle_buckets['30-45deg'] += 1
        elif angle_from_vert <= 55:
            angle_buckets['45-55deg'] += 1
        elif angle_from_vert <= 70:
            angle_buckets['55-70deg'] += 1
        else:
            angle_buckets['70-90deg'] += 1

    total_faces = len(bm.faces)
    for bucket, count in angle_buckets.items():
        pct = count / total_faces * 100 if total_faces > 0 else 0
        flag = ' ** OVERHANG WARNING' if bucket in ('55-70deg', '70-90deg') and pct > 5 else ''
        lines.append(f'  {bucket}: {count} faces ({pct:.1f}%){flag}')

    bm.free()

    text = '\n'.join(lines)
    out_path = os.path.join(RENDER_DIR, f'{name}_analysis.txt')
    with open(out_path, 'w') as f:
        f.write(text)
    print(f'  Analysis: {out_path}')
    print(text)
    return out_path


def validate_stl(stl_path):
    """Run full visual validation on one STL file."""
    name = os.path.splitext(os.path.basename(stl_path))[0]
    print(f'\n{"="*60}')
    print(f'Validating: {name}')
    print(f'{"="*60}')

    clear_scene()
    setup_render()

    obj = import_stl(stl_path)
    setup_material(obj)

    renders = []
    renders.extend(render_all_views(obj, name))
    renders.extend(render_cross_sections(obj, name))
    renders.append(analyze_mesh(obj, name))

    return renders


def validate_all():
    """Validate all STLs in exports/stl/."""
    stl_files = sorted([
        os.path.join(STL_DIR, f)
        for f in os.listdir(STL_DIR)
        if f.endswith('.stl')
    ])

    if not stl_files:
        print('No STL files found in exports/stl/')
        return []

    all_renders = []
    for stl_path in stl_files:
        renders = validate_stl(stl_path)
        all_renders.extend(renders)

    print(f'\n{"="*60}')
    print(f'Generated {len(all_renders)} validation files in {RENDER_DIR}/')
    print(f'{"="*60}')
    print(f'\n*** HUMAN REVIEW REQUIRED ***')
    print(f'Open the PNG files in exports/renders/ and evaluate:')
    print(f'  1. Do the multi-view renders show the expected geometry?')
    print(f'  2. Do cross-sections show supply tube bore, pockets, walls?')
    print(f'  3. Do the dimensional spot-checks match tower_params.py?')
    print(f'  4. Is the fill ratio reasonable for a hollow structure (~15-25%)?')
    print(f'  5. Are overhang angles within printable limits (<=55 deg)?')
    return all_renders


# ── Main ─────────────────────────────────────────────────────────────
if __name__ == '__main__':
    if argv and argv[0] != '--all':
        stl_path = argv[0]
        if not os.path.isabs(stl_path):
            stl_path = os.path.join(STL_DIR, stl_path)
        validate_stl(stl_path)
    else:
        validate_all()
