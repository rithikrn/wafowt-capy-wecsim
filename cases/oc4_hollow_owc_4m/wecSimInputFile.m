%% WEC-Sim input file: 4 m hollow OWC-integrated OC4 semisubmersible
% Run command:
%   cd cases/oc4_hollow_owc_4m
%   wecSim
%
% This case keeps the platform shell and the three OWC internal water-column
% pistons as separate WEC-Sim bodies. The translational PTOs provide the
% linearized passive restriction proxy used in the reduced-order study.

%% Simulation Data
simu = simulationClass();
simu.simMechanicsFile = 'oc4_hollow_owc_4m_wecsim.slx';
simu.mode = 'normal';
simu.explorer = 'off';
simu.startTime = 0;
simu.rampTime  = 50;
simu.endTime   = 500;
simu.dt        = 0.01;
simu.solver    = 'ode45';
simu.b2b       = 1;      % body-to-body hydrodynamic coupling

%% Wave definition
% Default: regular SS4. Use the commented blocks below for decay or SS3.
waves = waveClass('regular');
waves.height = 5.49;
waves.period = 11.3;
waves.waterDepth = 200;

% % Regular SS3
% waves = waveClass('regular');
% waves.height = 2.44;
% waves.period = 8.1;
% waves.waterDepth = 200;

% % PM irregular SS3 with fixed phase seed
% waves = waveClass('irregular');
% waves.height = 2.44;
% waves.period = 8.1;
% waves.spectrumType = 'PM';
% waves.direction = 0;
% waves.phaseSeed = 12345;
% waves.waterDepth = 200;

% % No-wave free decay
% waves = waveClass('noWaveCIC');
% waves.waterDepth = 200;

%% Body Data
hydroFile = 'hydroData/oc4_hollow_owc_4m_wecsim.h5';

% Body 1: hollow platform shell
body(1) = bodyClass(hydroFile);
body(1).geometryFile = 'geometry/oc4_hollow_owc_4m_cg.stl';
body(1).mass         = 13025700;                       % [kg], preserved from uploaded WEC-Sim case
body(1).inertia      = [1.106e10, 1.106e10, 1.173e10]; % [kg*m^2]
body(1).initial.displacement = [0, 0, 0.2];

% Bodies 2-4: OWC internal water-column piston bodies
for iBody = 2:4
    body(iBody) = bodyClass(hydroFile); %#ok<SAGROW>
    body(iBody).geometryFile = 'geometry/owc_piston_4m.stl';
    body(iBody).mass         = 'equilibrium';
    body(iBody).inertia      = [1.345e8, 1.345e8, 1.875e8];
    body(iBody).initial.displacement = [0, 0, 0];
end

%% Constraint
constraint(1) = constraintClass('Constraint1');
constraint(1).location = [0, 0, -9.885];

%% Linearized mooring / vertical restoring proxy
mooring(1) = mooringClass('mooring1');
mooring(1).matrix.stiffness = zeros(6,6);
mooring(1).matrix.stiffness(3,3) = 3366256;       % C33 for 4 m hollow case [N/m]
mooring(1).matrix.damping = zeros(6,6);
mooring(1).matrix.damping(3,3) = 662177;          % nominal 5% critical [N*s/m]
mooring(1).matrix.preTension = [0, 0, 362117, 0, 0, 0];

%% OWC/PTO passive restriction proxy
rho_w = 1025;               % [kg/m^3]
g = 9.81;                   % [m/s^2]
D_col = 4.0;                % [m], chamber inner diameter
A_col = pi * D_col^2 / 4;   % [m^2]
K_wc = rho_w * g * A_col;   % [N/m], water-column hydrostatic stiffness proxy

orificeDiameter = 2.0;      % [m]; change to 0.25/0.50/1.00/2.00 for passive sweep
Cd_orifice = 0.6466;        % [-], discharge coefficient
rho_air = 1.2;              % [kg/m^3]

ptoCoefficient = (8 * rho_air * A_col^3) / (pi^2 * Cd_orifice^2 * orificeDiameter^4);

owcLocations = [
    -28.868,   0.0, -10.0;
     14.434,  25.0, -10.0;
     14.434, -25.0, -10.0
];

for iPto = 1:3
    pto(iPto) = ptoClass(sprintf('PTO%d', iPto)); %#ok<SAGROW>
    pto(iPto).stiffness = K_wc;
    pto(iPto).damping = ptoCoefficient;
    pto(iPto).location = owcLocations(iPto, :);
end
