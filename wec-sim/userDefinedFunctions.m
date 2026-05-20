%% Post-processing: figures -> results/figures/<caseType>/<seaState>/
if ~exist('caseType','var'); caseType = 'unknown'; end
if exist('waves','var') && isa(waves,'waveClass')
    switch lower(waves.type)
        case {'regular','regularcic'}, seaState = sprintf('reg_H%.2f_T%.2f',  waves.height, waves.period);
        case 'irregular',              seaState = sprintf('irr_Hs%.2f_Tp%.2f', waves.height, waves.period);
        case {'nowavecic','nowave'},   seaState = 'decay';
        otherwise,                     seaState = waves.type;
    end
else
    seaState = 'run';
end
filePrefix = sprintf('%s_%s', caseType, seaState);
savePath   = fullfile(pwd, 'results', 'figures', caseType, seaState);
if ~exist(savePath,'dir'); mkdir(savePath); end

try, waves.plotElevation(simu.rampTime); saveas(gcf, fullfile(savePath, ['elevation_' filePrefix '.fig'])); catch, end
try, waves.plotSpectrum();               saveas(gcf, fullfile(savePath, ['spectrum_'  filePrefix '.fig'])); catch, end

dofNames = {'surge','sway','heave','roll','pitch','yaw'};
for dof = 1:6
    try, output.plotForces(1, dof);   saveas(gcf, fullfile(savePath, [dofNames{dof} '_force_'    filePrefix '.fig'])); catch, end
    try, output.plotResponse(1, dof); saveas(gcf, fullfile(savePath, [dofNames{dof} '_response_' filePrefix '.fig'])); catch, end
end

if strcmpi(caseType, 'hollow')
    try
        figure; hold on; grid on;
        if exist('controller1_out','var'), plot(controller1_out.time, controller1_out.signals.values(:, 9)); end
        if exist('controller2_out','var'), plot(controller2_out.time, controller2_out.signals.values(:, 9)); end
        if exist('controller3_out','var'), plot(controller3_out.time, controller3_out.signals.values(:, 9)); end
        title('PTO Power'); xlabel('Time (s)'); ylabel('Power (W)');
        legend('PTO 1','PTO 2','PTO 3','Location','best');
        if exist('controller1_out','var'), xlim([simu.rampTime, controller1_out.time(end)]); end
        hold off;
        saveas(gcf, fullfile(savePath, ['pto_power_' filePrefix '.fig']));
    catch, end
end

% Optional 3D animation
saveAnimation = false;
if saveAnimation
    try
        output.saveViz(simu, body, waves, ...
            'timesPerFrame', 24, 'startEndTime', [100, min(220, simu.endTime)], ...
            'axisLimits',    [-75 75 -75 75 -40 40]);
    catch ME, warning('saveViz failed: %s', ME.message); end
end

fprintf('Figures: %s\n', savePath);
