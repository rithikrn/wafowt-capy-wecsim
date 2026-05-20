import os
import numpy as np
import capytaine as cpt
from capytaine.io.mesh_writers import write_GDF
import capy_call2 as cc  # Ensure this matches your saved module name

# =============================================================================
# USER CONFIGURATION - CASE SPECIFIC VARIABLES
# =============================================================================

# Define centers of gravity for the bodies
# Example: (Main body CG, Satellite body 1 CG, Satellite body 2 CG, ...)
bem_cg = (
    (0.0, 0.0, -9.885),
    (-28.868, 0.0, -10.0),
    (14.434, 25.0, -10.0),
    (14.434, -25.0, -10.0)
)

# Names of the bodies corresponding to the CGs above
body_names = (
    'FOWT',
    'OWC_1',
    'OWC_2',
    'OWC_3'
)

# Dimensions & settings for the generated vertical cylinders
cyl_length = 20.0
cyl_radius = 1.9
cyl_resolution = (5, 20, 40)

# Input mesh files for the main body and lid
main_mesh_file = 'owc_hollowdesign_template.stl'
lid_mesh_file = 'owc_hollow_template_lid.gdf'

# Environmental and simulation parameters
bem_w = np.linspace(0.02, 3.0, 150)             # Wave frequencies in rad/s
bem_headings = np.linspace(0, 2*np.pi*(2/3), 1) # Wave headings in rad            
bem_depth = 200.0                               # Water depth [m]
density = 1025.0                                # Water density [kg/m^3]
gravity = 9.81                                  # Gravity [m/s^2]

# Output settings
output_nc_filename = 'capytaine_output.nc'
num_threads = 4

# =============================================================================
# SCRIPT EXECUTION 
# =============================================================================

# Setup geometry directories
script_dir = os.path.dirname(__file__)
geoDir = os.path.abspath(os.path.join(script_dir, "..", "geometry"))
os.makedirs(geoDir, exist_ok=True)

# 1. Generate cylindrical meshes for the satellite bodies
for i in range(len(bem_cg) - 1):
    center = bem_cg[i+1]  # Center of the cylinder

    OWCs = cpt.meshes.predefined.cylinders.mesh_vertical_cylinder(
        length=cyl_length, 
        radius=cyl_radius,
        center=center,
        resolution=cyl_resolution,
        faces_max_radius=None, 
        axial_symmetry=False, 
        reflection_symmetry=False, 
        name=None,
        _theta_max=6.283185307179586
    )
    
    filename = os.path.join(geoDir, f'WC_{i}.gdf')
    write_GDF(filename, OWCs.vertices, OWCs.faces, ulen=1, gravity=gravity, isx=0, isy=0)

# 2. Collect mesh files dynamically based on the number of generated bodies
bem_files_list = [os.path.join(geoDir, main_mesh_file)]
for i in range(len(bem_cg) - 1):
    bem_files_list.append(os.path.join(geoDir, f'WC_{i}.gdf'))

bem_files = tuple(bem_files_list)
lid_files = [os.path.join(geoDir, lid_mesh_file)]

# Set output path
bem_ncFile = os.path.join(os.getcwd(), output_nc_filename)

if __name__ == '__main__':
    # 3. Call the capytaine wrapper solver
    cc.call_capy(
        meshFName=bem_files,
        CoG=bem_cg,
        body_name=body_names,
        headings=bem_headings,
        ncFName=bem_ncFile,
        wCapy=bem_w,
        wDes=bem_w,
        depth=bem_depth,
        density=density,
        lid_files=lid_files,
        additional_dofs_dir=None,
        num_threads=num_threads,
    )
