# WAFOWT-CAPY-WECSIM

An open-source, end-to-end, reproducible workflow for the reduced-order
hydrodynamic modelling of an oscillating-water-column (OWC) integrated
floating offshore wind turbine (FOWT) platform built on the NLR OC4
DeepCwind semisubmersible.

The repository implements a clean four-stage pipeline:

| Stage | Tool                                                                   | Language          | Role                                                                                              |
| :---: | :--------------------------------------------------------------------- | :---------------- | :------------------------------------------------------------------------------------------------ |
|   1   | Python + STL meshes                                                    | Python            | Platform geometry and mesh definition                                                              |
|   2   | [Capytaine](https://capytaine.org/) [1]                                 | Python            | Linear potential-flow boundary-element method (BEM) solve; frequency-domain coefficients to NetCDF |
|   3   | [BEMIO](https://wec-sim.github.io/WEC-Sim/dev/user/advanced_features.html#bemio) [2] | MATLAB            | Post-processes BEM data; computes IRFs and state-space radiation models; writes WEC-Sim HDF5      |
|   4   | [WEC-Sim](https://wec-sim.github.io/WEC-Sim/) [2,3]                    | MATLAB + Simulink | Time-domain coupled simulation: free decay, regular waves, irregular waves                         |

Two ready-to-run cases are bundled, sharing the same input file, the
same post-processor, and the same Python helpers:

| Case   | Geometry            | Bodies                                              | DOF | Hydro data                  | Simulink model        |
| :----- | :------------------ | :-------------------------------------------------- | :-: | :-------------------------- | :-------------------- |
| base   | `geometry/base.stl` | 1 (platform)                                        |  6  | `hydroData/base/base.h5`    | `wafowt_base.slx`     |
| hollow | `geometry/hollow.stl` | 4 (platform shell + 3 OWC piston bodies)          |  9  | `hydroData/hollow/hollow.h5`| `wafowt_hollow.slx`   |

---

## Table of contents

1. [What this repository is for](#1-what-this-repository-is-for)
2. [Workflow at a glance](#2-workflow-at-a-glance)
3. [Repository structure](#3-repository-structure)
4. [Installation](#4-installation)
   - [4.1 Prerequisites](#41-prerequisites)
   - [4.2 Python and Capytaine](#42-python-and-capytaine)
   - [4.3 MATLAB and WEC-Sim](#43-matlab-and-wec-sim)
   - [4.4 BEMIO](#44-bemio)
   - [4.5 Verifying the installation](#45-verifying-the-installation)
5. [Quick start](#5-quick-start)
6. [Detailed methodology](#6-detailed-methodology)
   - [6.1 Stage 1: Geometry and mass properties](#61-stage-1-geometry-and-mass-properties)
   - [6.2 Stage 2: Capytaine BEM solve](#62-stage-2-capytaine-bem-solve)
   - [6.3 Stage 3: BEMIO post-processing](#63-stage-3-bemio-post-processing)
   - [6.4 Stage 4: WEC-Sim time-domain simulation](#64-stage-4-wec-sim-time-domain-simulation)
7. [Theory summary](#7-theory-summary)
8. [Running the standard cases](#8-running-the-standard-cases)
9. [File-by-file guide](#9-file-by-file-guide)
10. [Verification and benchmarking](#10-verification-and-benchmarking)
11. [Common pitfalls and troubleshooting](#11-common-pitfalls-and-troubleshooting)
12. [References](#12-references)
13. [Citing this workflow](#13-citing-this-workflow)
14. [License](#14-license)

---

## 1. What this repository is for

Floating offshore wind turbines based on semisubmersible platforms are
structurally expensive: the offset columns alone constitute a major
share of the platform's steel mass, and platform mass is a dominant
driver of fabrication cost [4, 5]. Hollowing the offset columns to form
OWC chambers is attractive because it simultaneously removes structural
material and introduces a wave-energy-capture opportunity. However,
hollowing also changes mass, waterplane area, hydrostatic restoring
stiffness, added mass, radiation damping, and the global rigid-body
response. None of these effects can be reasoned about in isolation.

This repository provides the reduced-order modelling tools needed to
quantify those coupled changes:

- a transparent Python layer for the linear potential-flow BEM solve,
  including auto-generated lid meshes for irregular-frequency
  suppression;
- a thin MATLAB layer for BEMIO post-processing (radiation IRF,
  excitation IRF, state-space realisation);
- a single WEC-Sim input file driving either case with one flag;
- a generic post-processor that captures forces, responses, waves, and
  PTO power for both cases.

It is intentionally limited to the Capytaine + BEMIO + WEC-Sim
reduced-order layer to keep the moving parts small and inspectable.

---

## 2. Workflow at a glance

The four pipeline stages map one-to-one onto four top-level folders.
The four-stage flowchart shows the dataflow:

![Four-stage workflow flowchart](docs/media/images/capywecsimworkflowflowchart.png)
*Four-stage computational workflow: geometry → Capytaine BEM → BEMIO →
WEC-Sim time-domain.*

The host platform geometry, in its baseline (solid) form, is shown
below. The OWC modification hollows each of the three offset columns
into a vertical chamber open to the sea at the bottom and capped by a
trapped air volume above:

![Baseline OC4 DeepCwind platform](docs/media/images/oc4_baseline_platform.png)
*Geometry of the baseline NLR OC4 DeepCwind semisubmersible platform
[6].*

![OWC integration concept](docs/media/owc_concept.png)
*OWC-integration concept: (left) top view showing the three offset-column
chambers; (right) section view of one chamber showing the internal water
column and trapped air volume.*

The same wetted-surface mesh used by Capytaine for the OWC-integrated
platform, together with the lid mesh used to suppress irregular
frequencies, is shown below:

![Capytaine mesh and lid](docs/media/capytaine_mesh_and_lid.png)
*Capytaine mesh: (left) wetted-surface mesh of the platform (green) with
OWC chambers modelled at each offset column (blue, yellow, and pink);
(right) lid mesh (pink) placed at the still water plane.*

The two Simulink models, one for each case, are shown below:

![Simulink layouts](docs/media/simulink_layouts.png)
*WEC-Sim Simulink layouts: (left) baseline (no-OWC); (right) 4 m hollow
OWC case with platform shell plus three OWC piston bodies.*

An example simulation animation (4 m hollow case, SS4 regular waves) is
provided in `docs/media/`:

- `docs/media/animation_hollow_ss4.mp4`

---

## 3. Repository structure

```
wafowt-capy-wecsim/
├── README.md                         <- you are here
├── LICENSE                           <- MIT
├── CITATION.cff
├── environment.yml                   <- conda environment (recommended)
├── requirements.txt                  <- pip-only alternative
├── .gitignore
│
├── capytaine/                        <- STAGE 2: BEM driver scripts (Python)
│   ├── capytaine_call.py             <- shared helpers (mesh, body, solver, export)
│   ├── wafowt_capy_base.py           <- runs the baseline BEM solve
│   └── wafowt_capy_hollow.py         <- runs the 4 m hollow OWC BEM solve
│
├── geometry/                         <- STAGE 1: wetted-surface meshes
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
├── wecsim/                           <- STAGE 4: time-domain simulation
│   ├── wecSimInputFile.m             <- generic input file, switches on caseType
│   ├── userDefinedFunctions.m        <- generic post-processor
│   ├── wafowt_base.slx               <- Simulink model for the baseline case
│   └── wafowt_hollow.slx             <- Simulink model for the hollow OWC case
│
├── docs/
│   └── media/                        <- figures and animations used by this README
│
└── scripts/
    └── check_repository.py           <- pre-flight check that all files exist
```

Each pipeline stage is its own folder. Folder names match stage names.
You always know where you are.

---

## 4. Installation

### 4.1 Prerequisites

This workflow uses two independent toolchains; both are required.

| Toolchain   | Required version                               | Required toolboxes / dependencies                              |
| :---------- | :--------------------------------------------- | :------------------------------------------------------------- |
| Python      | 3.10 – 3.12 (Capytaine supports 3.8+)          | numpy, scipy, xarray, netCDF4, matplotlib, meshio, Capytaine   |
| MATLAB      | R2020b or later (four latest releases tested) [7] | Simulink, Simscape, Simscape Multibody                     |

Both toolchains run on Windows, macOS, and Linux.

A working `git` client is recommended for cloning WEC-Sim. `git-lfs` is
needed if you want WEC-Sim's bundled large `.h5` examples.

### 4.2 Python and Capytaine

Capytaine [1] is the linear potential-flow BEM solver used in stage 2.
Two installation routes are supported.

**Recommended (Conda).** Conda-forge ships precompiled Capytaine wheels
on all major platforms and resolves the Fortran/MKL dependencies
automatically [8]:

```bash
git clone https://github.com/rithikrn/wafowt-capy-wecsim.git
cd wafowt-capy-wecsim
conda env create -f environment.yml
conda activate wafowt-capy-wecsim
```

The `environment.yml` pins Python 3.10–3.12, Capytaine ≥ 2.2, and the
relevant scientific Python stack.

**Alternative (pip).** Capytaine also publishes precompiled wheels on
PyPI [8]:

```bash
git clone https://github.com/rithikrn/wafowt-capy-wecsim.git
cd wafowt-capy-wecsim
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Verify the install:

```bash
python -c "import capytaine as cpt; print('Capytaine', cpt.__version__)"
```

You should see Capytaine 2.2 or later.

If you cannot or do not want to install Python locally, Capytaine also
runs unmodified inside Google Colab and CoCalc; install with
`%pip install capytaine` in a notebook cell [8].

### 4.3 MATLAB and WEC-Sim

WEC-Sim [2, 3] is the time-domain solver used in stage 4. The
following follows WEC-Sim's official getting-started guide [7].

**Step 1: Verify MATLAB toolboxes.** In MATLAB type `ver` and check
that all four of the following are listed:

- MATLAB
- Simulink
- Simscape
- Simscape Multibody

**Step 2: Clone WEC-Sim.** WEC-Sim uses Git LFS for its example `.h5`
files, so install Git LFS first [7]:

```bash
git lfs install
git clone https://github.com/WEC-Sim/WEC-Sim
```

Take note of the local path you cloned into; it is referred to below as
`$WECSIM`.

**Step 3: Add WEC-Sim to the MATLAB path.** The simplest option is the
one-time-per-session script (Option 2 in the WEC-Sim docs [7]):

```matlab
>> cd $WECSIM
>> addWecSimSource
```

For a permanent addition, copy `$WECSIM/source/addWecSimSource.m` into a
MATLAB `startup.m` file in your MATLAB start-up folder, as documented
in [7].

**Step 4: Refresh the Simulink library browser.**

```matlab
>> slLibraryBrowser
```

The WEC-Sim library should appear in the browser. The library blocks
are saved in R2020b format so newer MATLAB versions will load them
without complaint.

**Step 5: Test WEC-Sim independently of this repository.** Run the
WEC-Sim RM3 reference case [7]:

```matlab
>> cd $WECSIM/examples/RM3
>> wecSim
```

If a Mechanics Explorer window opens and produces output figures, your
WEC-Sim installation is good.

### 4.4 BEMIO

BEMIO ships **with** WEC-Sim as MATLAB code [2]; there is no separate
install step. As long as the WEC-Sim source directory is on the MATLAB
path (step 3 above), functions like `readCAPYTAINE`, `radiationIRF`,
`radiationIRFSS`, `excitationIRF`, `writeBEMIOH5`, and `plotBEMIO` are
available globally.

> **Note.** The legacy Python BEMIO is no longer supported [2]. All
> BEMIO work in this workflow uses the MATLAB version that ships with
> WEC-Sim.

### 4.5 Verifying the installation

From the repository root:

```bash
python scripts/check_repository.py
```

This script checks that every expected file is present in the tree. It
does not run Capytaine or WEC-Sim; it just makes sure nothing is
missing before you begin a long workflow run.

From MATLAB, you can also confirm BEMIO sees your Capytaine output once
you have run stage 2 (see the next section).

---

## 5. Quick start

After completing section 4, the full pipeline for either case is four
commands:

**Baseline case.**

```bash
python capytaine/wafowt_capy_base.py            # stage 2: writes hydroData/base/base.nc
```
```matlab
>> cd hydroData/base ; bemio_base               % stage 3: writes hydroData/base/base.h5
>> cd ../../wecsim                              % stage 4
>> %  edit wecSimInputFile.m -> caseType = 'base'
>> wecSim
```

**Hollow OWC case.**

```bash
python capytaine/wafowt_capy_hollow.py          % stage 2: writes hydroData/hollow/hollow.nc
```
```matlab
>> cd hydroData/hollow ; bemio_hollow           % stage 3: writes hydroData/hollow/hollow.h5
>> cd ../../wecsim                              % stage 4
>> %  edit wecSimInputFile.m -> caseType = 'hollow'
>> wecSim
```

The `userDefinedFunctions.m` post-processor saves all figures to:

```
wecsim/results/figures/<caseType>/<seaState>/
```

---

## 6. Detailed methodology

### 6.1 Stage 1: Geometry and mass properties

The host platform is the NREL OC4 DeepCwind semisubmersible [6]
supporting the NREL 5 MW reference wind turbine [9]. The platform
consists of one central main column, three offset columns connected by
a pontoon and cross-brace system, and circular base columns at the
bottom of each offset column.

Both cases are derived from the same OC4 reference. The OWC variant
hollows each of the three offset columns to form a vertical chamber of
inner diameter D = 4 m, open to the sea at the bottom and capped by a
trapped air volume at the top.

Mass and inertia properties (system-level, including the tower and the
RNA) are hard-coded in `wecsim/wecSimInputFile.m`:

|                                       | Base                | Hollow 4 m          |
| :------------------------------------ | :------------------ | :------------------ |
| System mass m_sys [kg]                | 14 072 718          | 13 857 402          |
| z_CM,sys [m below SWL]                | -9.893              | -9.885              |
| I_xx = I_yy [kg m²]                   | 1.3813 × 10¹⁰       | 1.106 × 10¹⁰        |
| I_zz [kg m²]                          | 1.2287 × 10¹⁰       | 1.157 × 10¹⁰        |
| Waterplane area A_wp [m²]             | 372.48              | 334.78              |
| Heave stiffness C_33 = ρ g A_wp [N/m] | 3 745 330           | 3 366 256           |

The wind turbine masses (tower 249 718 kg, RNA 350 000 kg) are kept
constant across both cases, isolating the effect of hollowing.

The wetted-surface STL meshes are co-located at the body's centre of
gravity, as required by WEC-Sim's body class [10].

### 6.2 Stage 2: Capytaine BEM solve

Capytaine solves the linear potential-flow radiation/diffraction problem
over a frequency grid. The default settings, defined in
`capytaine/capytaine_call.py`, follow standard practice:

| Parameter               | Value                  |
| :---------------------- | :--------------------- |
| Water density ρ         | 1025 kg/m³             |
| Water depth h           | 200 m (matches OC4)    |
| Angular frequency ω     | 150 uniform points in [0.02, 3.0] rad/s |
| Wave heading β          | 0 rad (head seas)      |
| Lid mesh                | Auto-generated at SWL  |

The lid method [1] places a flat horizontal mesh inside the floating
body at the still water line, suppressing the standing-wave modes
("irregular frequencies") that otherwise pollute the BEM solution.
Capytaine's `Mesh.generate_lid(faces_max_radius=...)` API is used; the
default panel radius is 1.0 m and is exposed in
`capytaine_call.build_rigid_body`.

The two case drivers compose the helpers in different ways:

- `wafowt_capy_base.py` loads `geometry/base.stl`, builds one
  `FloatingBody` with the six standard rigid-body DOFs (surge, sway,
  heave, roll, pitch, yaw), solves, and exports
  `hydroData/base/base.nc` via Capytaine's `export_dataset` [11].

- `wafowt_capy_hollow.py` loads `geometry/hollow.stl` for the platform
  shell, builds it as a six-DOF rigid body, and then constructs three
  one-DOF heaving piston bodies (one per offset column) as flat disks
  at the chamber centroids. The four bodies are summed before being
  passed to `BEMSolver.fill_dataset`, which signals Capytaine to solve
  the full coupled 9 × 9 radiation/diffraction problem. The
  body-to-body coupling matrices end up in `hydroData/hollow/hollow.nc`.

Both drivers accept command-line overrides:

```bash
python capytaine/wafowt_capy_hollow.py --omega-max 4.0 --n-freq 200
```

Use `--help` for the full list.

### 6.3 Stage 3: BEMIO post-processing

BEMIO [2] reads the Capytaine NetCDF file and produces the time-domain
quantities WEC-Sim needs. The processing steps (matching the thesis
settings) are:

1. **`readCAPYTAINE(hydro, ncFile, hsDir)`** — reads the
   radiation/diffraction coefficients, body geometry, and hydrostatic
   stiffness (the latter from the `Hydrostatics.dat` and `KH.dat`
   files that Capytaine writes alongside the `.nc`).
2. **`radiationIRF(hydro, 60, [], [], [], 1.9)`** — computes the
   radiation impulse-response function via the cosine transform of the
   radiation damping, with a 60 s convolution window and a 1.9 rad/s
   high-frequency cutoff [2, 12].
3. **`radiationIRFSS(hydro, [], [])`** — fits a state-space model to
   each radiation IRF (max order 10, R² threshold 0.95 by default).
4. **`excitationIRF(hydro, 60, [], [], [], 1.9)`** — computes the
   excitation IRF by inverse Fourier transform.
5. **`writeBEMIOH5(hydro)`** — packages all of the above into a single
   HDF5 file consumed by WEC-Sim.

The two case scripts (`bemio_base.m`, `bemio_hollow.m`) are nearly
identical; they differ only in the input and output filenames.

For the hollow case, the resulting `hollow.h5` contains the full
(6 × 4) × (6 × 4) = 24 × 24 augmented coefficient block. WEC-Sim slices
it per body using `simu.b2b = 1`, which is set automatically by
`wecSimInputFile.m`.

### 6.4 Stage 4: WEC-Sim time-domain simulation

WEC-Sim [3] integrates the Cummins time-domain equation [13] for each
body using the BEMIO-generated hydro data. The Simulink models
implement the standard WEC-Sim block structure: a global reference frame,
a rigid body block per hydrodynamic body, a constraint block, a mooring
block, and (for the hollow case) a translational PTO block per OWC
chamber.

`wecsim/wecSimInputFile.m` is a single file that drives both cases via
one flag:

```matlab
caseType = 'hollow';    % 'base' or 'hollow'
```

When `caseType = 'base'`:
- loads `wafowt_base.slx`;
- declares one body referencing `../hydroData/base/base.h5`;
- sets the baseline mooring stiffness C_33 = 3 745 330 N/m;
- skips PTO setup entirely.

When `caseType = 'hollow'`:
- loads `wafowt_hollow.slx`;
- declares one platform body plus three OWC piston bodies referencing
  `../hydroData/hollow/hollow.h5`;
- sets `simu.b2b = 1` (mandatory for the multi-body coupling);
- sets the hollow mooring stiffness C_33 = 3 366 256 N/m;
- defines three translational PTOs at the chamber centroids, each with
  a water-column hydrostatic stiffness `K_wc = ρ_w g A_bore` and a
  fixed linearised pneumatic damping coefficient as a reduced-order
  proxy for the OWC mechanism.

The wave block in `wecSimInputFile.m` defaults to a regular wave at the
SS4 sea state (H = 5.49 m, T = 11.3 s). Free-decay (no waves) and
irregular (Pierson–Moskowitz) blocks are present but commented; switch
to them by uncommenting the desired block and commenting the regular
block.

`userDefinedFunctions.m` runs automatically at the end of every
`wecSim` call and produces:

- elevation and (where applicable) spectrum plots;
- body-1 force plots in all six DOFs (surge, sway, heave, roll, pitch,
  yaw);
- body-1 response plots in all six DOFs;
- PTO power plots for each chamber (hollow case only);
- optional 3-D Simscape Mechanics Explorer animation (toggle via the
  `saveAnimation` flag).

Figures are saved to:

```
wecsim/results/figures/<caseType>/<seaState>/
```

The `<seaState>` tag is auto-generated from the active wave class, so
runs at different sea states do not overwrite each other.

---

## 7. Theory summary

### 7.1 Linear potential-flow BEM

Under the standard linear potential-flow assumptions [14], the fluid
velocity is described by a scalar potential Φ satisfying Laplace's
equation in the fluid domain, the linearised free-surface boundary
condition on z = 0, and the body boundary condition on the wetted
surface. Capytaine solves this boundary-value problem using a
collocation BEM and returns, for each frequency ω:

- the added-mass matrix A(ω);
- the radiation damping matrix B(ω);
- the excitation force vector X(ω, β);
- the hydrostatic stiffness matrix K_H.

For the baseline case these are 6 × 6 matrices. For the hollow case
they are 9 × 9 (one heave DOF per OWC piston, in addition to the six
rigid-body DOFs of the shell).

### 7.2 Time-domain Cummins equation

WEC-Sim integrates, per body, the Cummins equation [13]:

```
( M + A_inf ) · η̈(t)
 + ∫₀ᵗ K_r(t - τ) · η̇(τ) dτ
 + K_H · η(t)
 = F_exc(t) + F_visc(t) + F_moor(t) + F_PTO(t)
```

where `A_inf` is the infinite-frequency added mass, `K_r(t)` is the
radiation impulse-response function

```
K_r(t) = (2/π) ∫₀^∞ B(ω) cos(ω t) dω
```

and η is the rigid-body displacement vector. BEMIO produces a
state-space realisation `(A_r, B_r, C_r, D_r)` so this convolution can
be evaluated as an ODE [12, 15], dramatically reducing run time.

### 7.3 OWC chamber model (reduced-order)

In the hollow case, each piston body's heave equals the internal water
surface in that chamber. The trapped air volume above the piston gives
a pneumatic restoring force and the orifice gives a pneumatic damping
force. The reduced-order proxy used here is

```
F_PTO,k(t) = K_wc · z_k(t) + c_pto · ż_k(t)
```

where `z_k` is the piston heave for chamber k, `K_wc = ρ_w g A_bore` is
the water-column hydrostatic stiffness, and `c_pto` is a fixed
linearised pneumatic-damping coefficient. This is the simplest model
that preserves the qualitative behaviour of the OWC at the reduced-order
fidelity targeted by this workflow.

### 7.4 Wave conditions

Wave conditions are defined per WEC-Sim conventions [3]. Regular waves
are monochromatic sinusoids `η(x,t) = (H/2) cos(ωt − k x)`. Irregular
waves are constructed by superposition of the Pierson–Moskowitz
spectrum [16],

```
S_PM(ω) = (5/16) · H_s² · ω_p⁴ · ω⁻⁵ · exp(-(5/4) (ω_p/ω)⁴)
```

discretised by WEC-Sim's `EqualEnergy` or `Traditional` binning.

### 7.5 Sea-state matrix

The standard sea-state matrix [6] used throughout:

| Sea state | H_s [m] | T_p [s] | Description |
| :-------: | :-----: | :-----: | :---------- |
| SS2       | 0.67    | 4.8     | mild        |
| SS3       | 2.44    | 8.1     | moderate    |
| SS4       | 5.49    | 11.3    | significant |
| SS5       | 10.0    | 13.6    | severe      |
| SS6       | 10.5    | 14.3    | very severe |

---

## 8. Running the standard cases

### 8.1 Free-decay tests

To extract heave / pitch / roll natural periods:

```matlab
% in wecSimInputFile.m:
waves = waveClass('noWaveCIC');
body(1).initial.displacement = [0, 0, 1.0];   % 1 m heave kick
```

Run `wecSim`. The damped oscillation in the heave time history yields
the natural period directly.

### 8.2 Regular waves

The default block. Set `waves.height` and `waves.period` to the target
sea state:

```matlab
waves = waveClass('regular');
waves.height = 5.49;       % H [m]
waves.period = 11.3;       % T [s]
```

### 8.3 Irregular waves (Pierson–Moskowitz)

```matlab
waves = waveClass('irregular');
waves.height       = 2.44;     % Hs [m]
waves.period       = 8.1;      % Tp [s]
waves.spectrumType = 'PM';
waves.direction    = 0;
waves.phaseSeed    = 1;        % for reproducible realisations
```

`waves.phaseSeed` makes the wave realisation deterministic and is
strongly recommended for any quantitative comparison.

---

## 9. File-by-file guide

| Path                                         | Stage | Description                                                                                                  |
| :------------------------------------------- | :---: | :----------------------------------------------------------------------------------------------------------- |
| `capytaine/capytaine_call.py`                |   2   | Shared helpers: mesh loading, body construction (rigid and piston), test-matrix building, BEM solve, export. |
| `capytaine/wafowt_capy_base.py`              |   2   | Baseline driver. One body, six DOFs.                                                                          |
| `capytaine/wafowt_capy_hollow.py`            |   2   | Hollow driver. Platform shell + three heaving piston disks at the chamber centroids; 9 DOFs.                  |
| `geometry/base.stl`                          |   1   | Baseline OC4 wetted surface, CG-aligned.                                                                      |
| `geometry/hollow.stl`                        |   1   | Hollow-shell wetted surface, CG-aligned.                                                                      |
| `geometry/owc_piston_4m.stl`                 |   1   | Visualisation mesh for the OWC piston bodies (Simulink view only).                                            |
| `hydroData/base/bemio_base.m`                |   3   | BEMIO driver for the baseline case.                                                                           |
| `hydroData/hollow/bemio_hollow.m`            |   3   | BEMIO driver for the hollow case.                                                                             |
| `hydroData/*/{*.nc, *.h5}`                   | 2 / 3 | Outputs of stages 2 and 3. Created by the driver scripts.                                                     |
| `wecsim/wecSimInputFile.m`                   |   4   | Generic WEC-Sim input file. One flag, two cases.                                                              |
| `wecsim/userDefinedFunctions.m`              |   4   | Generic post-processor. Saves all figures.                                                                    |
| `wecsim/wafowt_base.slx`                     |   4   | Simulink model: one body + global reference + mooring.                                                        |
| `wecsim/wafowt_hollow.slx`                   |   4   | Simulink model: shell + 3 piston bodies + 3 PTOs + global reference + mooring.                                |
| `scripts/check_repository.py`                |   -   | Pre-flight integrity check.                                                                                   |
| `environment.yml` / `requirements.txt`       |   -   | Python dependency manifests.                                                                                  |
| `CITATION.cff`                               |   -   | Machine-readable citation metadata.                                                                           |

---

## 10. Verification and benchmarking

A non-exhaustive comparison of this workflow's heave natural period
against published OC4 results:

| Source                                          | T_n,z [s]      | Method                            |
| :---------------------------------------------- | :------------- | :-------------------------------- |
| Robertson et al. 2014 [6]                       | 17.5           | WAMIT, moored                     |
| Koo et al. 2014 [17] (1:50 experiment)          | 17.8           | wave-basin                        |
| OC5 phase II multi-code range [18]              | 17.0 – 17.8    | multi-code comparison             |
| **This workflow** (Capytaine + BEMIO + WEC-Sim) | **17.96**      | linearised mooring, base case     |

A 2.6 % agreement with the NREL reference and 0.9 % with the experiment
is typical for linear potential-flow models with a simplified mooring.

The hydrodynamic coefficients of the baseline platform agree with the
NLR OC4 reference data [6] to within 2.5 %, with residual differences
attributable primarily to pontoon omission and finite mesh resolution.

---

## 11. Common pitfalls and troubleshooting

1. **Base hydrodynamic data is not interchangeable with the hollow
   case.** The base case has 6 DOFs (1 body); the hollow case has 9
   DOFs (4 bodies). Always pair `base.h5` with `wafowt_base.slx` and
   `hollow.h5` with `wafowt_hollow.slx`.

2. **Body order must match between Capytaine and WEC-Sim.** For the
   hollow case the order is `1 = shell, 2 = front piston, 3 = rear-port
   piston, 4 = rear-starboard piston`. Reordering at one stage but not
   the other silently corrupts the PTO and body-to-body couplings.

3. **`simu.b2b = 1` must be on for the hollow case.** This is set
   automatically by the supplied `wecSimInputFile.m`. If you write
   your own input file, remember.

4. **Regenerating stage 2 invalidates stage 3.** Re-run the
   corresponding `bemio_*.m` whenever you change the `.nc` file.

5. **STL meshes must be referenced at the body's CG.** This is a
   WEC-Sim requirement [3, 10]. The supplied meshes already are.

6. **Lid mesh resolution.** Capytaine's auto-lid uses
   `lid_faces_max_radius = 1.0` by default. For finely panelled
   platform meshes you may need to reduce this; for coarse meshes,
   increasing it speeds up the solve.

7. **Hydrostatics.dat / KH.dat next to the `.nc`.** BEMIO's
   `readCAPYTAINE` looks for these files in the same folder as the
   NetCDF. Capytaine writes them automatically when
   `compute_hydrostatic_stiffness` has been called on the body, which
   `capytaine_call.build_rigid_body` does. If BEMIO complains about
   missing hydrostatics, check that both files appeared.

8. **`git lfs` errors during WEC-Sim install.** If the WEC-Sim RM3
   example fails because `rm3.h5` is missing, run `bemio.m` inside
   `$WECSIM/examples/RM3/hydroData/` to regenerate it [7].

---

## 12. References

[1] M. Ancellin and F. Dias, "Capytaine: a Python-based linear potential
flow BEM solver," *Journal of Open Source Software*, vol. 4, no. 36, p.
1341, 2019. https://doi.org/10.21105/joss.01341. Documentation:
https://capytaine.org.

[2] WEC-Sim Team, "BEMIO: Boundary Element Method Input/Output." In
*WEC-Sim Advanced Features documentation*.
https://wec-sim.github.io/WEC-Sim/dev/user/advanced_features.html#bemio.

[3] K. Ruehl, C. Michelen, S. Kanner, M. Lawson, and Y.-H. Yu,
"Preliminary verification and validation of WEC-Sim, an open-source
wave energy converter design tool," in *Proc. of the ASME 33rd
International Conference on Ocean, Offshore and Arctic Engineering*,
2014. WEC-Sim documentation: https://wec-sim.github.io/WEC-Sim/.

[4] T. Wang et al., "Multi-objective optimisation of floating offshore
wind platforms," (representative literature on cost-driven
semisubmersible design).

[5] M. Stehly and P. Beiter, "2019 Cost of Wind Energy Review," NREL
Technical Report NREL/TP-5000-78471, 2020.

[6] A. Robertson, J. Jonkman, M. Masciola, H. Song, A. Goupee, A.
Coulling, and C. Luan, "Definition of the Semisubmersible Floating
System for Phase II of OC4," NREL Technical Report NREL/TP-5000-60601,
2014. https://www.nrel.gov/docs/fy14osti/60601.pdf.

[7] WEC-Sim Team, "Getting Started." In *WEC-Sim User Manual*.
https://wec-sim.github.io/WEC-Sim/dev/user/getting_started.html.

[8] M. Ancellin, "Installation for users." In *Capytaine documentation*.
https://capytaine.org/stable/user_manual/installation.html.

[9] J. Jonkman, S. Butterfield, W. Musial, and G. Scott, "Definition
of a 5-MW Reference Wind Turbine for Offshore System Development," NREL
Technical Report NREL/TP-500-38060, 2009.

[10] WEC-Sim Team, "Code Structure." In *WEC-Sim User Manual*.
https://wec-sim.github.io/WEC-Sim/dev/user/code_structure.html.

[11] M. Ancellin, "Export outputs." In *Capytaine documentation*.
https://capytaine.org/stable/user_manual/export_output.html.

[12] T. Perez and T. I. Fossen, "A Matlab toolbox for parametric
identification of radiation-force models of ships and offshore
structures," *Modeling, Identification and Control*, vol. 30, no. 1, pp.
1–15, 2009.

[13] W. E. Cummins, "The Impulse Response Function and Ship Motions,"
*Schiffstechnik*, vol. 9, pp. 101–109, 1962.

[14] O. M. Faltinsen, *Sea Loads on Ships and Offshore Structures*.
Cambridge University Press, 1993.

[15] WEC-Sim Team, "Theory Manual." 
https://wec-sim.github.io/WEC-Sim/dev/theory/index.html.

[16] W. J. Pierson Jr. and L. Moskowitz, "A proposed spectral form for
fully developed wind seas based on the similarity theory of S. A.
Kitaigorodskii," *Journal of Geophysical Research*, vol. 69, no. 24,
pp. 5181–5190, 1964.

[17] B. J. Koo, A. J. Goupee, R. W. Kimball, and K. F. Lambrakos, "Model
Tests for a Floating Wind Turbine on Three Different Floaters," in
*Proc. of the ASME 33rd International Conference on Ocean, Offshore and
Arctic Engineering*, 2014.

[18] A. Robertson et al., "OC5 Project Phase II: Validation of Global
Loads of the DeepCwind Floating Semisubmersible Wind Turbine," *Energy
Procedia*, vol. 137, pp. 38–57, 2017.

---

## 13. Citing this workflow

If you use this workflow in academic work, please cite this repository
(see `CITATION.cff`) together with the three primary tool publications:

- Capytaine: Ancellin and Dias 2019 [1];
- WEC-Sim: Ruehl et al. 2014 [3];
- OC4 reference geometry: Robertson et al. 2014 [6].

A machine-readable BibTeX entry can be generated from `CITATION.cff`
with [`cffconvert`](https://github.com/citation-file-format/cffconvert):

```bash
pip install cffconvert
cffconvert --infile CITATION.cff -f bibtex
```

---

## 14. License

MIT. See `LICENSE`. Before redistributing modified geometry or hydro
data, confirm that any upstream licences (OC4 specification, 5 MW
reference turbine, WEC-Sim examples) permit your particular use case.
