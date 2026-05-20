# Adding or Swapping Custom Platform Geometry

This workflow is entirely platform-agnostic. While it defaults to the NLR OC4 DeepCwind semisubmersible, you can seamlessly swap the geometry to model a completely different platform (e.g., VolturnUS, OC3, or a custom proprietary design).

If you are adapting this repository to a new platform or possess a higher-fidelity geometry set, follow these steps carefully to ensure hydrodynamic consistency across all four stages of the pipeline:

### 1. Replace the Wetted Surface Meshes
Over-write the default `.stl` files in the `geometry/` directory. 
> **Crucial WEC-Sim Requirement:** All `.stl` meshes must be appropriately triangulated and their coordinate origins **must be exactly co-located at the platform's Center of Gravity (CG)**.

* **Baseline Platform (No OWC):** Replace `geometry/base.stl`
* **Hollowed Platform Shell (For OWC):** Replace `geometry/hollow.stl`
* **OWC Internal Water Column Piston:** Replace `geometry/owc.stl`

### 2. Handle the Lid Mesh (Optional but Recommended)
To suppress irregular frequencies during the Capytaine boundary-element solve, a lid mesh at the still water line is highly recommended. 
* Replace or add your custom lid file at: `geometry/lid.gdf`

*(Note: If a custom lid mesh is not provided, the Capytaine execution scripts are configured to automatically generate a flat lid mesh at $z = 0$.)*

### 3. Update the Physical Parameters
Swapping geometry invalidates the default mass properties. You must update the mathematical parameters to match your new platform's volume and mass distribution:
* **Capytaine setup:** Update the `CENTER_OF_MASS` and (if applicable) `CHAMBER_DIAMETER` coordinates in `capytaine/wafowt_capy_base.py` and `capytaine/wafowt_capy_hollow.py`.
* **WEC-Sim setup:** Open `wecsim/wecSimInputFile.m` and replace the mass, moments of inertia, and mooring stiffness parameters. (Refer to `docs/PARAMETERS.md` for the exact matrix layouts required).

### 4. Execute the Full Pipeline
Because the platform's wetted surface has changed, the previous frequency-domain coefficients and impulse response functions are no longer valid. You must re-run the chain in this exact order:

1. **Stage 2 (BEM):** Re-run Capytaine (`python capytaine/wafowt_capy_base.py` and `wafowt_capy_hollow.py`).
2. **Stage 3 (BEMIO):** Open MATLAB and re-run the post-processors (`bemio_base.m` and `bemio_hollow.m`) to generate the new WEC-Sim `.h5` files.
3. **Stage 4 (Time-Domain):** Run `wecSim` to visualize your new platform.

---
**⚠️ Important Architecture Warning**
Do not overwrite the `hollow.stl` with your `base.stl` geometry. The two configurations are deliberately isolated. The `base` case operates on a standard 6-DOF single-body matrix, whereas the `hollow` case initializes a 9-DOF multi-body solver incorporating the pneumatic PTO couplings. Mixing them will cause fatal dimension-mismatch errors in WEC-Sim.
