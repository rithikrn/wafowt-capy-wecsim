# WAFOWT-CAPY-WECSIM

An open-source, reproducible workflow for reduced-order hydrodynamic
modelling of an oscillating-water-column (OWC) integrated floating
offshore wind turbine platform, built around three established tools:

| Stage | Tool                                           | Role                                                                                   |
| :---- | :--------------------------------------------- | :------------------------------------------------------------------------------------- |
|   1   | Python + STL                                   | platform geometry generation and mesh export                                           |
|   2   | [Capytaine](https://capytaine.org/) (Python)   | linear potential-flow BEM solve; outputs frequency-domain coefficients to NetCDF       |
|   3   | [BEMIO](https://wec-sim.github.io/WEC-Sim/dev/user/advanced_features.html#bemio) (MATLAB) | post-processing of BEM data into a WEC-Sim-ready HDF5 file       |
|   4   | [WEC-Sim](https://wec-sim.github.io/WEC-Sim/) (MATLAB + Simulink) | time-domain coupled simulation (decay, regular, irregular waves)        |

The host platform is the NREL OC4 DeepCwind semisubmersible
[[Robertson et al., 2014]](https://www.nrel.gov/docs/fy14osti/60601.pdf)
supporting the NREL 5 MW reference wind turbine. The repository ships
two ready-to-run cases:

| Case   | Description                                                      | Bodies                                                |
| :----- | :--------------------------------------------------------------- | :---------------------------------------------------- |
| base   | Solid (no-OWC) OC4 baseline                                      | 1 (platform, 6 DOF)                                   |
| hollow | Three offset columns hollowed to form 4 m-diameter OWC chambers  | 4 (platform + 3 OWC piston bodies, 9 DOF total)       |

The base case is the reference; the hollow case shows how the same
pipeline handles a coupled multi-body hydrodynamic problem.

> **Scope.** This repository implements the *reduced-order* layer of the
> workflow. The CFD layer (OpenFOAM RANS--VOF with 6-DoF) and the
> passive-orifice study referenced in the accompanying paper are
> separate; this repo is intentionally limited to Capytaine + BEMIO +
> WEC-Sim so that the moving parts are easy to follow and easy to
> reproduce on any laptop.

---

## Repository layout

```
wafowt-capy-wecsim/
├── README.md                         <- you are here
├── LICENSE
├── CITATION.cff
├── environment.yml                   <- conda environment (recommended)
├── requirements.txt                  <- pip-only alternative
├── .gitignore
│
├── capytaine/                        <- STAGE 2 driver scripts
│   ├── capytaine_call.py             <- shared helpers (mesh, body, solver, export)
│   ├── wafowt_capy_base.py           <- runs the baseline BEM solve
│   └── wafowt_capy_hollow.py         <- runs the 4 m hollow OWC BEM solve
│
├── geometry/                         <- STAGE 1 outputs (surface meshes)
│   ├── base.stl                      <- baseline OC4 wetted surface (CG-aligned)
│   ├── hollow.stl                    <- 4 m hollow shell (CG-aligned)
│   └── owc_piston_4m.stl             <- visualisation mesh for the OWC pistons
│
├── hydroData/                        <- STAGE 2 + STAGE 3 outputs
│   ├── base/
│   │   ├── bemio_base.m              <- BEMIO post-processor for base case
│   │   ├── base.nc                   <- Capytaine output (created at stage 2)
│   │   └── base.h5                   <- WEC-Sim hydro data (created at stage 3)
│   └── hollow/
│       ├── bemio_hollow.m            <- BEMIO post-processor for hollow case
│       ├── hollow.nc                 <- Capytaine output (created at stage 2)
│       └── hollow.h5                 <- WEC-Sim hydro data (created at stage 3)
│
├── wecsim/                           <- STAGE 4
│   ├── wecSimInputFile.m             <- generic input file, switches on caseType
│   ├── userDefinedFunctions.m        <- generic post-processor (plots, animation)
│   ├── wafowt_base.slx               <- Simulink model for the baseline case
│   └── wafowt_hollow.slx             <- Simulink model for the hollow OWC case
│
├── docs/
│   ├── images/                       <- workflow flowchart, mesh views, schematics
│   └── videos/                       <- optional simulation animations
│
└── scripts/
    └── check_repository.py           <- pre-flight check that all expected files exist
```

The four stages map directly onto four folders, so it is always clear
where you are in the pipeline.

---

## Quick start (TL;DR)

1. Install the Python environment (conda recommended):

   ```bash
   conda env create -f environment.yml
   conda activate wafowt-capy-wecsim
   ```

2. Sanity-check the repository:

   ```bash
   python scripts/check_repository.py
   ```

3. Run the BEM solve for whichever case you want:

   ```bash
   python capytaine/wafowt_capy_base.py        # base case
   python capytaine/wafowt_capy_hollow.py      # 4 m hollow case
   ```

4. From MATLAB (with WEC-Sim on the path), build the WEC-Sim hydro file:

   ```matlab
   >> cd hydroData/base    ;  bemio_base
   >> cd hydroData/hollow  ;  bemio_hollow
   ```

5. From MATLAB, run the simulation:

   ```matlab
   >> cd wecsim
   >> edit wecSimInputFile.m         % set caseType = 'base' or 'hollow', pick wave block
   >> wecSim
   ```

The post-processor saves figures to
`wecsim/results/figures/<caseType>/<seaState>/`.

---

## Methodology, step by step

### Stage 1 -- Geometry and mass properties

The platform is a single rigid body (6 DOF) in the baseline case, and a
four-body system in the hollow case (one platform shell plus three OWC
piston bodies in heave). Geometry is represented by triangulated STL
meshes co-located at the platform centre of gravity:

- `geometry/base.stl`   -- baseline OC4 wetted surface
- `geometry/hollow.stl` -- shell of the hollowed platform

Mass and inertia properties, taken from the NREL OC4 specification and
the hollow-column derivation in the accompanying paper, are hard-coded
near the top of `wecsim/wecSimInputFile.m`:

|                                       | Base                | Hollow 4 m          |
| :------------------------------------ | :------------------ | :------------------ |
| System mass, m\_sys [kg]              | 14 072 718          | 13 857 402          |
| z\_CM,sys [m below SWL]               | -9.893              | -9.885              |
| I\_xx = I\_yy [kg m^2]                | 1.3813e10           | 1.106e10            |
| I\_zz [kg m^2]                        | 1.2287e10           | 1.157e10            |
| Waterplane area A\_wp [m^2]           | 372.48              | 334.78              |
| Heave stiffness C\_33 = ρgA\_wp [N/m] | 3 745 330           | 3 366 256           |

The wind turbine masses (tower 249 718 kg, RNA 350 000 kg) are kept
constant across both cases so the comparison isolates the effect of
hollowing.

### Stage 2 -- Capytaine BEM solve

Capytaine solves the linear potential-flow radiation/diffraction problem
over a frequency grid. The default settings (defined in
`capytaine/capytaine_call.py`) are:

- water density rho = 1025 kg/m³,
- water depth h = 200 m (matches OC4),
- angular frequency range omega in \[0.02, 3.0\] rad/s with 150 uniform points,
- single head-sea direction beta = 0 rad,
- automatic lid mesh at the still water line to suppress irregular frequencies.

The case-specific drivers compose `capytaine_call.py`'s helpers into the
right problem:

- **`wafowt_capy_base.py`** -- loads `geometry/base.stl`, builds one
  rigid body with 6 DOFs, solves, and exports
  `hydroData/base/base.nc`.

- **`wafowt_capy_hollow.py`** -- loads `geometry/hollow.stl`, builds the
  platform shell as one rigid body and three heaving piston disks
  (one per offset column, at the chamber centroids), sums them into a
  multi-body system so Capytaine produces the full 9 x 9 added-mass and
  radiation-damping matrices, and exports
  `hydroData/hollow/hollow.nc`.

The lid method places a flat mesh inside the floating body to suppress
the standing-wave modes that pollute the BEM solution at irregular
frequencies. Capytaine generates this automatically when
`lid_faces_max_radius` is set in `build_rigid_body`.

### Stage 3 -- BEMIO post-processing

BEMIO (now bundled with WEC-Sim as MATLAB code, not the legacy Python
`bemio`) reads the NetCDF file and produces the time-domain quantities
WEC-Sim needs:

- the **radiation impulse-response function (IRF)**, computed via the
  cosine transform of the radiation damping with a 60 s convolution
  interval and a 1.9 rad/s high-frequency cutoff,
- a **state-space realisation** of that IRF for fast time-domain
  evaluation,
- the **excitation IRF** via inverse Fourier transform,
- and the **hydrostatic data** (volume, CoB, CoG, stiffness matrix).

Everything is packaged into a `.h5` file. The two driver scripts
(`hydroData/base/bemio_base.m` and `hydroData/hollow/bemio_hollow.m`)
are nearly identical; both use the BEMIO defaults that match the
settings reported in the accompanying paper.

For the multi-body hollow case, the resulting `hollow.h5` contains a
(6×4)-by-(6×4) = 24×24 augmented coefficient block that WEC-Sim slices
per-body using `simu.b2b = 1` (body-to-body interactions). This flag
**must** be on for the hollow case and is set automatically by
`wecSimInputFile.m`.

### Stage 4 -- WEC-Sim time-domain simulation

`wecsim/wecSimInputFile.m` switches between cases via a single flag at
the top of the file:

```matlab
caseType = 'hollow';    % 'base'  or  'hollow'
```

When `caseType = 'base'`, the input file:

- loads `wafowt_base.slx`,
- declares a single body referencing `../hydroData/base/base.h5`,
- sets the baseline mooring stiffness C\_33 = 3 745 330 N/m,
- skips the OWC PTO block.

When `caseType = 'hollow'`, the input file:

- loads `wafowt_hollow.slx`,
- declares one platform body plus three OWC piston bodies referencing
  `../hydroData/hollow/hollow.h5`,
- sets the hollow mooring stiffness C\_33 = 3 366 256 N/m,
- defines three translational PTOs, each with:
  - stiffness K\_wc = ρgA\_bore (the OWC water-column hydrostatic),
  - damping derived from the standard quadratic-orifice mass-flow
    relation linearised around steady oscillation:
    ```
            8 * rho_air * A_bore^3
    c_pto = ----------------------
              pi^2 * Cd^2 * d0^4
    ```

The orifice diameter `orificeDiameter` (= d0) is the principal passive
control parameter. Changing this one number sweeps chamber restriction
without touching anything else.

A run produces, for body 1:

- elevation and (if applicable) spectrum plots,
- force and response plots in all 6 DOFs,
- PTO power plots in the hollow case,
- optional 3D Simscape Mechanics Explorer animation.

`userDefinedFunctions.m` files them under
`wecsim/results/figures/<caseType>/<seaState>/`.

### Workflow diagram

```
   geometry/                                                 wecsim/
   ┌──────────┐       capytaine/         hydroData/         ┌─────────────────┐
   │ base.stl │──┐  ┌──────────────┐  ┌───────────────┐  ┌─>│ wafowt_base.slx │
   │  hollow  │  │  │  capytaine_  │  │ bemio_base.m  │  │  └─────────────────┘
   │   .stl   │──┼─>│   call.py +  │─>│ bemio_hollow  │──┤
   └──────────┘  │  │  wafowt_capy │  │     .m        │  │  ┌─────────────────────┐
                 │  │ _base/hollow │  │               │  └─>│ wafowt_hollow.slx   │
                 │  └──────────────┘  └───────────────┘     └─────────────────────┘
                 │         │                  │                       │
                 │       .nc files          .h5 files                 │
                 │                                                    │
                 └────────────────────────────────────────────────────┘
                                wecSimInputFile.m  +
                                userDefinedFunctions.m
                                       │
                                       v
                              results/figures/...
```

A higher-resolution version is in `docs/images/workflow_flowchart.png`.

---

## How the calculations connect physically

### Frequency-domain BEM coefficients (Capytaine)

Capytaine returns, for each frequency omega:

- the **added-mass** matrix `A(omega)`,
- the **radiation damping** matrix `B(omega)`,
- the **excitation force** vector `X(omega, beta)`,
- the **hydrostatic stiffness** matrix `K_H`.

For the baseline case these matrices are 6 x 6. For the hollow case
they are 9 x 9 because each OWC piston body adds one heave DOF
(`platform (6 DOF) + 3 pistons (1 DOF each) = 9`).

### Cummins equation (BEMIO -> WEC-Sim)

WEC-Sim integrates the Cummins time-domain equation per body:

```
( M + A_inf ) * eta_ddot(t)
   + integral_0^t K_r(t - tau) * eta_dot(tau) dtau
   + K_H * eta(t)
   = F_exc(t) + F_visc(t) + F_moor(t) + F_PTO(t)
```

`A_inf` is the infinite-frequency added mass, `K_r` is the radiation
IRF, and `eta` is the rigid-body displacement. BEMIO supplies the
state-space realisation `(A_r, B_r, C_r, D_r)` so this convolution can
be evaluated as an ODE rather than a quadrature.

### OWC chamber dynamics (hollow case PTO)

In the hollow case, each piston body's heave is the internal water
surface in that chamber. The trapped air volume above the piston gives
a pneumatic restoring force, and the orifice gives a pneumatic damping
force. The WEC-Sim `ptoClass` represents both:

- `pto(k).stiffness = rho_w * g * A_bore`  -- water-column restoring
- `pto(k).damping   = 8 rho_air A_bore^3 / (pi^2 * Cd^2 * d0^4)`
  -- linearised orifice damping (passive restriction)

This is the simplest hydro-pneumatic proxy that preserves the qualitative
behaviour of the orifice; for the full chamber-pressure dynamics and
choked/unchoked transitions, use the CFD layer documented in the paper.

---

## Reproducing the case studies

### Free-decay tests

1. In `wecSimInputFile.m`:
   ```matlab
   waves = waveClass('noWaveCIC');
   body(1).initial.displacement = [0, 0, 1.0];   % 1 m heave kick
   ```
2. Run `wecSim` from `wecsim/`.

This is the verification case used to extract the heave natural period
(17.96 s for the baseline, 18.27 s for the 4 m hollow case in the
thesis).

### Regular waves

1. In `wecSimInputFile.m`, use the default regular block and set the
   `waves.height` and `waves.period` to the target sea state.

Recommended values (Robertson 2014):
| Sea state | Hs [m] | Tp [s] |
|:---------:|:------:|:------:|
| SS2       | 0.67   | 4.8    |
| SS3       | 2.44   | 8.1    |
| SS4       | 5.49   | 11.3   |
| SS5       | 10.0   | 13.6   |
| SS6       | 10.5   | 14.3   |

### Irregular Pierson-Moskowitz waves

In `wecSimInputFile.m`, comment the regular block and uncomment the
irregular block:

```matlab
waves = waveClass('irregular');
waves.height       = 2.44;
waves.period       = 8.1;
waves.spectrumType = 'PM';
waves.direction    = 0;
waves.phaseSeed    = 1;     % for reproducible realisations
```

### Sweeping the OWC orifice diameter (hollow case only)

Change one line in `wecSimInputFile.m`:

```matlab
orificeDiameter = 0.25;   %  e.g. 0.25, 0.50, 1.00, 2.00 m
```

The PTO damping `ptoCoefficient` is computed automatically.

---

## Important gotchas

1. **Base hydrodynamic data is *not* interchangeable with the hollow
   case.** The base case has 6 DOFs (1 body); the hollow case has 9 DOFs
   (4 bodies). Always pair `base.h5` with `wafowt_base.slx` and
   `hollow.h5` with `wafowt_hollow.slx`.

2. **Body order in `wecSimInputFile.m` must match the body order in the
   Capytaine driver.** For the hollow case this is:
   `1 = shell, 2 = front piston, 3 = rear-port piston, 4 = rear-starboard piston`.
   Swapping these silently produces wrong PTO and B2B couplings.

3. **`simu.b2b = 1` must be on for the hollow case.** It is set
   automatically by the supplied `wecSimInputFile.m`, but if you write
   your own input file, remember.

4. **Re-running stage 2 invalidates stage 3.** If you regenerate the
   `.nc` file, re-run the corresponding `bemio_*.m` before invoking
   WEC-Sim again.

5. **STL meshes must be referenced at the body's CG** (this is a
   WEC-Sim requirement, not a Capytaine one). The supplied meshes
   already are.

6. **Lid mesh resolution matters.** Capytaine's auto-lid uses
   `lid_faces_max_radius = 1.0` by default in
   `capytaine_call.build_rigid_body`. For finely panelled platform
   meshes you may need to reduce this; for coarse meshes, increasing it
   speeds up the solve. Iterate if the added-mass or excitation curves
   show oscillatory artefacts near irregular frequencies.

---

## Verification snapshot

A non-exhaustive comparison of the workflow's heave natural period
against published OC4 results:

| Source                                          | T_n,z [s]      | Method                            |
| :---------------------------------------------- | :------------- | :-------------------------------- |
| Robertson et al. 2014                           | 17.5           | WAMIT, moored                     |
| Koo et al. 2014 (1:50 experiment)               | 17.8           | wave-basin                        |
| OC5 phase II multi-code range                   | 17.0 -- 17.8   | multi-code comparison             |
| **This workflow (Capytaine + BEMIO + WEC-Sim)** | **17.96**      | linearised mooring, base case     |

A 2.6% agreement with the NREL reference and 0.9% with the experiment
is typical for linear potential-flow models with a simplified mooring.
Full verification tables for the 4 m hollow case appear in the paper.

---

## Citing

If you use this workflow, please cite:

- This repository (see `CITATION.cff`),
- Ancellin & Dias, "Capytaine: a Python-based linear potential flow BEM
  solver," Journal of Open Source Software, 2019,
- The WEC-Sim publication appropriate to your version,
- Robertson et al., "Definition of the Semisubmersible Floating System
  for Phase II of OC4," NREL TP-5000-60601, 2014.

---

## Official documentation references used

- Capytaine quickstart:  
  https://capytaine.org/stable/user_manual/quickstart.html
- Capytaine export:  
  https://capytaine.org/stable/user_manual/export_output.html
- Capytaine hydrostatics:  
  https://capytaine.org/stable/user_manual/hydrostatics.html
- WEC-Sim workflow:  
  https://wec-sim.github.io/WEC-Sim/dev/user/workflow.html
- WEC-Sim code structure:  
  https://wec-sim.github.io/WEC-Sim/dev/user/code_structure.html
- WEC-Sim advanced features (BEMIO, B2B, nonlinear hydro):  
  https://wec-sim.github.io/WEC-Sim/dev/user/advanced_features.html

---

## License

MIT. See `LICENSE`. Before redistributing modified geometry or hydro
data, confirm that the upstream OC4 specification permits the
particular use case.
