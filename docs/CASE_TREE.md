# Case tree and purpose

```text
wafowt-capy-wecsim/
|-- README.md
|-- LICENSE
|-- environment.yml                  conda environment (recommended)
|-- requirements.txt                 pip alternative
|-- .gitignore
|
|-- capytaine/                       STAGE 2: Python BEM drivers
|   |-- capytaine_call.py            shared helpers (mesh, body, solver, export)
|   |-- wafowt_capy_base.py          baseline driver (1 body, 6 DOF)
|   `-- wafowt_capy_hollow.py        hollow driver  (4 bodies, 9 DOF)
|
|-- geometry/                        STAGE 1: surface meshes
|   |-- base.stl                     baseline OC4 wetted surface (CG-aligned)
|   |-- hollow.stl                   hollow shell                (CG-aligned)
|   |-- owc.stl                      OWC piston visualisation mesh
|   `-- lid.gdf                      Lid mesh for suppressing irregular frequencies
|
|-- hydroData/                       STAGE 2 outputs + STAGE 3 scripts/outputs
|   |-- base/
|   |   |-- bemio_base.m             BEMIO post-processor
|   |   |-- base.nc                  Capytaine output    (created by stage 2)
|   |   `-- base.h5                  WEC-Sim hydro data  (created by stage 3)
|   `-- hollow/
|       |-- bemio_hollow.m
|       |-- hollow.nc
|       `-- hollow.h5
|
|-- wecsim/                          STAGE 4: time-domain simulation
|   |-- wecSimInputFile.m            generic input file, switches on caseType
|   |-- userDefinedFunctions.m       generic post-processor
|   |-- wafowt_base.slx              baseline Simulink model
|   `-- wafowt_hollow.slx            hollow with OWC Simulink model
|
`-- docs/                            Additional Detailed Documentation
    |-- METHOD_THEORY.md             Mathematical theory & thermodynamic formulas
    |-- PARAMETERS.md                Mass, inertia, and dimensional parameters
    |-- CASE_TREE.md                 Hierarchical breakdown of load cases
    |-- ADD_BASE_GEOMETRY_CHECKLIST.md
    |-- FILE_AUDIT.md
    |-- OFFICIAL_DOC_REFERENCES.md
    `-- media/
        |-- images/                  figures used in this README
        `-- videos/                  simulation animations (.gif)
```

## Baseline case

The baseline case is a one-body, no-OWC, no-PTO reference. Use it for free decay, regular waves, or irregular waves when comparing against the hollow case.

## Hollow OWC case

The hollow case is a four-body hydrodynamic model. WEC-Sim body order must remain synchronized with Capytaine body order:

1. hollow platform shell,
2. OWC piston 1 at `(-28.868, 0, -10)`,
3. OWC piston 2 at `(14.434, 25, -10)`,
4. OWC piston 3 at `(14.434, -25, -10)`.
