%% BEMIO preprocessing for 4 m hollow OWC-integrated OC4 case
% Run from: cases/oc4_hollow_owc_4m/bemio
% Requires WEC-Sim/BEMIO on the MATLAB path.

clear; clc;

caseDir = fileparts(fileparts(mfilename('fullpath')));
hydroDir = fullfile(caseDir, 'hydroData');
capyFile = fullfile(hydroDir, 'oc4_hollow_owc_4m_capytaine.nc');
outputBaseName = fullfile(hydroDir, 'oc4_hollow_owc_4m_wecsim');

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
