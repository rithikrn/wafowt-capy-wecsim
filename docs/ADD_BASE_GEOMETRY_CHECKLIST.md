# Adding or replacing exact baseline geometry files

The baseline case currently includes a baseline STL from the uploaded workflow archive. If you have a more exact baseline geometry set, replace files carefully:

1. Replace the Capytaine BEM mesh:
   ```text
   cases/oc4_baseline_no_owc/geometry/oc4_semisubmersible_baseline_bem.stl
   ```
2. Replace the WEC-Sim visualization/CG mesh:
   ```text
   cases/oc4_baseline_no_owc/geometry/oc4_semisubmersible_baseline_cg.stl
   ```
3. If the baseline Capytaine solve uses a lid mesh, add:
   ```text
   cases/oc4_baseline_no_owc/geometry/oc4_semisubmersible_baseline_lid.gdf
   ```
   The baseline Capytaine driver automatically uses this file if it exists.
4. Re-run Capytaine.
5. Re-run BEMIO.
6. Re-run WEC-Sim.

Do not overwrite the hollow OWC geometry with baseline geometry. The two cases are intentionally separated.
