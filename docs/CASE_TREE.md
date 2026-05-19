# Case tree and purpose

```text
cases/
├── oc4_baseline_no_owc/
│   ├── capytaine/
│   │   └── run_capytaine_oc4_baseline_no_owc.py
│   ├── bemio/
│   │   └── bemio_oc4_baseline_no_owc.m
│   ├── geometry/
│   │   ├── oc4_semisubmersible_baseline_bem.stl
│   │   └── oc4_semisubmersible_baseline_cg.stl
│   ├── hydroData/
│   │   ├── oc4_baseline_capytaine.nc
│   │   └── oc4_baseline_wecsim.h5
│   ├── oc4_baseline_no_owc_wecsim.slx
│   ├── wecSimInputFile.m
│   └── userDefinedFunctions.m
└── oc4_hollow_owc_4m/
    ├── capytaine/
    │   └── run_capytaine_oc4_hollow_owc_4m.py
    ├── bemio/
    │   └── bemio_oc4_hollow_owc_4m.m
    ├── geometry/
    │   ├── oc4_hollow_owc_4m_bem.stl
    │   ├── oc4_hollow_owc_4m_cg.stl
    │   └── owc_piston_4m.stl
    ├── hydroData/
    │   ├── oc4_hollow_owc_4m_capytaine.nc
    │   └── oc4_hollow_owc_4m_wecsim.h5
    ├── oc4_hollow_owc_4m_wecsim.slx
    ├── wecSimInputFile.m
    └── userDefinedFunctions.m
```

## Baseline case

The baseline case is a one-body, no-OWC, no-PTO reference. Use it for free decay, regular waves, or irregular waves when comparing against the hollow case.

## Hollow OWC case

The hollow case is a four-body hydrodynamic model. WEC-Sim body order must remain synchronized with Capytaine body order:

1. hollow platform shell,
2. OWC piston 1 at `(-28.868, 0, -10)`,
3. OWC piston 2 at `(14.434, 25, -10)`,
4. OWC piston 3 at `(14.434, -25, -10)`.
