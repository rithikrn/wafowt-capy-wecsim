"""Shared Capytaine helpers for the WAFOWT-CAPY-WECSIM workflow."""
from __future__ import annotations
from pathlib import Path
import numpy as np
import xarray as xr
import capytaine as cpt

WATER_DENSITY = 1025.0
WATER_DEPTH   = 200.0
GRAVITY       = 9.81

DEFAULT_OMEGA_MIN = 0.02
DEFAULT_OMEGA_MAX = 3.00
DEFAULT_N_FREQ    = 150
DEFAULT_WAVE_DIRECTION = 0.0


def load_platform_mesh(mesh_path, file_format=None):
    mesh_path = Path(mesh_path)
    if not mesh_path.exists():
        raise FileNotFoundError(f"Mesh file not found: {mesh_path}")
    if file_format is None:
        return cpt.load_mesh(str(mesh_path))
    return cpt.load_mesh(str(mesh_path), file_format=file_format)


def build_rigid_body(mesh, name, center_of_mass=(0.0, 0.0, 0.0),
                     rotation_center=None, lid_faces_max_radius=1.0,
                     rho=WATER_DENSITY):
    """6-DOF rigid floating body with auto-generated SWL lid."""
    if rotation_center is None:
        rotation_center = tuple(center_of_mass)
    lid = mesh.generate_lid(faces_max_radius=lid_faces_max_radius) if lid_faces_max_radius else None
    body = cpt.FloatingBody(
        mesh=mesh, lid_mesh=lid,
        dofs=cpt.rigid_body_dofs(rotation_center=tuple(rotation_center)),
        center_of_mass=tuple(center_of_mass), name=name,
    )
    body.inertia_matrix = body.compute_rigid_body_inertia(rho=rho)
    body.hydrostatic_stiffness = body.immersed_part().compute_hydrostatic_stiffness(rho=rho)
    return body


def build_piston_body(mesh, name, center_of_mass, rho=WATER_DENSITY):
    """Single-DOF heaving piston (one OWC chamber)."""
    body = cpt.FloatingBody(
        mesh=mesh,
        dofs={"Heave": np.array([(0.0, 0.0, 1.0) for _ in mesh.faces])},
        center_of_mass=tuple(center_of_mass), name=name,
    )
    body.inertia_matrix = body.compute_rigid_body_inertia(rho=rho)
    body.hydrostatic_stiffness = body.immersed_part().compute_hydrostatic_stiffness(rho=rho)
    return body


def make_test_matrix(bodies, omegas=None,
                     wave_directions=(DEFAULT_WAVE_DIRECTION,),
                     water_depth=WATER_DEPTH, rho=WATER_DENSITY):
    if omegas is None:
        omegas = np.linspace(DEFAULT_OMEGA_MIN, DEFAULT_OMEGA_MAX, DEFAULT_N_FREQ)
    return xr.Dataset({
        "omega":          np.asarray(omegas, dtype=float),
        "wave_direction": np.asarray(list(wave_directions), dtype=float),
        "radiating_dof":  list(bodies.dofs),
        "water_depth":    [water_depth],
        "rho":            [rho],
    })


def solve_and_export(bodies, test_matrix, output_nc):
    """Solve the BEM problem and write a BEMIO-compatible NetCDF file."""
    output_nc = Path(output_nc)
    output_nc.parent.mkdir(parents=True, exist_ok=True)
    bodies = bodies.immersed_part()
    dataset = cpt.BEMSolver().fill_dataset(test_matrix, bodies)
    if output_nc.exists():
        output_nc.unlink()
    cpt.export_dataset(str(output_nc), dataset)
    return dataset
