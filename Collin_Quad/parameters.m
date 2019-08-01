%P = struct;

%dynamics params
% P.m = 0.4794;
% P.g = 9.81;
% P.Ix = 0.0086;
% P.Iy = 0.0086;
% P.Iz = 0.0172;
% P.L = 0.225;

P.m = 1.5;
P.g = 9.81;
P.Ix = 0.0347563;
P.Iy = 0.0458929;
P.Iz = 0.0977;
P.L = 0.47/2;

P.I = diag([P.Ix,P.Iy,P.Iz]);
P.e3 = [0;0;1];

P.Cd1 = 0.2;%4.842/(200);
P.Cd2 = 0.2;%4.842/(200);
P.Cd3 = 0.2;%4.842/(200);

%attitude controller params
P.K2 = -14.6211*1.5;
P.K3 = -14.6211*1.5;
P.K4 = -32*1.5;

P.Kp2 = 1.8668*5*.5;
P.Kp3 = 1.8572*5*.5;
P.Kp4 = 1.5064*5*.5;

P.Kd2 = .2340*.8;
P.Kd3 = .2334*.8;
P.Kd4 = .1870*.8;


%position controller params
P.Ts = 0.001;
P.kp = 0.3;
P.kd = 0.25;
%integral term needs to be scaled by timestep
P.ki = 2E-4*(1000*P.Ts);


%altitude
%P.k2 = 200;%1.5;
%P.kd2 =20;%.05;
%P.ki2 = 5E-3*(1000*P.Ts);%3E-4*(1000*P.Ts);
P.k2=1.5;
P.kd2=.05;
P.ki2=3E-4*(1000*P.Ts);

%motor control
P.kd_motor = .01;
P.kp_motor = 1.2;
P.ki_motor = 5;


% wind parameters
%50 meter alt
P.L_wx = 200;
P.L_wy = 200;
P.L_wz = 50;
%100 meter alt
% P.L_wx = 263;
% P.L_wy = 263;
% P.L_wz = 100;
% %150 meter alt
% P.L_wx = 287;
% P.L_wy = 287;
% P.L_wz = 150;

%motor parameters
P.k_t = 0.00005;
P.k_d = 0.00005;


%rotor parameters
P.R = 0.1;%m
P.rho = 1.225;%kg/m^3
P.kf_rotor = .003;
