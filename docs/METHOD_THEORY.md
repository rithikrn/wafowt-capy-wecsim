# Method and theory notes

This repository implements a reduced-order hydrodynamic workflow. It does not include the OpenFOAM CFD cases.

## Frequency-domain BEM

For each body or multi-body system, the Capytaine step solves the linear radiation and diffraction problems over a user-defined frequency grid. The resulting data include added mass, radiation damping, excitation forces, and hydrostatic quantities.

The baseline case has six platform rigid-body DOFs. The hollow OWC case is represented by one platform body and three additional piston bodies, giving a body-to-body hydrodynamic model that captures coupling among the platform and internal OWC water-column modes.

## BEMIO conversion

BEMIO converts the frequency-domain BEM data into time-domain-compatible hydrodynamic data. The key outputs are:

- radiation impulse-response functions,
- excitation impulse-response functions,
- radiation state-space coefficients,
- a WEC-Sim-ready HDF5 file.

## Time-domain WEC-Sim model

The WEC-Sim equation-of-motion structure is assembled from the HDF5 hydrodynamic data, WEC-Sim body objects, constraints, mooring/restoring proxies, and optional PTO elements. The case can be used for:

- no-wave free decay,
- regular-wave response,
- PM irregular-wave response.

## Interpreting results

- Free decay: extract natural period and damping from response peaks.
- Regular waves: compare steady-state peak or peak-to-peak response at one wave period.
- Irregular waves: use the same phase seed across cases for fair deterministic case ranking.
- OWC sweep: compare motion reduction, force/moment response, and pneumatic power trends.
