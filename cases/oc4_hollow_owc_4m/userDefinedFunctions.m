%% Optional WEC-Sim post-processing: 4 m hollow OWC case
% Path-safe replacement for the uploaded userDefinedFunctions.m.
% WEC-Sim calls this file after the run if it is present in the case folder.

caseDir = fileparts(mfilename('fullpath'));
resultsDir = fullfile(caseDir, 'results', 'figures');
if ~exist(resultsDir, 'dir')
    mkdir(resultsDir);
end

platformType = 'oc4_hollow_owc_4m';
seaState = 'active_case';
filePrefix = [platformType, '_', seaState];

try
    waves.plotElevation(simu.rampTime);
    saveas(gcf, fullfile(resultsDir, ['wave_elevation_', filePrefix, '.fig']));
catch ME
    warning('Wave elevation plot skipped: %s', ME.message);
end

try
    waves.plotSpectrum();
    saveas(gcf, fullfile(resultsDir, ['wave_spectrum_', filePrefix, '.fig']));
catch
    % Regular-wave and no-wave cases may not have a spectrum plot.
end

% DOF convention: 1 surge, 2 sway, 3 heave, 4 roll, 5 pitch, 6 yaw
plotRequests = {
    'pitch_force',    @() output.plotForces(1,5);
    'surge_force',    @() output.plotForces(1,1);
    'roll_force',     @() output.plotForces(1,4);
    'sway_force',     @() output.plotForces(1,2);
    'heave_force',    @() output.plotForces(1,3);
    'pitch_response', @() output.plotResponse(1,5);
    'surge_response', @() output.plotResponse(1,1);
    'sway_response',  @() output.plotResponse(1,2);
    'heave_response', @() output.plotResponse(1,3);
    'roll_response',  @() output.plotResponse(1,4)
};

for iPlot = 1:size(plotRequests, 1)
    try
        plotRequests{iPlot, 2}();
        saveas(gcf, fullfile(resultsDir, [plotRequests{iPlot, 1}, '_', filePrefix, '.fig']));
    catch ME
        warning('Plot skipped (%s): %s', plotRequests{iPlot, 1}, ME.message);
    end
end

% Optional visualization export. Keep this off by default because it can be slow.
makeViz = false;
if makeViz
    output.saveViz(simu, body, waves, ...
        'timesPerFrame', 24, ...
        'startEndTime', [100 220], ...
        'axisLimits', [-75 75 -75 75 -40 40]);
end
