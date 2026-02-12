"""
Visual Validation Pipeline — Golden Tower
==========================================
Renders multi-view PNGs and cross-section analysis for every exported STL.
This is the primary feedback mechanism for the agent swarm — without these
renders, iteration is blind.

Usage:
    python validate_visual.py                  # render all STLs
    python validate_visual.py segment.stl      # render one STL
    python validate_visual.py --cross-section  # also generate cross-sections

Outputs to exports/renders/:
    {name}_ortho.png    — 4-view orthographic (front, right, top, perspective)
    {name}_cross_Z{h}.png — cross-section at height h
    {name}_analysis.txt — dimensional spot-checks
"""

import os
import sys
import math
import argparse
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tower_params import *

STL_DIR = os.path.join(os.path.dirname(__file__), 'exports', 'stl')
RENDER_DIR = os.path.join(os.path.dirname(__file__), 'exports', 'renders')


def ensure_dirs():
    os.makedirs(RENDER_DIR, exist_ok=True)


def load_mesh(stl_path):
    """Load an STL and return a trimesh mesh."""
    import trimesh
    mesh = trimesh.load(stl_path)
    if isinstance(mesh, trimesh.Scene):
        mesh = trimesh.util.concatenate(mesh.dump())
    return mesh


def render_orthographic(mesh, name, output_dir=RENDER_DIR):
    """Render 4-view orthographic projection to a single PNG.

    Views: Front (XZ), Right (YZ), Top (XY), Perspective (isometric).
    Uses matplotlib for headless rendering — no GPU needed.
    """
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    vertices = mesh.vertices
    faces = mesh.faces

    # Subsample faces for rendering performance (max 5000 faces)
    if len(faces) > 5000:
        indices = np.random.choice(len(faces), 5000, replace=False)
        render_faces = faces[indices]
    else:
        render_faces = faces

    fig = plt.figure(figsize=(20, 20))
    fig.suptitle(f'{name}\nBbox: {mesh.bounding_box.extents[0]:.1f} × '
                 f'{mesh.bounding_box.extents[1]:.1f} × '
                 f'{mesh.bounding_box.extents[2]:.1f} mm  |  '
                 f'Volume: {mesh.volume:.0f} mm³  |  '
                 f'Watertight: {mesh.is_watertight}',
                 fontsize=14, y=0.98)

    views = [
        ('Front (XZ)', 0, 0),
        ('Right (YZ)', 0, 90),
        ('Top (XY)', 90, 0),
        ('Perspective', 30, -45),
    ]

    center = mesh.centroid
    extent = max(mesh.bounding_box.extents) * 0.7

    for idx, (title, elev, azim) in enumerate(views):
        ax = fig.add_subplot(2, 2, idx + 1, projection='3d')
        ax.set_title(title, fontsize=12)

        # Plot mesh faces
        poly = Poly3DCollection(
            vertices[render_faces],
            alpha=0.6,
            facecolor='#4a90d9',
            edgecolor='#2c3e50',
            linewidths=0.1
        )
        ax.add_collection3d(poly)

        ax.set_xlim(center[0] - extent, center[0] + extent)
        ax.set_ylim(center[1] - extent, center[1] + extent)
        ax.set_zlim(center[2] - extent, center[2] + extent)
        ax.view_init(elev=elev, azim=azim)
        ax.set_xlabel('X (mm)')
        ax.set_ylabel('Y (mm)')
        ax.set_zlabel('Z (mm)')

    plt.tight_layout()
    out_path = os.path.join(output_dir, f'{name}_ortho.png')
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f'  Rendered: {out_path}')
    return out_path


