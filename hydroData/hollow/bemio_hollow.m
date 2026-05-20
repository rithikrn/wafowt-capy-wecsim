%% BEMIO post-processing for the hollow OWC case.
clear; clc; close all;

thisDir = fileparts(mfilename('fullpath'));
ncFile  = fullfile(thisDir, 'hollow.nc');

hydro = struct();
hydro = readCAPYTAINE(hydro, ncFile, thisDir);
hydro = radiationIRF(hydro, 60, [], [], [], 1.9);
hydro = radiationIRFSS(hydro, [], []);
hydro = excitationIRF(hydro, 60, [], [], [], 1.9);

hydro.file = fullfile(thisDir, 'hollow.h5');
writeBEMIOH5(hydro);
% plotBEMIO(hydro);
fprintf('Wrote: %s\n', hydro.file);
