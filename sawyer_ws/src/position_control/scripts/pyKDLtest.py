#! /usr/bin/env python

import sys
import rospy
import intera_interface
import numpy as np
from sawyer_pykdl import sawyer_kinematics


class PyKDLTest:
    def __init__(self):
        self.arm = "right"
        self.limb = intera_interface.Limb(self.arm)     # Create arm & limb objects
        self.kin = sawyer_kinematics(self.arm)          # Create kinematics construct
        
        self.rs = intera_interface.RobotEnable()        # Enable Saywer
        self.rs.enable()

    def run(self):
        rate = rospy.Rate(10)
        while not rospy.is_shutdown():                  # Joint right_j0 = shoulder -> right_j6 = wrist
            velocities = self.limb.joint_velocities()
            ee_vel_dic = self.limb.endpoint_velocity()

            vel_list = list()
            
            for vel in velocities:
                vel_list.append(velocities[vel])
            
            vel_list.reverse()

            vel_vec = np.zeros((7,1))
            for i in range(0,7):
                vel_vec[i][0] = vel_list[i]

            ee_vel = self.kin.jacobian() * vel_vec

            ee_linear = np.zeros((1,3))
            ee_angular = np.zeros((1,3))

            for i in range(0,3):
                ee_linear[0][i] = ee_vel[i][0]

            for i in range(3,6):
                ee_angular[0][i-3] = ee_vel[i][0]

            ee_vel_linear = np.zeros((1,3))
            ee_vel_angular = np.zeros((1,3))

            ee_vel_linear[0][0] = ee_vel_dic['linear'][1]
            ee_vel_linear[0][1] = ee_vel_dic['linear'][0]
            ee_vel_linear[0][2] = ee_vel_dic['linear'][2] 

            #for i in range(0,3):
            #    ee_vel_linear[0][i]=ee_vel_dic['linear'][i]

            for i in range(0,3):
                ee_vel_angular[0][i]=ee_vel_dic['angular'][i]
                
            print(ee_vel_linear - ee_linear)
            rate.sleep()

    def clean_shutdown(self):
        print("Exiting...")
        return True

def main():
    print("Starting up node...")
    rospy.init_node("pyKDLtest")
    
    tester = PyKDLTest()

    rospy.on_shutdown(tester.clean_shutdown)
    tester.run()


if __name__ == '__main__':
    main()