def render_cross_sections(mesh, name, output_dir=RENDER_DIR):
    """Slice the mesh at key Z heights and render 2D cross-section profiles.

    This catches issues that 3D views miss:
    - Missing pocket holes
    - Supply tube bore present/absent
    - Wall thickness visual check
    - Drain channel geometry
    """
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches

    bbox = mesh.bounding_box
    z_min, z_max = bbox.bounds[0][2], bbox.bounds[1][2]
    z_range = z_max - z_min

    # Slice at 5 evenly-spaced heights plus specific feature heights
    z_heights = sorted(set([
        z_min + z_range * 0.05,   # near bottom (interlock region)
        z_min + z_range * 0.25,   # lower pocket region
        z_min + z_range * 0.50,   # mid pocket region
        z_min + z_range * 0.75,   # upper pocket region
        z_min + z_range * 0.95,   # near top (interlock region)
    ]))

    fig, axes = plt.subplots(1, len(z_heights), figsize=(4 * len(z_heights), 4))
    if len(z_heights) == 1:
        axes = [axes]

    fig.suptitle(f'{name} — Cross Sections', fontsize=14, y=1.02)

    sections_found = 0
    for idx, z in enumerate(z_heights):
        ax = axes[idx]
        ax.set_title(f'Z = {z:.1f} mm\n({(z - z_min) / z_range * 100:.0f}% height)',
                     fontsize=9)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)

        try:
            section = mesh.section(plane_origin=[0, 0, z],
                                   plane_normal=[0, 0, 1])
            if section is not None:
                # Get 2D path
                slice_2d, _ = section.to_2D()
                for entity in slice_2d.entities:
                    points = slice_2d.vertices[entity.points]
                    ax.plot(points[:, 0], points[:, 1], 'b-', linewidth=0.8)
                sections_found += 1

                # Add reference circles for expected features
                # Supply tube bore
                circle_tube = plt.Circle((0, 0), SUPPLY_TUBE_OD / 2,
                                         fill=False, color='red',
                                         linestyle='--', linewidth=0.5,
                                         label='Supply tube OD')
                ax.add_patch(circle_tube)
                # Outer envelope
                circle_outer = plt.Circle((0, 0), SEGMENT_OUTER_RADIUS,
                                          fill=False, color='green',
                                          linestyle='--', linewidth=0.5,
                                          label='Outer envelope')
                ax.add_patch(circle_outer)

                ax.set_xlim(-SEGMENT_OUTER_RADIUS * 1.3,
                            SEGMENT_OUTER_RADIUS * 1.3)
                ax.set_ylim(-SEGMENT_OUTER_RADIUS * 1.3,
                            SEGMENT_OUTER_RADIUS * 1.3)
            else:
                ax.text(0.5, 0.5, 'No intersection', transform=ax.transAxes,
                        ha='center', va='center', fontsize=10, color='red')
        except Exception as e:
            ax.text(0.5, 0.5, f'Error:\n{e}', transform=ax.transAxes,
                    ha='center', va='center', fontsize=8, color='red')

    # Legend
    if sections_found > 0:
        red_line = mpatches.Patch(color='red', label='Supply tube OD (expected)')
        green_line = mpatches.Patch(color='green', label='Outer envelope (expected)')
        fig.legend(handles=[red_line, green_line], loc='lower center', ncol=2)

    plt.tight_layout()
    out_path = os.path.join(output_dir, f'{name}_cross_sections.png')
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f'  Cross-sections: {out_path}')
    return out_path


