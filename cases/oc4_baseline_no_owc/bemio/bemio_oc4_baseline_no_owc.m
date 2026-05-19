%% BEMIO preprocessing for OC4 baseline no-OWC/no-PTO case
% Run from: cases/oc4_baseline_no_owc/bemio
% Requires WEC-Sim/BEMIO on the MATLAB path.

clear; clc;

caseDir = fileparts(fileparts(mfilename('fullpath')));
hydroDir = fullfile(caseDir, 'hydroData');
capyFile = fullfile(hydroDir, 'oc4_baseline_capytaine.nc');
outputBaseName = fullfile(hydroDir, 'oc4_baseline_wecsim');

if ~isfile(capyFile)
    error('Capytaine NetCDF not found: %s', capyFile);
end

hydro = struct();
hydro = readCAPYTAINE(hydro, capyFile);
hydro = cleanBEM(hydro, []);

hydro = radiationIRF(hydro, 60, [], [], [], 1.9);
hydro = radiationIRFSS(hydro, [], []);
hydro = excitationIRF(hydro, 157, [], [], [], 1.9);

hydro.file = outputBaseName;
writeBEMIOH5(hydro);
plotBEMIO(hydro);

fprintf('WEC-Sim H5 written to: %s.h5\n', outputBaseName);
