%% ========================================================================
%% USER CONFIGURATION - CASE SPECIFIC VARIABLES
%% ========================================================================

% --- File Paths ---
simu_file      = 'wafowt_nomoor_template.slx';             % Simulink Model
hydrodata_file = 'Hydrodata/owc_template.h5';              % BEM output (.h5)
platform_geo   = 'Geometry/owc_platform_template.stl';     % Platform geometry
pto_geo        = 'Geometry/owc_pto_template.stl';          % PTO geometry

% --- Wave Parameters (Regular) ---
wave_height    = 5.49;    % [m]
wave_period    = 11.3;    % [s]
water_depth    = 200;     % [m]

% --- Body 1: Platform Properties ---
platform_mass  = 13025700;                       % [kg]
platform_I     = [1.106e10, 1.106e10, 1.173e10]; % [kg-m^2]
platform_disp  = [0, 0, 0.2];                    % Initial displacement [m]

% --- Body 2-4: OWC/PTO Properties ---
pto_mass       = 'equilibrium';                  % usually 'equilibrium'
pto_I          = [1.345e8, 1.345e8, 1.875e8];    % [kg-m^2]
pto_disp       = [0, 0, 0];                      % Initial displacement [m]

% --- Coordinates / Locations [x, y, z] ---
cg_platform    = [0.0, 0.0, -9.885];
cg_pto1        = [-28.868, 0.0, -10.0];
cg_pto2        = [14.434, 25.0, -10.0];
cg_pto3        = [14.434, -25.0, -10.0];

% --- Mooring Parameters (Heave / Z-direction) ---
mooring_stiff_z = 3366256; % C33 Stiffness [N/m]
mooring_damp_z  = 662177;  % C33 Damping (e.g., 5% critical) [N·s/m]
mooring_preT_z  = 362117;  % Pre-tension [N] (upward)

% --- OWC / Air Chamber Physical Parameters ---
rho_w          = 1025;     % Water density [kg/m^3]
g              = 9.81;     % Gravity [m/s^2]
rho_air        = 1.2;      % Air density [kg/m^3]
chamber_diam   = 4.0;      % Diameter of air chamber [m]
orifice_diam   = 2.0;      % Orifice diameter [m]
Cd             = 0.6466;   % Orifice discharge coefficient


%% ========================================================================
%% WEC-SIM SETUP & EXECUTION
%% ========================================================================

%% Simulation Data
simu = simulationClass();
simu.simMechanicsFile = simu_file;
simu.mode = 'normal';
simu.explorer = 'on';
simu.startTime = 0;      % [s]
simu.rampTime  = 50;     % [s]
simu.endTime   = 500;    % [s]
simu.solver = 'ode45';
simu.b2b   = 1; 
simu.dt        = 0.01;   % [s]


%% Wave Info
waves = waveClass('regular');
waves.height = wave_height; 
waves.period = wave_period; 
waves.waterDepth = water_depth; 

% % % noWaveCIC, no waves with radiation CIC  
% waves = waveClass('noWaveCIC');

% % Regular Waves with CIC
% waves = waveClass('regularCIC');                                               
% waves.height = 2.44;                                       
% waves.period = 8.1;                                         

% % Irregular Waves using PM Spectrum 
% waves = waveClass('irregular');                           
% waves.height = 2.44;                                       
% waves.period = 8.1;                                         
% waves.spectrumType = 'PM';                                
% waves.direction = 0;

% % Irregular Waves using JS Spectrum with Equal Energy and Seeded Phase
% waves = waveClass('irregular');                           
% waves.height = 2.5;                                       
% waves.period = 8;                                         
% waves.spectrumType = 'JS';                                
% waves.bem.option = 'EqualEnergy';          
% waves.phaseSeed = 1;                                      

% % Irregular Waves using PM Spectrum with Traditional and State Space 
% waves = waveClass('irregular');                           
% waves.height = 2.5;                                       
% waves.period = 8;                                         
% waves.spectrumType = 'PM';                                
% simu.stateSpace = 1;                                      
% waves.bem.option = 'Traditional';          

% % Irregular Waves with imported spectrum
% waves = waveClass('spectrumImport');      
% waves.spectrumFile = 'spectrumData.mat';  

% % Waves with imported wave elevation time-history  
% waves = waveClass('elevationImport');          
% waves.elevationFile = 'elevationData.mat';     


%% Body Data
% 1) Platform
body(1) = bodyClass(hydrodata_file);
body(1).geometryFile = platform_geo;
body(1).mass         = platform_mass;
body(1).inertia      = platform_I;
body(1).initial.displacement = platform_disp;

% 2) PTO offset 1
body(2) = bodyClass(hydrodata_file);
body(2).geometryFile = pto_geo;
body(2).mass         = pto_mass;
body(2).inertia      = pto_I;
body(2).initial.displacement = pto_disp;

% 3) PTO offset 2
body(3) = bodyClass(hydrodata_file);
body(3).geometryFile = pto_geo;
body(3).mass         = pto_mass;
body(3).inertia      = pto_I;
body(3).initial.displacement = pto_disp;

% 4) PTO offset 3
body(4) = bodyClass(hydrodata_file);
body(4).geometryFile = pto_geo;
body(4).mass         = pto_mass;
body(4).inertia      = pto_I;
body(4).initial.displacement = pto_disp;


%% Constraints
constraint(1) = constraintClass('Constraint1');
constraint(1).location = cg_platform;


%% Mooring
mooring(1) = mooringClass('mooring1');
mooring(1).matrix.stiffness = zeros(6,6);
mooring(1).matrix.stiffness(3,3) = mooring_stiff_z;       
mooring(1).matrix.damping = zeros(6,6);
mooring(1).matrix.damping(3,3) = mooring_damp_z;           
mooring(1).matrix.preTension = [0 0 mooring_preT_z 0 0 0]; 


%% Translational PTOs (Oscillating Water Columns)

% Calculate Stiffness and Damping coefficients dynamically
A_bore = (pi * chamber_diam^2) / 4;                               
K_wc = rho_w * g * A_bore; 
ptoCoeffcient = (8 * rho_air * A_bore^3) / (pi^2 * Cd^2 * orifice_diam^4);

pto(1) = ptoClass('PTO1');                      
pto(1).stiffness = K_wc;                           
pto(1).damping = ptoCoeffcient;                       
pto(1).location = cg_pto1;                     

pto(2) = ptoClass('PTO2');                      
pto(2).stiffness = K_wc;                           
pto(2).damping = ptoCoeffcient;                       
pto(2).location = cg_pto2;                     

pto(3) = ptoClass('PTO3');                      
pto(3).stiffness = K_wc;                           
pto(3).damping = ptoCoeffcient;                       
pto(3).location = cg_pto3;