def analyze_dimensions(mesh, name, output_dir=RENDER_DIR):
    """Dimensional spot-checks — probe specific features in the mesh.

    Writes human-readable analysis to a text file.
    """
    bbox = mesh.bounding_box
    extents = bbox.extents
    bounds = bbox.bounds

    lines = []
    lines.append(f'=== Dimensional Analysis: {name} ===')
    lines.append(f'')
    lines.append(f'Bounding Box:')
    lines.append(f'  X: {bounds[0][0]:.1f} to {bounds[1][0]:.1f} ({extents[0]:.1f} mm)')
    lines.append(f'  Y: {bounds[0][1]:.1f} to {bounds[1][1]:.1f} ({extents[1]:.1f} mm)')
    lines.append(f'  Z: {bounds[0][2]:.1f} to {bounds[1][2]:.1f} ({extents[2]:.1f} mm)')
    lines.append(f'')
    lines.append(f'Volume: {mesh.volume:.0f} mm³ ({mesh.volume / 1000:.1f} cm³)')
    lines.append(f'Surface Area: {mesh.area:.0f} mm²')
    lines.append(f'Watertight: {mesh.is_watertight}')
    lines.append(f'Winding Consistent: {mesh.is_winding_consistent}')
    lines.append(f'Faces: {len(mesh.faces)}, Vertices: {len(mesh.vertices)}')
    lines.append(f'')

    # Fill ratio vs cylindrical envelope
    envelope_vol = math.pi * (SEGMENT_OUTER_RADIUS ** 2) * SEGMENT_HEIGHT
    fill_pct = mesh.volume / envelope_vol * 100 if envelope_vol > 0 else 0
    lines.append(f'Fill ratio vs {SEGMENT_OUTER_DIAMETER}mm × {SEGMENT_HEIGHT}mm '
                 f'cylinder: {fill_pct:.1f}%')
    lines.append(f'')

    # Expected vs actual dimensions
    lines.append(f'Dimensional Checks:')
    lines.append(f'  Expected outer diameter: {SEGMENT_OUTER_DIAMETER:.0f} mm')
    lines.append(f'  Actual XY span: {max(extents[0], extents[1]):.1f} mm')
    xy_delta = max(extents[0], extents[1]) - SEGMENT_OUTER_DIAMETER
    lines.append(f'  Delta: {xy_delta:+.1f} mm '
                 f'{"(pockets protrude — expected)" if xy_delta > 0 else "(within envelope)"}')
    lines.append(f'')
    lines.append(f'  Expected height: ~{SEGMENT_HEIGHT:.0f} mm '
                 f'(+{INTERLOCK_HEIGHT:.0f}mm interlock)')
    lines.append(f'  Actual Z span: {extents[2]:.1f} mm')
    lines.append(f'')

    # Cross-section area at various heights to detect hollowing issues
    lines.append(f'Cross-section areas (solid area at each Z height):')
    z_min, z_max = bounds[0][2], bounds[1][2]
    z_range = z_max - z_min
    for frac in [0.1, 0.25, 0.5, 0.75, 0.9]:
        z = z_min + z_range * frac
        try:
            section = mesh.section(plane_origin=[0, 0, z],
                                   plane_normal=[0, 0, 1])
            if section is not None:
                slice_2d, _ = section.to_2D()
                area = slice_2d.area if hasattr(slice_2d, 'area') else 0
                lines.append(f'  Z={z:.1f}mm ({frac*100:.0f}%): {area:.1f} mm²')
            else:
                lines.append(f'  Z={z:.1f}mm ({frac*100:.0f}%): no section')
        except Exception as e:
            lines.append(f'  Z={z:.1f}mm ({frac*100:.0f}%): error ({e})')

    text = '\n'.join(lines)
    out_path = os.path.join(output_dir, f'{name}_analysis.txt')
    with open(out_path, 'w') as f:
        f.write(text)
    print(f'  Analysis: {out_path}')
    print(text)
    return out_path


def validate_stl(stl_path, do_cross_sections=True):
    """Run full visual validation on one STL file."""
    name = os.path.splitext(os.path.basename(stl_path))[0]
    print(f'\n{"="*60}')
    print(f'Validating: {name}')
    print(f'{"="*60}')

    mesh = load_mesh(stl_path)
    renders = []
    renders.append(render_orthographic(mesh, name))
    if do_cross_sections:
        renders.append(render_cross_sections(mesh, name))
    renders.append(analyze_dimensions(mesh, name))
    return renders


def validate_all(do_cross_sections=True):
    """Validate all STLs in exports/stl/."""
    ensure_dirs()
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
        renders = validate_stl(stl_path, do_cross_sections)
        all_renders.extend(renders)

    print(f'\n{"="*60}')
    print(f'Generated {len(all_renders)} validation files in {RENDER_DIR}/')
    print(f'{"="*60}')
    print(f'\n*** HUMAN REVIEW REQUIRED ***')
    print(f'Open the PNG files in exports/renders/ and evaluate:')
    print(f'  1. Do the 4-view renders show the expected geometry?')
    print(f'  2. Do cross-sections show supply tube bore, pockets, walls?')
    print(f'  3. Do the dimensional spot-checks match tower_params.py?')
    print(f'  4. Is the fill ratio reasonable for a hollow structure (~15-25%)?')
    return all_renders


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Visual validation for Golden Tower STLs')
    parser.add_argument('stl', nargs='?', help='Specific STL file to validate')
    parser.add_argument('--no-cross-section', action='store_true',
                        help='Skip cross-section rendering')
    args = parser.parse_args()

    ensure_dirs()

    if args.stl:
        if not os.path.isabs(args.stl):
            args.stl = os.path.join(STL_DIR, args.stl)
        validate_stl(args.stl, not args.no_cross_section)
    else:
        validate_all(not args.no_cross_section)
