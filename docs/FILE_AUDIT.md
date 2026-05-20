# File Audit and editing decisions

This audit records how the original, disparate script files utilized during the thesis research were interpreted, refactored, and consolidated into the current clean, 4-stage reproducible pipeline.

## 1. Capytaine BEM Scripts (Stage 2)

### Original Baseline Script 
* **Interpretation:** The baseline FOWT solver script without OWC chambers and without PTO dynamics. Only one center of gravity is active, and OWC water-column generation is commented out.
* **Repository Action:**
  * Renamed and moved to `capytaine/wafowt_capy_base.py`.
  * Abstracted the repetitive Capytaine solver routines (mesh generation, lid application, and solver setup) into a single shared helper module: `capytaine/capytaine_call.py`.
  * Hardcoded the output path to drop the NetCDF file directly into `hydroData/base/base.nc`.
  * Maintained strictly as a 1-body, 6-DOF system.

### Original Hollow Script
* **Interpretation:** The multi-body OWC model representing the hollowed platform shell plus three internal OWC piston bodies. 
* **Repository Action:**
  * Renamed to `capytaine/wafowt_capy_hollow.py`.
  * Refactored to utilize the same `capytaine_call.py` helpers.
  * Ensures a 4-body, 9-DOF coupled radiation/diffraction solve, outputting to `hydroData/hollow/hollow.nc`.

## 2. WEC-Sim Configuration (Stage 4)

### `wecSimInputFile.m`
* **Interpretation:** Originally, separate input files existed for the baseline and hollow cases, leading to duplicate wave and simulation parameter definitions. 
* **Repository Action:**
  * **Consolidated** into a single, unified `wecsim/wecSimInputFile.m`.
  * Introduced a programmatic `caseType = 'base'` or `'hollow'` switch at the top of the file. This switch dynamically controls which `.h5` hydrodynamic file is loaded, which `.slx` Simulink model is called, and whether multi-body dynamics (`simu.b2b = 1`) and PTO blocks are initialized.
  * Standardized geometry references to point cleanly to `../geometry/base.stl` and `../geometry/hollow.stl`.
  * Set `simu.explorer = 'off'` as the default for non-interactive batch reproducibility, though it can easily be toggled on.

### Binary Simulink Files (`.slx`)
* **Interpretation:** The core block-diagram physics models for WEC-Sim. 
* **Repository Action:**
  * Renamed for clear discoverability to `wafowt_base.slx` (single body) and `wafowt_hollow.slx` (multi-body with translational PTOs). 
  * Their binary block structures were not fundamentally modified; any internal parameter changes should be driven by the `wecSimInputFile.m` workspace variables.

## 3. Post-Processing Scripts

### `userDefinedFunctions.m`
* **Interpretation:** Optional WEC-Sim post-processing script that historically contained a hard-coded local Windows save path (e.g., `C:\Users\...`).
* **Repository Action:**
  * Removed the user-specific, hard-coded path.
  * Implemented dynamic folder generation: results and plots are now automatically saved to `results/figures/<caseType>/<seaState>/` directly within the `wecsim/` directory.
  * Wrapped plotting functions in `try/catch` blocks so that missing variables (e.g., trying to plot PTO power on the base case, or wave spectrums on a regular wave) do not crash the post-processing execution.

## 4. Geometry & Hydrodynamic Data

### STL Meshes
* **Repository Action:** Renamed verbose original files (e.g., `oc4_semisubmersible_baseline_cg.stl`) to simplified, explicit names (`base.stl`, `hollow.stl`, `owc.stl`) housed inside the `geometry/` folder.

### BEMIO Post-processors (`.m`, `.nc`, `.h5`)
* **Repository Action:** Split the BEMIO scripts cleanly into `hydroData/base/bemio_base.m` and `hydroData/hollow/bemio_hollow.m` to prevent accidental cross-contamination of the `.h5` outputs.
