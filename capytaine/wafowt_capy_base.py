"""Capytaine BEM solve for the baseline (no-OWC) platform."""
from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
import capytaine_call as cc

REPO_ROOT      = Path(__file__).resolve().parents[1]
DEFAULT_MESH   = REPO_ROOT / "geometry" / "base.stl"
DEFAULT_OUTPUT = REPO_ROOT / "hydroData" / "base" / "base.nc"

# >>> REPLACE for your platform: full-system centre of mass (x, y, z) [m].
CENTER_OF_MASS = (0.0, 0.0, -9.893)


def run(mesh_path, output_path,
        omega_min=cc.DEFAULT_OMEGA_MIN,
        omega_max=cc.DEFAULT_OMEGA_MAX,
        n_freq=cc.DEFAULT_N_FREQ):
    mesh = cc.load_platform_mesh(mesh_path)
    platform = cc.build_rigid_body(
        mesh=mesh, name="platform_base",
        center_of_mass=CENTER_OF_MASS, rotation_center=CENTER_OF_MASS,
        lid_faces_max_radius=1.0,
    )
    omegas = np.linspace(omega_min, omega_max, n_freq)
    test_matrix = cc.make_test_matrix(platform, omegas=omegas)
    cc.solve_and_export(platform, test_matrix, output_path)
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
