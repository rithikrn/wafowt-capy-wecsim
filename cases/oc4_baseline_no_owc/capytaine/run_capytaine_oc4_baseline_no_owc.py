"""
Capytaine driver for the OC4 baseline semisubmersible without OWC/PTO bodies.

This is the cleaned, path-safe replacement for the uploaded
``fowt_med_MS_v2_withoutpto.py``. It intentionally models one hydrodynamic
body only: the baseline floating platform. The commented OWC-water-column
body generation from the uploaded script was removed because this baseline
case is the no-OWC/no-PTO reference.

Run from the repository root:

    python cases/oc4_baseline_no_owc/capytaine/run_capytaine_oc4_baseline_no_owc.py --overwrite
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

BASELINE_LID = GEOMETRY_DIR / "oc4_semisubmersible_baseline_lid.gdf"
BODY_SPECS = (
    BodySpec(
        name="OC4_BASELINE",
        mesh_file=GEOMETRY_DIR / "oc4_semisubmersible_baseline_bem.stl",
        center_of_mass=(0.0, 0.0, -9.8926),
        lid_file=BASELINE_LID if BASELINE_LID.exists() else None,
    ),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=HYDRO_DIR / "oc4_baseline_capytaine.nc")
    parser.add_argument("--omega-min", type=float, default=0.02)
    parser.add_argument("--omega-max", type=float, default=3.0)
    parser.add_argument("--omega-count", type=int, default=150)
    parser.add_argument("--water-depth", type=float, default=200.0)
    parser.add_argument("--rho", type=float, default=1025.0)
    parser.add_argument("--threads", type=int, default=2)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
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
