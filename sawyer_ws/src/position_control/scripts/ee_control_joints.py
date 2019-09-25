#! /usr/bin/env python

import sys
import rospy
import intera_interface
import numpy as np
from sawyer_pykdl import sawyer_kinematics


class EEControl:
    def __init__(self):
        self.arm = "right"
        self.limb = intera_interface.Limb(self.arm)
        self.joint_names = self.limb.joint_names()
        self.kin = sawyer_kinematics(self.arm)

        self.limb.set_joint_position_speed(0.25)


        self.rs = intera_interface.RobotEnable()
        self.rs.enable()

        self._state = "LEFT2RIGHT"

        neutral = [-1.186115234375, 0.805931640625, 2.448353515625, 1.99850390625, -2.3551396484375, -0.67713671875, 3.3021533203125, 0.0]
        self.neutral = dict(zip(self.joint_names, neutral))

    def clean_shutdown(self):
        print("Exiting...")
        self.limb.move_to_joint_positions(positions=self.neutral, timeout=15.0)

        return True

    def run(self):
        self.limb.move_to_joint_positions(positions=self.neutral, timeout=15.0)

        looptime = .01
        
        dx       = 0.1   # m (distance available to slow down)
        maxSpeed = 0.5  # m/s
        maxAccel = maxSpeed**2/(2*dx)  # m/s**2
        
        x_des = 0.65    # desired x position
        kP = 1.0        # proportional coefficient for P controller 

        rate = rospy.Rate(1/looptime)

        stop = np.zeros((6,1))

        joint_vels = np.zeros((7,1))
        velocity = stop

        vel_dic = dict()

        def np_to_list(in_arr):
            output = np.zeros((1,7))
            for i in range(0,7):
                output[0][i] = in_arr[i][0]

            return list(output[0])

        while not rospy.is_shutdown():

            ee_pos = self.limb.endpoint_pose()
            x = ee_pos['position'][0]
            y = ee_pos['position'][1]
            #z = ee_pos['position'][2]

            x_error = x_des - x
            velocity[0][0] = x_error * kP       # update x vel to keep ee_x_pos at desired position


            if self._state == "STOP":
                velocity = stop
                joint_vels = self.kin.jacobian_pseudo_inverse() * velocity
                vel_dic = dict(zip(self.joint_names, np_to_list(joint_vels)))
                
            elif self._state == "RIGHT":
                velocity[1][0] = -maxSpeed
                joint_vels = self.kin.jacobian_pseudo_inverse() * velocity
                vel_dic = dict(zip(self.joint_names, np_to_list(joint_vels)))

                if y < -0.25:
                    self._state = "RIGHT2LEFT"

            elif self._state == "LEFT":
                velocity[1][0] = maxSpeed
                joint_vels = self.kin.jacobian_pseudo_inverse() * velocity
                vel_dic = dict(zip(self.joint_names, np_to_list(joint_vels)))

                if y > 0.25: 
                    self._state = "LEFT2RIGHT"

            elif self._state == "RIGHT2LEFT":
                velocity[1][0] += maxAccel*looptime
                joint_vels = self.kin.jacobian_pseudo_inverse() * velocity
                vel_dic = dict(zip(self.joint_names, np_to_list(joint_vels)))

                if velocity[1][0] >= maxSpeed:
                    self._state = "LEFT"
                
            elif self._state == "LEFT2RIGHT":
                velocity[1][0] -= maxAccel*looptime
                joint_vels = self.kin.jacobian_pseudo_inverse() * velocity
                vel_dic = dict(zip(self.joint_names, np_to_list(joint_vels)))

                if velocity[1][0] <= -maxSpeed:
                    self._state = "RIGHT"

            self.limb.set_joint_velocities(vel_dic)

            print(self._state)

            rate.sleep()



def main():
    print("Starting up node...")
    rospy.init_node("ee_control_joints")
    controller = EEControl()

    rospy.on_shutdown(controller.clean_shutdown)
    print("Node initialized")

    controller.run()

if __name__ == '__main__':
    main()
