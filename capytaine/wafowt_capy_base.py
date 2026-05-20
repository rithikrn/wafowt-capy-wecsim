import os
import numpy as np
import capytaine as cpt
from capytaine.io.mesh_writers import write_GDF
from capytaine.meshes.predefined.cylinders import mesh_disk
import capy_call2 as cc  # Ensure this matches your saved module name

# =============================================================================
# USER CONFIGURATION - CASE SPECIFIC VARIABLES (Single Body)
# =============================================================================

# Define center of gravity for the base body
bem_cg = [(0.0, 0.0, -9.8926)]

# Name of the base body
body_names = ['FOWT_base']

# Input mesh files for the main body and lid
main_mesh_file = 'owc_basedesign_template.stl'
lid_mesh_file = 'owc_basedesign_lid_template.gdf'

# Environmental and simulation parameters
bem_w = np.linspace(0.02, 3.0, 150)             # Wave frequencies in rad/s
bem_headings = np.linspace(0, 2*np.pi*(2/3), 1) # Wave headings in rad            
bem_depth = 200.0                               # Water depth [m]
density = 1025.0                                # Water density [kg/m^3]

# Output settings
output_nc_filename = 'capytaine_withoutpto_base.nc'
num_threads = 2

# =============================================================================
# SCRIPT EXECUTION 
# =============================================================================

# Setup geometry directories
script_dir = os.path.dirname(__file__)
geoDir = os.path.abspath(os.path.join(script_dir, "..", "geometry"))
os.makedirs(geoDir, exist_ok=True)

# Collect mesh files
bem_files = [os.path.join(geoDir, main_mesh_file)]
lid_files = [os.path.join(geoDir, lid_mesh_file)]

# Set output path
bem_ncFile = os.path.join(os.getcwd(), output_nc_filename)

if __name__ == '__main__':
    # Call the capytaine wrapper solver
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
