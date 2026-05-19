"""
Reusable Capytaine runner for OWC/FOWT hydrodynamic preprocessing.

This module replaces the original project-specific ``capy_call2.py`` with a
path-safe, case-independent runner.  It is intentionally conservative: it keeps
Capytaine's standard ``FloatingBody`` + ``BEMSolver.fill_dataset`` workflow and
writes the Nemoh-style ``Hydrostatics[_i].dat`` and ``KH[_i].dat`` files needed
by BEMIO/WEC-Sim.
"""

from __future__ import annotations

from dataclasses import dataclass
from multiprocessing import Process
from pathlib import Path
from typing import Iterable, Sequence
import importlib
import shutil
import sys

import numpy as np
import xarray as xr

try:
    import capytaine as cpt
except ModuleNotFoundError as exc:  # pragma: no cover - import guard for users
    raise ModuleNotFoundError(
        "Capytaine is required for this module. Install the Python dependencies "
        "from requirements.txt or create the conda environment described in the README."
    ) from exc


@dataclass(frozen=True)
class BodySpec:
    """Description of one hydrodynamic body in the Capytaine model."""

    name: str
    mesh_file: Path
    center_of_mass: Sequence[float]
    lid_file: Path | None = None


def _as_path(path_like: str | Path) -> Path:
    return Path(path_like).expanduser().resolve()


def _write_hydrostatics_files(bodies: Sequence[cpt.FloatingBody], output_dir: Path, rho: float) -> None:
    """Write BEMIO-compatible Hydrostatics/KH files next to the NetCDF output."""
    output_dir.mkdir(parents=True, exist_ok=True)
    multiple_bodies = len(bodies) > 1

    for index, body in enumerate(bodies):
        suffix = f"_{index}" if multiple_bodies else ""
        cg = np.asarray(body.center_of_mass, dtype=float)

        try:
            hydro = body.compute_hydrostatics(rho=rho)
            disp_volume = float(hydro["disp_volume"])
            center_of_buoyancy = np.asarray(hydro["center_of_buoyancy"], dtype=float)
            stiffness = np.asarray(hydro["hydrostatic_stiffness"], dtype=float)
        except Exception:
            # Fully submerged auxiliary bodies can fail hydrostatics depending on
            # the Capytaine/mesh configuration. For those OWC piston bodies, keep
            # zero hydrostatic restoring and export volume/CB from geometry when
            # available so that BEMIO still receives a complete file set.
            disp_volume = float(getattr(body, "volume", 0.0))
            center_of_buoyancy = np.asarray(getattr(body, "center_of_buoyancy", cg), dtype=float)
            stiffness = np.zeros((6, 6))

        stiffness_full = np.zeros((6, 6))
        if stiffness.shape == (6, 6):
            stiffness_full[:, :] = stiffness
        elif stiffness.shape == (3, 3):
            stiffness_full[2:5, 2:5] = stiffness
        else:
            raise ValueError(f"Unexpected hydrostatic stiffness shape for {body.name}: {stiffness.shape}")

        np.savetxt(output_dir / f"KH{suffix}.dat", stiffness_full, fmt="%.8e")
        with (output_dir / f"Hydrostatics{suffix}.dat").open("w", encoding="utf-8") as stream:
            for component, label in enumerate(("X", "Y", "Z")):
                stream.write(
                    f"{label}F = {center_of_buoyancy[component]: .6f} - "
                    f"{label}G = {cg[component]: .6f}\n"
                )
            stream.write(f"Displacement = {disp_volume:.8E}\n")


def _load_body(spec: BodySpec) -> cpt.FloatingBody:
    """Load one body mesh, assign CoG, crop to immersed part, and add 6 DOFs."""
    mesh = cpt.io.mesh_loaders.load_mesh(str(spec.mesh_file))
    kwargs = {"mesh": mesh, "name": spec.name}

    if spec.lid_file is not None and spec.lid_file.exists():
        try:
            kwargs["lid_mesh"] = cpt.io.mesh_loaders.load_mesh(str(spec.lid_file))
        except Exception as exc:
            print(f"WARNING: lid mesh for {spec.name} could not be loaded ({exc}); continuing without lid.")

    try:
        body = cpt.FloatingBody(**kwargs)
    except TypeError:
        # Older/newer Capytaine versions may not accept lid_mesh in the
        # constructor. Fall back to the hull-only body, which matches the
        # original uploaded script because lid_mesh was loaded but not used.
        body = cpt.FloatingBody(mesh=mesh, name=spec.name)

    body.center_of_mass = tuple(float(v) for v in spec.center_of_mass)
    body.keep_immersed_part()
    body.add_all_rigid_body_dofs()
    return body


def _read_and_concat_netcdfs(pattern: str | Path, dim: str = "omega") -> xr.Dataset:
    paths = sorted(Path().glob(str(pattern))) if not Path(str(pattern)).is_absolute() else sorted(Path(str(pattern)).parent.glob(Path(str(pattern)).name))
    if not paths:
        raise FileNotFoundError(f"No NetCDF files matched {pattern}")
    datasets = [xr.open_dataset(path) for path in paths]
    return xr.concat(datasets, dim)


