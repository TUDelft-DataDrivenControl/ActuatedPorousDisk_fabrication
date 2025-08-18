clc;clear; close all;
Ct = [0.3 2];

Dr = 0.1;
Uinf = 5;
rho = 1.225;

Ebrass = 120e9;
Esteel = 200e9;

L = 0.11;

RtowerO = 0.003;
RtowerI = 0.0025;
Raxle =   0.0015;


%%
l1 = linspace(0,L,100);

Itower = pi/4*(RtowerO^4 - RtowerI^4);
Iaxle = pi/4*Raxle^4;

EIbrass = Ebrass*Itower;
EIsteel = Esteel*Iaxle;

EI = EIbrass+EIsteel;

T = pi*rho*Dr^2*Uinf^2*Ct/8;

M = kron(T.',(L-l1));

disT = kron(T.',l1.^2)/2/EI;

strain = M*RtowerO/EI;
eta = 1-2*strain(1,:)./(sum(strain,1));
%%
figure
% subplot(1,2,1)
% plot(l1,disT)
% subplot(1,2,2)
hold on
plot(l1,strain(1,:), DisplayName='min')
plot(l1,strain(2,:), DisplayName='max')
xlabel("Gauge installation height [m]")
ylabel("Strain")
legend

% plot(l1,theta_max)
% plot(l1,theta_min)










