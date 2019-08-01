clear variables; close all; %clc;

wind1 = load('field1.dat');
windE1 = wind1(96001:128000,:);
wind2 = load('field2.dat');
windE2 = wind2(96001:128000,:);
wind3 = load('field3.dat');
windE3 = wind3(96001:128000,:);
wind4 = load('field4.dat');
windE4 = wind4(96001:128000,:);
wind5 = load('field5.dat');
windE5 = wind5(96001:128000,:);
wind6 = load('field6.dat');
windE6 = wind6(96001:128000,:);
wind7 = load('field7.dat');
windE7 = wind7(96001:128000,:);

windECombined = [windE1; windE2; windE3; windE4; windE5; windE6; windE7];

% wind1 = load('field1.dat');
windN1 = wind1(128001:160000,:);
% wind2 = load('field2.dat');
windN2 = wind2(128001:160000,:);
% wind3 = load('field3.dat');
windN3 = wind3(128001:160000,:);
% wind4 = load('field4.dat');
windN4 = wind4(128001:160000,:);
% wind5 = load('field5.dat');
windN5 = wind5(128001:160000,:);
% wind6 = load('field6.dat');
windN6 = wind6(128001:160000,:);
% wind7 = load('field7.dat');
windN7 = wind7(128001:160000,:);

windNCombined = [windN1; windN2; windN3; windN4; windN5; windN6; windN7];

clear wind1 wind2 wind3 wind4 wind5 wind6 wind7;

%%
Ts = 0.001;
%dynamics timestep
Tsd = 0.001;

wind = [5 5 0];

maxVel = [8, 8];

%sigma = 1*[1.06 1.06 0.7];
sigma = 0*[1.06 1.06 0];

wind_and_Max_Vel = abs([0, crosswind, maxVel]);


des_Position = zeros(10005/Ts + 1, 7);

for i=5000:(size(des_Position,1))-1%5.3
   des_Position(i+1,1:2) = des_Position(i,1:2)+5.3/1000;
    
end

des_Position(:,4) = 0;
des_Position(:,5) = 0;
des_Position(:,3) = 0;
des_Position(:,7) = pi/4;

P.Va0 = norm(wind + des_Position(1,4:6));

ytot = [];
windtot = [];

t=0:.001:25;
name = "Data_Keras_Crosswind\Data_Train";

for i=1:1
        randseed = randi(50000, [3 1]);
        seed = randi(50000, [3 1]);
        sim('quadrotor.slx')
        
        ywind = y.Data;
        windout = wind_output.Data;
        
        
%         windvel = con2seq([windout(5100:100:end,1:2)']);
%         posdev = con2seq([[100000 0]'-ywind(5100:100:end,1:2)'; ywind(5100:100:end,4:5)']);

        windvel = con2seq([windout(5100:100:end,1:2)'; ywind(5100:100:end,4:5)';...
            acceleration.data(5100:100:end,4:5)'; ywind(5100:100:end,7:8)']);
        posdev = con2seq([[100000 0]'-ywind(5100:100:end,1:2)']);
        
        data = [windvel; posdev];
           
        %save(strcat(name,int2str(i)), 'data')
        
%         ytot = [ytot ywind(5001:end,1:3)-[ywind(10000,4)*t' zeros(25001,1) zeros(25001,1)]-ywind(5001,1:3)];
%         windtot = [windtot windout(5001:end,:)];
        %ytot = [ytot; ywind(5001:end,:)-[ywind(10000,4)*t' zeros(25001,11)]-ywind(5001,:)];
        ytot = [ytot; ywind(5001:end,:)];
        windtot = [windtot; windout(5001:end,:)];

        
        i
    %end
end
% 
% figure
% plot(y.Time, ywind(:,2))
% hold on;
% plot(y.Time, windout(:,2))

endtime = 1250*2;
t=0:.001:endtime-20;


% ytot_temp = zeros(size(ytot(:,1:3),1),6);
% accel_temp = zeros(size(acceleration.Data(:,1:3),1),6);
%psi = ywind(end,
%psi = pi/4;
%R = [cos(psi), sin(psi), 0; -sin(psi), cos(psi), 0; 0, 0, 1];
% 
% for i=1:(size(ytot,1))-1
%     psi = ytot(i,9);
% %     R = [cos(psi), sin(psi), 0; -sin(psi), cos(psi), 0; 0, 0, 1];
% 
%     ytot_temp(i,1:3) = R*ytot(i,1:3)'; 
%     ytot_temp(i,4:6) = R*ytot(i,4:6)';
%     accel_temp(i,4:6) = R*acceleration.Data(i,4:6)';
%     windtot(i,:) = R*windtot(i,:)';
% end

%save for Keras
% keras_data = [windtot(1:100:end,1:2) ytot(1:100:end,4:5) ...
%     acceleration.Data(5001:100:end,4:5) 100000-ytot(1:100:end,1) ...
%     ytot(1:100:end,2) ytot(1:100:end,7:8)];

keras_data = [windtot(1:100:end,1:2) ytot(1:100:end,4:5) ...
    acceleration.Data(5001:100:end,4:5) ytot(1:100:end,1) ...
    ytot(1:100:end,2) ytot(1:100:end,7:8)];


dlmwrite('Quad_Data_With_Euler_Diagonal.txt', keras_data, ',')

%% format data
% % 
% for i=1:4950
%     for j=1:1
% %         entemp(1,j) = (ytot(100*i+(j-1)*25000+1, 2));
% %         entemp(1:2,j) = des_Position()-(ytot(100*i+(j-1)*25000+1, 1:2));
%         %entemp(3:4,j) = (ytot(100*i+(j-1)*25000+1, 7:8));
% %         enwindtemp(1:2,j) = (windtot(100*i+(j-1)*25000+1, 1:2));
% %         enwindtemp(3:4,j) = [ytot(100*i+(j-1)*25000+1, 4:5)-[ytot(100+(j-1)*25000+1,4) 0]];
% 
% 
%         entemp(1:2,j) = [10000 0]-(ytot(100*i+(j-1)*495000+1, 1:2));
%         entemp(3:4,j) = (ytot(100*i+(j-1)*495000+1, 7:8));
%         entemp(5:6,j) = ytot(100*i+(j-1)*495000+1, 4:5);
% %         entemp(1:2,j) = (ytot(100*i+(j-1)*495000+1, 4:5));
%         enwindtemp(1:2,j) = (windtot(100*i+(j-1)*495000+1, 1:2));
%         %enwindtemp(3:4,j) = ytot(100*i+(j-1)*495000+1, 4:5);
% %         enwindtemp(1,j) = (windtot(100*i+(j-1)*25000+1, 2));
%     end
%     enpos(:,i) = num2cell(entemp,[1,2]);
%     enwind(:,i) = num2cell(enwindtemp,[1,2]);
% end
