# OC4 4 m hollow OWC case

This folder contains the selected hollow OWC-integrated case. The offset columns are hollowed to form three OWC chambers, and the internal water columns are represented as piston bodies.

## Run order

1. Optional Capytaine re-solve:
   ```bash
   python capytaine/run_capytaine_oc4_hollow_owc_4m.py --overwrite
   ```
2. Optional BEMIO conversion in MATLAB:
   ```matlab
   cd cases/oc4_hollow_owc_4m/bemio
   bemio_oc4_hollow_owc_4m
   ```
3. WEC-Sim:
   ```matlab
   cd cases/oc4_hollow_owc_4m
   wecSim
   ```

## Case identity

- Hydrodynamic bodies: one hollow platform shell plus three OWC piston bodies.
- WEC-Sim body order: platform, front piston, rear-port piston, rear-starboard piston.
- PTOs: three translational PTOs at the chamber centroids.
- Default wave mode: regular SS4; commented blocks are included for regular SS3, PM irregular SS3, and no-wave decay.
- Hydrodynamic file used by WEC-Sim: `hydroData/oc4_hollow_owc_4m_wecsim.h5`.

The included passive-restriction proxy is controlled by `orificeDiameter` in `wecSimInputFile.m`.