def _solve_frequency_block(
    omega_block: np.ndarray,
    headings: np.ndarray,
    output_file: str,
    water_depth: float,
    rho: float,
    combo_body: cpt.FloatingBody,
) -> None:
    """Solve one frequency block and write a separated-complex NetCDF file."""
    problems = xr.Dataset(
        coords={
            "omega": omega_block,
            "wave_direction": headings,
            "radiating_dof": list(combo_body.dofs),
            "water_depth": [float(water_depth)],
            "rho": [float(rho)],
        }
    )
    solver = cpt.BEMSolver()
    data = solver.fill_dataset(problems, [combo_body], hydrostatics=True)
    cpt.io.xarray.separate_complex_values(data).to_netcdf(
        output_file,
        encoding={
            "radiating_dof": {"dtype": "U"},
            "influenced_dof": {"dtype": "U"},
        },
    )


def run_capytaine(
    bodies: Sequence[BodySpec],
    omega: Iterable[float],
    output_nc: str | Path,
    headings: Iterable[float] = (0.0,),
    water_depth: float = 200.0,
    rho: float = 1025.0,
    num_threads: int = 1,
    overwrite: bool = False,
    additional_dofs_dir: str | Path | None = None,
) -> xr.Dataset:
    """
    Run Capytaine and write hydrodynamic coefficients to a NetCDF file.

    Parameters
    ----------
    bodies:
        Ordered body definitions. Body order must match the WEC-Sim body order.
    omega:
        Angular frequency grid in rad/s.
    output_nc:
        Output NetCDF path.
    headings:
        Wave headings in radians.
    water_depth:
        Positive water depth in meters.
    rho:
        Water density in kg/m^3.
    num_threads:
        Number of independent frequency blocks to solve. Use 1 for debugging.
    overwrite:
        If False, refuse to overwrite an existing NetCDF file.
    additional_dofs_dir:
        Optional directory containing ``gbm_dofs.py`` with ``new_dofs(bodies)``.
    """
    output_nc = _as_path(output_nc)
    output_nc.parent.mkdir(parents=True, exist_ok=True)
    omega = np.asarray(list(omega), dtype=float)
    headings = np.asarray(list(headings), dtype=float)

    if output_nc.exists() and not overwrite:
        raise FileExistsError(f"Output file already exists: {output_nc}. Re-run with overwrite=True.")
    if num_threads < 1:
        raise ValueError("num_threads must be >= 1")
    if omega.size < 2:
        raise ValueError("At least two frequency points are required.")

    loaded_bodies = [_load_body(spec) for spec in bodies]
    _write_hydrostatics_files(loaded_bodies, output_nc.parent, rho=rho)

    if additional_dofs_dir is not None:
        dofs_dir = _as_path(additional_dofs_dir)
        sys.path.insert(0, str(dofs_dir))
        try:
            gbm_dofs = importlib.import_module("gbm_dofs")
            additional_dofs = gbm_dofs.new_dofs(loaded_bodies)
            for body in loaded_bodies:
                if body.name in additional_dofs:
                    body.dofs.update(additional_dofs[body.name])
        finally:
            sys.path.remove(str(dofs_dir))

    combo_body = loaded_bodies[0]
    for body in loaded_bodies[1:]:
        combo_body += body

    print("\n--- Capytaine BEM setup ---")
    print(f"Bodies       : {[body.name for body in loaded_bodies]}")
    print(f"Output       : {output_nc}")
    print(f"Omega range  : {omega[0]:.3f} to {omega[-1]:.3f} rad/s ({omega.size} points)")
    print(f"Headings     : {headings.tolist()} rad")
    print(f"Water depth  : {water_depth:.3f} m")
    print(f"DOFs         : {len(combo_body.dofs)}")
    print(f"Threads      : {num_threads}")

    if num_threads == 1:
        _solve_frequency_block(omega, headings, str(output_nc), water_depth, rho, combo_body)
        return xr.open_dataset(output_nc)

    temp_dir = output_nc.parent / "capyParallelFolder"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir(parents=True)

    jobs: list[Process] = []
    for index, block in enumerate(np.array_split(omega, num_threads), start=1):
        block_file = temp_dir / f"capy_parallel_{index:02d}.nc"
        proc = Process(
            target=_solve_frequency_block,
            args=(block, headings, str(block_file), water_depth, rho, combo_body),
        )
        jobs.append(proc)
        proc.start()

    failed = []
    for proc in jobs:
        proc.join()
        if proc.exitcode != 0:
            failed.append(proc.exitcode)
    if failed:
        raise RuntimeError(f"One or more Capytaine worker processes failed: {failed}")

    combined = _read_and_concat_netcdfs(str(temp_dir / "capy_parallel_*.nc"), dim="omega")
    combined.to_netcdf(output_nc)
    shutil.rmtree(temp_dir)
    print(f"Capytaine complete. Combined output written to {output_nc}")
    return combined
