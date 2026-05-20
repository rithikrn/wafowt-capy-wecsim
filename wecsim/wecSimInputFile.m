%% Case Selection
caseType = 'hollow';                  % 'base' or 'hollow'

%% Simulation Data
simu = simulationClass();
switch lower(caseType)
    case 'base',   simu.simMechanicsFile = 'wafowt_base.slx';
    case 'hollow', simu.simMechanicsFile = 'wafowt_hollow.slx';
end
simu.mode      = 'normal';
simu.explorer  = 'on';
simu.startTime = 0;
simu.rampTime  = 50;
simu.endTime   = 500;
simu.solver    = 'ode45';
simu.b2b       = 1;
simu.dt        = 0.01;

%% Wave Info
waves = waveClass('regular');
waves.height     = 5.49;              % [m]
waves.period     = 11.3;              % [s]
waves.waterDepth = 200;               % [m]

% waves = waveClass('noWaveCIC');     % free decay

% waves = waveClass('regularCIC');
% waves.height = 2.44; waves.period = 8.1;

% waves = waveClass('irregular');
% waves.height       = 2.44;
% waves.period       = 8.1;
% waves.spectrumType = 'PM';
% waves.direction    = 0;
% waves.phaseSeed    = 1;

%% Body Data    >>> REPLACE mass / inertia / displacement for your platform <<<
switch lower(caseType)
case 'base'
    body(1) = bodyClass('../hydroData/base/base.h5');
    body(1).geometryFile        = '../geometry/base.stl';
    body(1).mass                = 14072718;
    body(1).inertia             = [1.3813e10, 1.3813e10, 1.2287e10];
    body(1).initial.displacement = [0, 0, 0.2];

case 'hollow'
    h5File = '../hydroData/hollow/hollow.h5';

    body(1) = bodyClass(h5File);
    body(1).geometryFile        = '../geometry/hollow.stl';
    body(1).mass                = 13025700;
    body(1).inertia             = [1.106e10, 1.106e10, 1.173e10];
    body(1).initial.displacement = [0, 0, 0.2];

    for k = 2:4
        body(k) = bodyClass(h5File);
        body(k).geometryFile        = '../geometry/owc_piston_4m.stl';
        body(k).mass                = 'equilibrium';
        body(k).inertia             = [1.345e8, 1.345e8, 1.875e8];
        body(k).initial.displacement = [0, 0, 0];
    end
end

%% Constraints   >>> REPLACE location with your platform CoG <<<
constraint(1) = constraintClass('Constraint1');
switch lower(caseType)
    case 'base',   constraint(1).location = [0 0 -9.893];
    case 'hollow', constraint(1).location = [0 0 -9.885];
end

%% Mooring (linearised vertical spring; C33 = rho*g*A_wp)   >>> REPLACE values <<<
mooring(1) = mooringClass('mooring1');
mooring(1).matrix.stiffness = zeros(6,6);
mooring(1).matrix.damping   = zeros(6,6);
switch lower(caseType)
case 'base'
    mooring(1).matrix.stiffness(3,3) = 3745330;       % C33 [N/m]
    mooring(1).matrix.damping(3,3)   = 696200;        % ~5% critical [N*s/m]
    mooring(1).matrix.preTension     = [0 0 374533 0 0 0];
case 'hollow'
    mooring(1).matrix.stiffness(3,3) = 3366256;
    mooring(1).matrix.damping(3,3)   = 662177;
    mooring(1).matrix.preTension     = [0 0 362117 0 0 0];
end

%% Translational PTOs (hollow case)   >>> REPLACE D, locations, ptoCoefficient <<<
if strcmpi(caseType, 'hollow')
    rho_w = 1025; g = 9.81;
    D       = 4.0;                       % chamber diameter [m]
    A_bore  = pi*D^2/4;
    K_wc    = rho_w * g * A_bore;        % water-column stiffness [N/m]
    ptoCoefficient = 1.71e6;             % linearised pneumatic damping [N*s/m]

    pto(1) = ptoClass('PTO1');
    pto(1).stiffness = K_wc;  pto(1).damping = ptoCoefficient;
    pto(1).location  = [-28.868, 0.0, -10.0];

    pto(2) = ptoClass('PTO2');
    pto(2).stiffness = K_wc;  pto(2).damping = ptoCoefficient;
    pto(2).location  = [ 14.434,  25.0, -10.0];

    pto(3) = ptoClass('PTO3');
    pto(3).stiffness = K_wc;  pto(3).damping = ptoCoefficient;
    pto(3).location  = [ 14.434, -25.0, -10.0];
end
