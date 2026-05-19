%% WEC-Sim input file: OC4 baseline semisubmersible, no OWC, no PTO
% Run command:
%   cd cases/oc4_baseline_no_owc
%   wecSim
%
% This file is the cleaned version of the uploaded baseline WEC-Sim input.
% It is intentionally a single-body reference case. The uploaded script used
% noWaveCIC by default and had all OWC/PTO lines commented; that structure is
% preserved here, but paths and names are made repository-safe.

%% Simulation Data
simu = simulationClass();
simu.simMechanicsFile = 'oc4_baseline_no_owc_wecsim.slx';
simu.mode = 'normal';
simu.explorer = 'off';
simu.startTime = 0;
simu.rampTime = 50;
simu.endTime = 500;
simu.solver = 'ode45';
simu.dt = 0.01;

%% Wave definition
% Default: no waves with radiation convolution initialization for decay tests.
waves = waveClass('noWaveCIC');
waves.waterDepth = 200;

% % Regular SS3
% waves = waveClass('regular');
% waves.height = 2.44;
% waves.period = 8.1;
% waves.waterDepth = 200;

% % PM irregular SS3 with fixed phase seed
% waves = waveClass('irregular');
% waves.height = 2.44;         % significant wave height Hs [m]
% waves.period = 8.1;          % peak period Tp [s]
% waves.spectrumType = 'PM';
% waves.direction = 0;
% waves.phaseSeed = 12345;
% waves.waterDepth = 200;

%% Body Data
hydroFile = 'hydroData/oc4_baseline_wecsim.h5';

body(1) = bodyClass(hydroFile);
body(1).geometryFile = 'geometry/oc4_semisubmersible_baseline_cg.stl';

% Preserved from the uploaded baseline WEC-Sim file. Replace with the exact
% full-system mass if your calibration uses the complete tower/RNA mass.
body(1).mass = 1.37e7;
body(1).inertia = [1.3813e10, 1.3813e10, 1.2287e10];
body(1).initial.displacement = [0, 0, 0.2];

%% Constraint and linearized vertical restoring proxy
constraint(1) = constraintClass('FreeFloating');
constraint(1).location = [0, 0, -9.893];

mooring(1) = mooringClass('mooring1');
mooring(1).matrix.stiffness = zeros(6,6);
mooring(1).matrix.stiffness(3,3) = 3745330;       % baseline C33 [N/m]
mooring(1).matrix.damping = zeros(6,6);
mooring(1).matrix.damping(3,3) = 716317;          % nominal 5% critical [N*s/m]
mooring(1).matrix.preTension = [0, 0, 0, 0, 0, 0];

% No PTO is defined in the baseline reference case.
