clc; clear; close all;
Vm = 2.8; % Motor rated voltage
Im = 1.68; % Motor rated current
Lm = 5e-3; % motor inductance, Henry
k = 32; % Microstepping factor, 2^n
theta = deg2rad(0.9); % Stepper motor stepsize degrees

alpha = deg2rad(6); % operation region degrees
closedAng = deg2rad(1.7); % Part of operation region that is closed
por = [1-closedAng/alpha, 1-2*closedAng/alpha]
Drotor = 0.1; % Rotor diameter, meter
mrotor = 0.02; % Rotor mass, kg

MhFS = 5.5*9.81/100; % Holding torque at full step mode, Nm
sf = 3; % Torque safety factor

St_max = 0.7; % Maximum Strouhal number we'll test
u_inf_max = 9; % Minimum free flow velocity we'll use, m/s
WFw = 9*Drotor; % Wind farm width

%% Torque calcs
f_max = St_max*u_inf_max/WFw; % Maximal control cycle frequency
M_max = mrotor*Drotor^2/4*pi^2*f_max^2*alpha *sf;

%% Gearing calcs
MhMS = [1 0.7 0.38 0.19 0.09 0.04 0.02 0.01]; % Holding torque degredation per microstepping
MSpFS = log2(k);
Mh = MhFS*MhMS(MSpFS);
eta = ceil(M_max/Mh); % Gearing ratio stepper-disk, >1 : deceleration of disk
if eta~=1; warning(['Gear ratio of ' num2str(eta) ' is necessary']);end

%% Velocity calcs
% Mainly from https://www.allaboutcircuits.com/tools/stepper-motor-calculator/
dphi_max = pi*alpha*f_max*eta; % Design required maximum motor rotation velocity, rad/s
spr = 2*pi/theta; % Steps per revolution
dphiStepper_max = Vm/2/Lm/Im/spr*2*pi; % Theoretical maximum stepper velocity, rad/s
if dphi_max>dphiStepper_max; warning("Stepper is required to go faster than possible"); end

% Sampling considerations
Tstep_min = 2*Lm*Im/Vm; % Time necessary per full step, s
fControl_min = k/Tstep_min; % Step frequency necessary for maximum speed, Hz

%% Positional calcs
stepAngs = 0:theta/k:alpha;
Nsteps = length(stepAngs);
% scatter(1:Nsteps,rad2deg(stepAngs), '.')
% xlabel("Steps")
% ylabel("Angular position [deg]")

%% Resolution calcs
diskRes = theta/k;
Ct_range = -1.35*por+1.37
CtStep = (max(Ct_range)-min(Ct_range))/Nsteps


