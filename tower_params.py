"""
Golden Tower — Parametric Dimensions
=====================================
Single source of truth for all dimensions in the Golden Tower hydroponic
grow tower system. All values in millimeters and degrees.

Modify these values to change the design. All component scripts read from
this file — never hard-code dimensions in component files.
"""

import math

# ─── Golden Ratio & Angle ────────────────────────────────────────────
PHI = (1 + math.sqrt(5)) / 2                      # 1.6180339887...
GOLDEN_ANGLE_DEG = 360.0 / (PHI ** 2)             # 137.50776405003785°
GOLDEN_ANGLE_RAD = math.radians(GOLDEN_ANGLE_DEG)

# ─── Segment Geometry ────────────────────────────────────────────────
NODES_PER_SEGMENT = 3
SEGMENT_HEIGHT = 120.0          # mm — vertical height of one segment
SEGMENT_OUTER_DIAMETER = 180.0  # mm — max outer envelope diameter
SEGMENT_OUTER_RADIUS = SEGMENT_OUTER_DIAMETER / 2

# Derived: net rotation between stacked segments
INTERLOCK_ROTATION_DEG = (NODES_PER_SEGMENT * GOLDEN_ANGLE_DEG) % 360  # ≈ 52.524°

# Vertical pitch per node within a segment
NODE_VERTICAL_PITCH = SEGMENT_HEIGHT / NODES_PER_SEGMENT  # 40.0 mm

# ─── Central Tube ────────────────────────────────────────────────────
CENTRAL_TUBE_OD = 32.0          # mm — outer diameter
CENTRAL_TUBE_ID = 28.0          # mm — inner diameter
CENTRAL_TUBE_WALL = (CENTRAL_TUBE_OD - CENTRAL_TUBE_ID) / 2  # 2.0 mm

# ─── Planting Pocket ─────────────────────────────────────────────────
POCKET_DIAMETER = 52.0          # mm — sized for 2" (50mm) net cup + clearance
POCKET_RADIUS = POCKET_DIAMETER / 2
POCKET_TILT_ANGLE = 20.0        # degrees from vertical (outward tilt)
POCKET_DEPTH = 45.0             # mm — depth of pocket
POCKET_RADIAL_OFFSET = 55.0     # mm — center of pocket from tower axis

# ─── Wall Thickness ──────────────────────────────────────────────────
WALL_THICKNESS = 2.0            # mm — minimum wall thickness (5 perimeters × 0.4mm)
WATER_WALL_THICKNESS = 2.4      # mm — water-contact surfaces (6 perimeters)

# ─── Interlock Mechanism ─────────────────────────────────────────────
INTERLOCK_HEIGHT = 10.0         # mm — vertical engagement depth
INTERLOCK_CLEARANCE = 0.3       # mm — gap for printer tolerance
INTERLOCK_KEY_WIDTH = 8.0       # mm — width of alignment key
INTERLOCK_KEY_DEPTH = 3.0       # mm — depth of alignment key slot

# ─── Water Channels ──────────────────────────────────────────────────
CHANNEL_WIDTH = 8.0             # mm
CHANNEL_DEPTH = 3.0             # mm
CHANNEL_MIN_SLOPE = 3.0         # degrees — minimum grade for drainage

# ─── Top Cap ─────────────────────────────────────────────────────────
CAP_DEFLECTOR_ANGLE = 30.0      # degrees — cone half-angle
CAP_OVERHANG = 10.0             # mm — lip beyond outer diameter
CAP_HEIGHT = 40.0               # mm — total cap height including finial

# ─── Bottom Segment ──────────────────────────────────────────────────
QD_FITTING_BARB_OD = 12.7       # mm — 3/8" barb outer diameter (≈ 1/2")
QD_FITTING_ID = 9.525           # mm — 3/8" inner bore
LID_ATTACHMENT_TYPE = "bayonet"  # "bayonet" or "threaded"
LID_BAYONET_LUGS = 3            # number of locking lugs
LID_THREAD_PITCH = 3.0          # mm (if threaded)
RESERVOIR_LID_OD = 160.0        # mm — outer diameter of reservoir lid ring

# ─── 3D Printing ─────────────────────────────────────────────────────
BUILD_VOLUME_X = 256.0          # mm
BUILD_VOLUME_Y = 256.0          # mm
BUILD_VOLUME_Z = 256.0          # mm
BUILD_VOLUME = (BUILD_VOLUME_X, BUILD_VOLUME_Y, BUILD_VOLUME_Z)

LAYER_HEIGHT = 0.20             # mm
NOZZLE_DIAMETER = 0.40          # mm
MAX_OVERHANG_ANGLE = 55.0       # degrees from vertical
MAX_BRIDGE_SPAN = 40.0          # mm
MIN_PERIMETERS = 2              # for general walls
WATER_PERIMETERS = 3            # for water-contact surfaces

# ─── Assembly ─────────────────────────────────────────────────────────
TARGET_SEGMENT_COUNT = 8        # segments per full tower (6-10 range)
TOTAL_TOWER_HEIGHT = (
    CAP_HEIGHT +
    TARGET_SEGMENT_COUNT * SEGMENT_HEIGHT +
    INTERLOCK_HEIGHT  # bottom attachment
)

# ─── O-Ring Specifications (AS568) ────────────────────────────────────
# For inter-segment seal
SEGMENT_ORING_DASH = 228        # AS568-228: ID 50.17mm, CS 3.53mm
SEGMENT_ORING_ID = 50.17        # mm
SEGMENT_ORING_CS = 3.53         # mm (cross-section diameter)
ORING_GROOVE_DEPTH = 2.65       # mm (75% of CS for proper compression)
ORING_GROOVE_WIDTH = 4.50       # mm

# ─── Net Cup ──────────────────────────────────────────────────────────
NET_CUP_OD = 50.0              # mm — standard 2" net cup outer diameter
NET_CUP_LIP_OD = 57.0          # mm — lip/flange outer diameter
NET_CUP_LIP_HEIGHT = 5.0       # mm — lip thickness
NET_CUP_DEPTH = 50.0           # mm
