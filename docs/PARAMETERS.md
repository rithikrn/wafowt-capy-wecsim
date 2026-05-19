# Main parameters

## Common BEM parameters

| Parameter | Value |
|---|---:|
| Frequency range | 0.02 to 3.0 rad/s |
| Frequency count | 150 |
| Water depth | 200 m |
| Water density | 1025 kg/m³ |
| Wave heading | 0 rad in the provided scripts |

## Baseline case

| Parameter | Value |
|---|---:|
| Hydrodynamic bodies | 1 |
| Default WEC-Sim wave | `noWaveCIC` |
| Baseline heave restoring proxy | 3,745,330 N/m |
| Baseline inertia vector | `[1.3813e10, 1.3813e10, 1.2287e10]` kg m² |

## 4 m hollow OWC case

| Parameter | Value |
|---|---:|
| Hydrodynamic bodies | 4 |
| OWC chamber inner diameter | 4.0 m |
| OWC chamber area | 12.5664 m² |
| OWC chamber centroids | `[-28.868,0,-10]`, `[14.434,25,-10]`, `[14.434,-25,-10]` |
| Hollow heave restoring proxy | 3,366,256 N/m |
| Default orifice diameter | 2.0 m |

## Passive-orifice sweep

| Orifice diameter | Area ratio Λ = A_col/A_orifice |
|---:|---:|
| 0.25 m | 256 |
| 0.50 m | 64 |
| 1.00 m | 16 |
| 2.00 m | 4 |
