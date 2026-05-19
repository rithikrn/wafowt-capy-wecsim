# File audit and editing decisions

This audit records how the uploaded files were interpreted and renamed.

## Baseline files added in this revision

### `fowt_med_MS_v2_withoutpto.py`

Interpretation: baseline FOWT without OWC and without PTO. Evidence in the original file:

- the file comment states that it is for the FOWT without OWC and PTO;
- only one center of gravity is active;
- OWC water-column body generation is commented out;
- the active body name is `FOWT_base`;
- the output NetCDF name is the baseline no-PTO file.

Repository action:

- renamed to `cases/oc4_baseline_no_owc/capytaine/run_capytaine_oc4_baseline_no_owc.py`;
- replaced `import capy_call2 as cc` with the reusable package runner `owc_fowt_hydro.capytaine_runner`;
- removed unused/debug imports;
- changed output path to `hydroData/oc4_baseline_capytaine.nc`;
- kept one hydrodynamic body only.

### `wecSimInputFile.m` for baseline

Interpretation: baseline WEC-Sim setup, single platform body, no active PTO.

Repository action:

- retained the one-body structure;
- renamed the model reference to `oc4_baseline_no_owc_wecsim.slx`;
- renamed the hydrodynamic file reference to `hydroData/oc4_baseline_wecsim.h5`;
- moved the geometry reference to `geometry/oc4_semisubmersible_baseline_cg.stl`;
- set `simu.explorer = 'off'` for non-interactive reproducibility;
- kept the no-wave decay default, with commented regular and PM irregular options.

### `userDefinedFunctions.m`

Interpretation: optional WEC-Sim post-processing with a hard-coded local Windows save path.

Repository action:

- removed the user-specific path;
- created `results/figures/` automatically under the active case directory;
- wrapped plotting calls in `try/catch` so regular, irregular, and no-wave cases do not fail just because a plot type is unavailable;
- kept visualization export disabled by default because it can be slow.

### `.h5` and `.nc` files

Repository action:

- copied and renamed only;
- did not parse, edit, or regenerate their internal contents.

## Hollow case retained from previous cleanup

The hollow case remains the multi-body OWC model: one hollow platform shell plus three OWC piston bodies. Its Capytaine, BEMIO, WEC-Sim, geometry, and hydroData files were renamed to match the new repository naming convention.

## Binary Simulink files

The `.slx` files were copied and renamed for discoverability. Their binary contents were not modified. Any block-level changes should be made directly in MATLAB/Simulink.
