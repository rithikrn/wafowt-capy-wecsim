"""
Capytaine driver for the 4 m hollow OWC-integrated OC4 semisubmersible.

This case has four hydrodynamic bodies in this order:

1. hollow platform shell,
2. front/upwind OWC internal water-column piston,
3. rear-port OWC internal water-column piston,
4. rear-starboard OWC internal water-column piston.

Run from the repository root:

    python cases/oc4_hollow_owc_4m/capytaine/run_capytaine_oc4_hollow_owc_4m.py --overwrite
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))

from owc_fowt_hydro.capytaine_runner import BodySpec, run_capytaine  # noqa: E402

CASE_DIR = Path(__file__).resolve().parents[1]
GEOMETRY_DIR = CASE_DIR / "geometry"
HYDRO_DIR = CASE_DIR / "hydroData"

BODY_SPECS = (
    BodySpec("OC4_HOLLOW_OWC_4M", GEOMETRY_DIR / "oc4_hollow_owc_4m_bem.stl", (0.0, 0.0, -9.885)),
    BodySpec("OWC_PISTON_1_FRONT", GEOMETRY_DIR / "owc_piston_4m_ch1.gdf", (-28.868, 0.0, -10.0)),
    BodySpec("OWC_PISTON_2_REAR_PORT", GEOMETRY_DIR / "owc_piston_4m_ch2.gdf", (14.434, 25.0, -10.0)),
    BodySpec("OWC_PISTON_3_REAR_STARBOARD", GEOMETRY_DIR / "owc_piston_4m_ch3.gdf", (14.434, -25.0, -10.0)),
)


def write_gdf_vertical_cylinder(path: Path, center: tuple[float, float, float], radius: float = 1.9, length: float = 20.0) -> None:
    """Generate a simple vertical cylindrical piston mesh in GDF format."""
    import capytaine as cpt
    from capytaine.io.mesh_writers import write_GDF

    mesh = cpt.meshes.predefined.cylinders.mesh_vertical_cylinder(
        length=length,
        radius=radius,
        center=center,
        resolution=(5, 20, 40),
        axial_symmetry=False,
        reflection_symmetry=False,
    )
    write_GDF(str(path), mesh.vertices, mesh.faces, ulen=1, gravity=9.81, isx=0, isy=0)


def ensure_owc_piston_gdfs() -> None:
    """Create the three OWC piston GDF meshes before the Capytaine solve."""
    GEOMETRY_DIR.mkdir(parents=True, exist_ok=True)
    write_gdf_vertical_cylinder(GEOMETRY_DIR / "owc_piston_4m_ch1.gdf", (-28.868, 0.0, -10.0))
    write_gdf_vertical_cylinder(GEOMETRY_DIR / "owc_piston_4m_ch2.gdf", (14.434, 25.0, -10.0))
    write_gdf_vertical_cylinder(GEOMETRY_DIR / "owc_piston_4m_ch3.gdf", (14.434, -25.0, -10.0))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=HYDRO_DIR / "oc4_hollow_owc_4m_capytaine.nc")
    parser.add_argument("--omega-min", type=float, default=0.02)
    parser.add_argument("--omega-max", type=float, default=3.0)
    parser.add_argument("--omega-count", type=int, default=150)
    parser.add_argument("--water-depth", type=float, default=200.0)
    parser.add_argument("--rho", type=float, default=1025.0)
    parser.add_argument("--threads", type=int, default=4)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ensure_owc_piston_gdfs()
    omega = np.linspace(args.omega_min, args.omega_max, args.omega_count)
    run_capytaine(
        bodies=BODY_SPECS,
        omega=omega,
        output_nc=args.output,
        headings=(0.0,),
        water_depth=args.water_depth,
        rho=args.rho,
        num_threads=args.threads,
        overwrite=args.overwrite,
    )


if __name__ == "__main__":
    main()
