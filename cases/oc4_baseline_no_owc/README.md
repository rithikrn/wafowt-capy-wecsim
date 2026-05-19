# OC4 baseline no-OWC/no-PTO case

This folder contains the solid baseline semisubmersible reference case. It is the control case used to compare the effect of hollowing the offset columns into OWC chambers.

## Run order

1. Optional Capytaine re-solve:
   ```bash
   python capytaine/run_capytaine_oc4_baseline_no_owc.py --overwrite
   ```
2. Optional BEMIO conversion in MATLAB:
   ```matlab
   cd cases/oc4_baseline_no_owc/bemio
   bemio_oc4_baseline_no_owc
   ```
3. WEC-Sim:
   ```matlab
   cd cases/oc4_baseline_no_owc
   wecSim
   ```

## Case identity

- Hydrodynamic bodies: one platform body.
- OWC bodies: none.
- PTOs: none.
- Default wave mode: `noWaveCIC`, suitable for free-decay tests.
- Hydrodynamic file used by WEC-Sim: `hydroData/oc4_baseline_wecsim.h5`.

The uploaded baseline `.h5` and `.nc` files were copied and renamed only; their internal contents were not modified.
