%% ========================================================================
%% USER CONFIGURATION - POST-PROCESSING & VISUALIZATION
%% ========================================================================

% --- Output Identification ---
platformType = 'hollow4m';              % e.g., 'hollow4m', 'base_model'
seaState     = 'reg_ss4';               % e.g., 'reg_ss4', 'irr_ss3'
filePrefix   = [platformType, '_', seaState];

% --- Output Directory ---
% Change this to your preferred absolute path if needed.
savePath     = fullfile(pwd, 'output_figures'); 

% --- Execution Toggles ---
saveFigures  = true;   % Set to false to skip 2D plotting and saving
runViz       = true;   % Set to false to skip 3D saveViz animation

% --- Plotting Defaults ---
plotStartTime = 100;   % [s] Start time for the PTO power plot x-axis

% --- WEC-Sim Visualization (saveViz) Settings ---
viz_timesPerFrame = 24;                       % Frames per second of simulation output
viz_startEndTime  = [100 220];                % [start_time end_time] in seconds
viz_axisLimits    = [-75 75 -75 75 -40 40];   % [X_min X_max Y_min Y_max Z_min Z_max]


%% ========================================================================
%% EXECUTION & PLOTTING
%% ========================================================================

if saveFigures
    % Create output directory if it doesn't exist
    if ~exist(savePath, 'dir')
        mkdir(savePath);
    end
    
    disp(['Saving post-processing figures to: ', savePath]);

    % --- 1. Wave Plots ---
    waves.plotElevation(simu.rampTime);
    saveas(gcf, fullfile(savePath, ['elevation_', filePrefix, '.fig']));
    
    try 
        waves.plotSpectrum();
        saveas(gcf, fullfile(savePath, ['spectrum_', filePrefix, '.fig']));
    catch
        disp('Wave spectrum plot skipped (expected for regular waves).');
    end

    % --- 2. Hydrodynamic Force Plots ---
    % 1-surge, 2-sway, 3-heave, 4-roll, 5-pitch, 6-yaw
    output.plotForces(1,1); saveas(gcf, fullfile(savePath, ['surge_force_', filePrefix, '.fig']));
    output.plotForces(1,2); saveas(gcf, fullfile(savePath, ['sway_force_', filePrefix, '.fig']));
    output.plotForces(1,3); saveas(gcf, fullfile(savePath, ['heave_force_', filePrefix, '.fig']));
    output.plotForces(1,4); saveas(gcf, fullfile(savePath, ['roll_force_', filePrefix, '.fig']));
    output.plotForces(1,5); saveas(gcf, fullfile(savePath, ['pitch_force_', filePrefix, '.fig']));

    % --- 3. Body Response Plots (Body 1) ---
    output.plotResponse(1,1); saveas(gcf, fullfile(savePath, ['surge_response_', filePrefix, '.fig']));
    output.plotResponse(1,2); saveas(gcf, fullfile(savePath, ['sway_response_', filePrefix, '.fig']));
    output.plotResponse(1,3); saveas(gcf, fullfile(savePath, ['heave_response_', filePrefix, '.fig']));
    output.plotResponse(1,4); saveas(gcf, fullfile(savePath, ['roll_response_', filePrefix, '.fig']));
    output.plotResponse(1,5); saveas(gcf, fullfile(savePath, ['pitch_response_', filePrefix, '.fig']));

    % --- 4. Power Take-Off (PTO) Plot ---
    % Safely checks if Simulink actually exported these variables to the workspace
    if exist('controller1_out', 'var') && exist('controller2_out', 'var')
        figure; hold on; grid on;
        
        plot(controller1_out.time, controller1_out.signals.values(:, 9), 'LineWidth', 1.5);
        plot(controller1_out.time, controller2_out.signals.values(:, 9), 'LineWidth', 1.5);
        
        % Check if PTO 3 exists and plot it, otherwise just group 2 & 3
        if exist('controller3_out', 'var')
            plot(controller3_out.time, controller3_out.signals.values(:, 9), 'LineWidth', 1.5);
            legend('PTO 1', 'PTO 2', 'PTO 3');
        else
            legend('PTO 1', 'PTO 2 and 3');
        end
        
        title('Power Take-Off (PTO) Power');
        xlabel('Time (s)');
        ylabel('Power (W)');
        xlim([plotStartTime, controller1_out.time(end)]);
        hold off;
        
        saveas(gcf, fullfile(savePath, ['pto_power_', filePrefix, '.fig']));
    else
        disp('PTO output variables (controller1_out, etc.) not found in workspace. Skipping PTO plot.');
    end
end

% --- 5. 3D WEC-Sim Visualization ---
if runViz
    disp('Running WEC-Sim 3D Visualization (saveViz)...');
    output.saveViz(simu, body, waves, ...
        'timesPerFrame', viz_timesPerFrame, ...
        'startEndTime', viz_startEndTime, ...
        'axisLimits', viz_axisLimits);
end
