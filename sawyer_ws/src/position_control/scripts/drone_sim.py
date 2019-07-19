#!/usr/bin/env python

import rospy, random, math, argparse
import numpy as np
from copy import copy
from geometry_msgs.msg import PoseStamped
from tf.transformations import quaternion_from_euler, euler_from_quaternion, quaternion_multiply
from std_msgs.msg import Header
from intera_interface import CHECK_VERSION, Limb, Lights, RobotEnable
from intera_motion_msgs.msg import TrajectoryOptions
from intera_motion_interface import (
	MotionTrajectory,
	MotionWaypoint,
	MotionWaypointOptions
)

RATE = 100 #hz
ACCESS_ROBOT = True


# BASIC PID ALGORITHM
class PID:
    def __init__(self, kP, kI, kD, MAX, MIN):
        self.kP = kP
        self.kI = kI
        self.kD = kD
        self.MAX = MAX
        self.MIN = MIN

        self.dt = 1/RATE
        self.integratedE = 0
        self.pastError   = 0

    def compute(self, actual, desired):
        error = actual - desired

        self.integratedE += error*self.dt

        P = error * self.kP
        I = self.integratedE
        D = (error - self.pastError) / self.dt

        self.prevError = error
        return (P*self.kP + I*self.kI + D*self.kD)



# CLASS TO SIMULATE DRONE MOTION ON THE SAWYER ROBOTIC ARM
class Drone:
    def __init__(self):
        print("Getting robot state... ")
        if ACCESS_ROBOT:
            self.rs = RobotEnable(CHECK_VERSION)
            self.rs.enable()

        self.pose = PoseStamped()
        self.prevX = 0point2.65
        self.prevY = 0.0

        ap = argparse.ArgumentParser()
        ap.add_argument("-c", "--condition", type=str, help="Condition of the environment: calm, average, rough")
        ap.add_argument("-r", "--randomize", action='store_true', help="Randomly generate trajectory, overrides condition (true/false)")
        ap.add_argument("-b", "--box", type=bool, help="Test box edges at progam startup (true/false)")
        ap.add_argument("--reset", action='store_true', help="Reset the arm to it's beginning position")
        self.args = vars(ap.parse_args())
        
        if self.args["condition"] is None:
            self.args["condition"] = "calm"
        if not self.args["randomize"]:
            self.args["randomize"] = False
        if not self.args["box"]:
            self.args["box"] = False
    
        outargs = dict(zip(self.args.keys(), self.args.values()))
        print('')
        print('')
        print(outargs)
        print('')
        print('')
        print('')
        print('')

        raw_input(" ----- ROBOT ENABLED, PLEASE PRESS 'ENTER' TO CONTINUE ----- ")



    # ENSURE THE WAYPOINTS LIST IS CLEARED AT TERMINATION OF PROGRAM
    def clean_shutdown(self):
        print("exiting")
        return

    # CONTAINS WAYPOINTS TO TRACE BOX AT START OF PROGRAM
    def trace_box(self, limb):
        print("I am tracing a box")


    # ABSTRACT CONTORL OF ARM TO DEDICATED FUNCTION
    def move(self, wait, point_list, MAX_LIN_SPD=7.0, MAX_LIN_ACCL=1.5):  # one point = [x_coord, y_coord, z_coord, x_deg, y_deg, z_deg]
        limb = Limb()                                                     # point_list = [pointA, pointB, pointC, ...]
        traj_options = TrajectoryOptions()
        traj_options.interpolation_type = TrajectoryOptions.CARTESIAN
        traj = MotionTrajectory(trajectory_options=traj_options, limb=limb)

        wpt_opts = MotionWaypointOptions(max_linear_speed=MAX_LIN_SPD, max_linear_accel=MAX_LIN_ACCL, corner_distance=0.05)
        
        for point in point_list:
            q_base = quaternion_from_euler(0, math.pi/2, 0)
            q = quaternion_from_euler(point[3], point[4], point[5])
            q = quaternion_multiply(q_base, q)

            newPose = PoseStamped()
            newPose.header = Header(stamp=rospy.Time.now(), frame_id='base')
            newPose.pose.position.x = point[0]
            newPose.pose.position.y = point[1]
            newPose.pose.position.z = point[2]
            newPose.pose.orientation.x = q[0]
            newPose.pose.orientation.y = q[1]
            newPose.pose.orientation.z = q[2]
            newPose.pose.orientation.w = q[3]

            waypoint = MotionWaypoint(options=wpt_opts.to_msg(), limb=limb)
            waypoint.set_cartesian_pose(newPose, "right_hand", limb.joint_ordered_angles())
            traj.append_waypoint(waypoint.to_msg())

        if(wait):
            print("Sending trajectory and waiting for finish")
            result = traj.send_trajectory(wait_for_result=wait)
            if result is None:
                rospy.logerr('Trajectory FAILED to send')
                success = False
            elif result.result:
                rospy.loginfo('Motion controller successfully finished the trajcetory')
                success = True
            else:
                rospy.logerr('Motion controller failed to complete the trajectory. Error: %s', result.errorId)
                success = False
        else:
            print("Sending trajector w/out waiting")
            traj.send_trajectory(wait_for_result=wait)
            success = True

        return success


    # MAIN CONTROL LOOP
    def fly(self, weather="calm"):
        print("flying")

        point = [0.65, 0.0, 0.5, 0.0, 0.0, 0.0, 0.0]
        point_list = [point]

        self.move(wait=True, point_list=point_list)

        rate = rospy.Rate(RATE)
        while not rospy.is_shutdown():
            rate.sleep()

        return


# PROGRAM INITIALIZATION
print('')
print("Initializing node... ")
rospy.init_node("position_control")
print("Pose for arm set to front: ")
print("	Position: x: 0.65, y: 0.0, z: 0.5")
print("	Orientation: x: 0.0, y: 0.0, z: 0.0, w: 0.0\n\n")

drone = Drone()
rospy.on_shutdown(drone.clean_shutdown)
drone.fly()