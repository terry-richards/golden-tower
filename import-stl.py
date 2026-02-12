from build123d import *
from ocp_vscode import show

# Import the STL file
print("Loading STL file...")
imported_mesh = import_stl("3-Way_Planting_Module_custom.stl")

# Get bounding box info
bbox = imported_mesh.bounding_box()
print(f"Bounding box size: {bbox.size}")
print(f"Min corner: {bbox.min}")
print(f"Max corner: {bbox.max}")

# Visualize
print("Rendering...")
show(imported_mesh)
