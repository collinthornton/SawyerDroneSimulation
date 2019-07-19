#!/usr/bin/env python

import math
import numpy as np

class Kinematics:
    def __init__(self):

        ''' Notation
                x, y, z    = absolute coordinates in base frame
                x', y', z' = absolute coordinates in body frame
                
                roll, pitch, yaw = absolute orientation in base frame

        '''
        np.set_printoptions(suppress=True)

        C = lambda x : math.cos(x)
        S = lambda x : math.sin(x)
        T = lambda x : math.tan(x)

        # Constants
        k = 2.980 * 10**(-6) # LIFT CONSTANT
        b = 1.140 * 10**(-7) # DRAG CONSTANT
        l = 0.225            # LENGTH FROM ROTOR TO COG m
        m = 0.468            # MASS kg
        Dx = Dy = Dz = 0.25           # DRAG FORCE COEFFICIENTS kg/s
        Ixx = Iyy = 4.856 * 10**(-3)  # INERTIAL COMPONENTS     kg*m^2
        Izz = 8.801 * 10**(-3)        # INERTIAL COMPONENTS     kg*m^2        
        
        
        # Variables
        roll  = droll  = phi   = 0
        pitch = dpitch = theta = 0
        yaw   = dyaw   = psi   = 0

        x = dx = ddx = 0
        y = dy = ddy = 0
        z = dz = ddz = 0

        rollb  = dRollb  = 0
        pitchb = dPitchb = 0
        yawb   = dYawb   = 0

        RPM = 8000
        rads = RPM * 2*math.pi / 60
        w1 = -rads-2222 #w1-4 = rotational velocity of rotors rad/s 
        w2 = rads
        w3 = -rads-2222
        w4 = rads


        N = np.array([roll, pitch, yaw])         # ANGULAR POSITION IN INERTIAL FRAME 
        dN = np.array([droll, dpitch, dyaw])     # ANGULAR VELOCITY IN INERTIAL FRAME
        Nb = np.array([rollb, pitchb, yawb])     # ANGULAR POSITION IN BODY FRAME
        dNb = np.array([dRollb, dPitchb, dYawb]) # ANGULAR VELOCITY IN BODY FRAME
        E = np.array([x,y,z])                    # ABSOLUTE POSITION IN INERTIAL FRAME
        dE = np.array([dx, dy, dz])              # ABSOLUTE VELOCITY IN INERTIAL FRAME
        ddE = np.array([ddx, ddy, ddz])          # ABSOLUTE ACCELERATION IN INERTIAL FRAME

        # ROTATION MATRIX FROM BODY FRAME TO INERTIAL FRAME
        R = np.array([[C(psi)*C(theta), C(psi)*S(theta)*S(phi)-S(psi)*C(phi), C(psi)*S(theta)*C(phi)+S(psi)*S(phi)],
                      [S(psi)*C(theta), S(psi)*S(theta)*S(phi)+C(psi)*C(phi), S(psi)*S(theta)*C(phi)-C(psi)*S(phi)],
                      [-1*S(theta), C(theta)*S(phi), C(theta)*C(phi)]])

        # TRANSFORMATION MATRIX FOR ANGULAR VELOCITIES FROM INERTIAL FRAME TO BODY FRAME
        W = np.array([[1, 0, -S(theta)],
                      [0, C(phi), C(theta)*S(phi)],
                      [0, -S(phi), C(theta)*C(phi)]])

        # INTERTIA MATRIX, NOTE THAT Ixx == Iyy
        I = np.array([[Ixx, 0, 0],
                      [0, Iyy, 0],
                      [0, 0, Izz]])

        # DRAG COEFFICIENT
        D = np.array([[Dx, 0, 0],
                      [0, Dy, 0],
                      [0, 0, Dz]])

        # GRAVITY
        G = np.array([0, 0, -9.81])

        force = np.array([k*w1**2, k*w2**2, k*w3**2, k*w4**2])
        Thrust = np.array([0, 0, np.sum(force)])   # THRUST IN BODY FRAME

        Torque = np.array([l*(force[3]-force[1]), l*(force[2]-force[0]), b*(force[3]-force[0]+force[1]-force[2])]) # TORQUE IN BODY FRAME= [roll, pitch, yaw]


        # Dynamics
        ddE = G + np.dot(R, Thrust)/m - np.dot(D, dE)/m
        #dNb = np.array([((Iyy-Izz)*dNb[1]*dNb[2]/Ixx), ((Izz-Ixx)*dNb[0]*dNb[2]/Iyy), ((Ixx-Iyy)*dNb[0]*dNb[1]/Izz)]) - np.
        dNb =  np.linalg.inv(I)*(Torque-np.cross(Nb,I*Nb))


        
        print("Acceleration (inertial):     ")
        print(ddE)
        print('\n\nThrust (body):  ')
        print(Thrust)
        print("\n\nR:     ")
        print(R)
        print("\n\nThrust*R:  ")
        print(Thrust*R)
        print("\n\nI:     ")
        print(I)
        print("\n\nI inverse: ")
        print(np.linalg.inv(I))
        print("\n\n\nTorque (body): ")
        print(Torque)
        print("\n\nAngular acceleration (body): ")
        print(dNb)
        print("\n\n")


k = Kinematics()
