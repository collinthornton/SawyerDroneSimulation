# SawyerDroneSimulation


This project is being developed for a multidisciplinary research project at Oklahoma State University. This code simulates a quadcopter drone on a Sawer Robotic Arm.

### Files of interest: 

*__1.__*  -  sawyer_ws/src/position_control/scripts/position_control.py \
*__2.__*  -  sawyer_ws/src/position_control/scripts/motion_control.py \
*__3.__*  -  sawyer_ws/src/position_control/scripts/drone_control.py \
*__4.__*  -  sawyer_ws/src/position_control/scripts/drone_sim.py \
*__5.__*  -  sawyer_ws/src/position_control/scripts/drone_sim_joints.py

### Intera Inverse Kinematics Solver
The SDK maintains a rosservice for solving inverse kinematics problems. It is exemplified in:

sawyer_ws/src/intera_sdk/intera_examples/scripts/ik_service_client.py 

Their example code is decently documented and works as a general guide. Further examples can be found in __1.__ and __5.__


### Intera SDK Control Interfaces
The Intera SDK contains multiple methods of controlling the arm.

#### Motion Controller
The Motion Controller Interface is a simplified method of giving the arm specific waypoints. It hfas two interpolation settings: CARTESIAN and JOINT. Both serve different purposes and must be implemented in different ways. 

__CARTESIAN -__ This mode tracks linearly from point to point. It is useful
