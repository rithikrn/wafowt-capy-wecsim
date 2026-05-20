"""Capytaine BEM solve for the hollow (3-chamber OWC) platform."""
from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
import capytaine as cpt
import capytaine_call as cc

REPO_ROOT      = Path(__file__).resolve().parents[1]
DEFAULT_MESH   = REPO_ROOT / "geometry" / "hollow.stl"
DEFAULT_OUTPUT = REPO_ROOT / "hydroData" / "hollow" / "hollow.nc"

# >>> REPLACE for your platform: full-system centre of mass [m].
CENTER_OF_MASS = (0.0, 0.0, -9.885)

# >>> REPLACE for your OWC chamber geometry.
CHAMBER_DIAMETER = 4.0
CHAMBER_RADIUS   = CHAMBER_DIAMETER / 2.0
RADIAL_OFFSET    = 28.868            # centre -> offset-column distance [m]
PISTON_DEPTH     = -0.001            # piston disk depth just below SWL [m]

# >>> REPLACE if your chambers are not arranged as 3 offset columns at 0/120/240 deg.
CHAMBER_POSITIONS = [
    (-RADIAL_OFFSET, 0.0,                                   PISTON_DEPTH),
    ( RADIAL_OFFSET * 0.5,  RADIAL_OFFSET * 0.5 * 3**0.5,  PISTON_DEPTH),
    ( RADIAL_OFFSET * 0.5, -RADIAL_OFFSET * 0.5 * 3**0.5,  PISTON_DEPTH),
]


def make_piston_disk(center_xyz, radius, n_radial=12, n_azimuthal=36):
    disk = cpt.mesh_disk(
        radius=radius, center=(0.0, 0.0, 0.0), normal=(0.0, 0.0, 1.0),
        resolution=(n_radial, n_azimuthal),
    )
    return disk.translated(center_xyz)


def run(mesh_path, output_path,
        omega_min=cc.DEFAULT_OMEGA_MIN,
        omega_max=cc.DEFAULT_OMEGA_MAX,
        n_freq=cc.DEFAULT_N_FREQ):
    shell = cc.load_platform_mesh(mesh_path)
    platform = cc.build_rigid_body(
        mesh=shell, name="platform_hollow",
        center_of_mass=CENTER_OF_MASS, rotation_center=CENTER_OF_MASS,
        lid_faces_max_radius=1.0,
    )

    pistons = []
    for i, pos in enumerate(CHAMBER_POSITIONS, start=1):
        disk = make_piston_disk(center_xyz=pos, radius=CHAMBER_RADIUS)
        pistons.append(cc.build_piston_body(
            mesh=disk, name=f"owc_piston_{i}", center_of_mass=pos,
        ))

    all_bodies = platform + pistons[0] + pistons[1] + pistons[2]
    omegas = np.linspace(omega_min, omega_max, n_freq)
    test_matrix = cc.make_test_matrix(all_bodies, omegas=omegas)
    cc.solve_and_export(all_bodies, test_matrix, output_path)
    print(f"Wrote {output_path}")


def parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--mesh",      type=Path, default=DEFAULT_MESH)
    p.add_argument("--output",    type=Path, default=DEFAULT_OUTPUT)
    p.add_argument("--omega-min", type=float, default=cc.DEFAULT_OMEGA_MIN)
    p.add_argument("--omega-max", type=float, default=cc.DEFAULT_OMEGA_MAX)
    p.add_argument("--n-freq",    type=int,   default=cc.DEFAULT_N_FREQ)
    return p.parse_args()


if __name__ == "__main__":
    a = parse_args()
    run(a.mesh, a.output, a.omega_min, a.omega_max, a.n_freq)
