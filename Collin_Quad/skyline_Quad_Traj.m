clear variables; %close all; %clc;

crosswind = 0;
Ts = 0.001;
%dynamics timestep
Tsd = 0.001;

wind = [2 -1 0];

maxVel = [8, 8];

% sigma = 0*[1.06 1.06 0.7];
 sigma = 1.0*[1.06 1.06 0];

wind_and_Max_Vel = abs([0, crosswind, maxVel]);


des_Position = zeros(5005/Ts + 1, 7);
% des_Position(:,1) = 0;%1000000;

des_Position(:,1) = 0;%1000000;


des_Position(:,4) = 0;%8;
des_Position(:,5) = 0;
% des_Position(:,3) = 0;
% des_Position(:,7) = 0;

P.Va0 = norm(wind + des_Position(1,4:6));

ytot = [];
windtot = [];

name = "Data_Keras_Crosswind\Data_Train";

for i=1:1
        randseed = randi(50000, [3 1]);
        seed = randi(50000, [3 1]);
        sim('quadrotor.slx')
        
        ywind = y.Data;
        windout = wind_output.Data;
                   

        ytot = [ytot; ywind(5001:end,:)];
        windtot = [windtot; windout(5001:end,:)];

        
        i
end


% NE wind vel., NE quad vel., NE quad accel., NE quad pos., roll/pitch
% angles. Sampled @ 10 Hz and starts 5 seconds after beginning of sim
%keras_data = [windtot(1:100:end,1:2) ytot(1:100:end,4:5) ...
%    acceleration.Data(5001:100:end,4:5) ytot(1:100:end,1) ...
%    ytot(1:100:end,2) ytot(1:100:end,7:8)];


% NED quad vel., NED quad accel., NED quad pos., RPY angles, RPY rates
keras_data = [ytot(1:100:end,4:6), acceleration.Data(5001:100:end,4:6) ...
    ytot(1:100:end,1:3), ytot(1:100:end,7:9), ytot(1:100:end,10:12)];

% keras_data = [windtot(1:100:end,1:3) ytot(1:100:end,1:6) ...
%     acceleration.Data(5001:100:end,4:6) ytot(1:100:end,7:12)];


% keras_data = [windtot(1:100:end,1:2) ytot(1:100:end,4:5) ...
%     acceleration.Data(5001:100:end,4:5) 99900+ytot(1:100:end,1) ...
%     ytot(1:100:end,2) ytot(1:100:end,7:8)];

% dlmwrite('Quad_Data_With_Euler_NorthEast_5ksec.txt', keras_data, ',')

dlmwrite('Quad_Data_Hover_Crosswinds.txt', keras_data, 'delimiter', ',', 'precision', 2)
