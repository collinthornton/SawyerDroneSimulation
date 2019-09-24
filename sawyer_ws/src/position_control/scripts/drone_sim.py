#!/usr/bin/env python

import rospy, random, math, argparse
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
from intera_core_msgs.srv import (
    SolvePositionIK,
    SolvePositionIKRequest,
)

from InputData import InputData

RATE = 100 #hz
ACCESS_ROBOT = True


# CLASS TO SIMULATE DRONE MOTION ON THE SAWYER ROBOTIC ARM
class Drone:
    def __init__(self):
        print("Getting robot state... ")
        if ACCESS_ROBOT:
            self.rs = RobotEnable(CHECK_VERSION)
            self.rs.enable()

        self.STOP = False 
        
        self.pose = PoseStamped()
        self.prevX = 0.65
        self.prevY = 0.0

        ap = argparse.ArgumentParser()
        ap.add_argument("-c", "--condition", type=str, help="Condition of the environment: calm, average, rough")
        ap.add_argument("-r", "--randomize", action='store_true', help="Randomly generate trajectory, overrides condition")
        ap.add_argument("-b", "--box", action='store_true', help="Test box edges at progam startup")
        ap.add_argument("-l", "--line", action='store_true', help="Move in straight line to test Doppler effect")
        ap.add_argument("--reset", action='store_true', help="Reset the arm to it's beginning position")
        self.args = vars(ap.parse_args())
        
        if self.args["condition"] is None:
            self.args["condition"] = "calm"
        if not self.args["randomize"]:
            self.args["randomize"] = False
        if not self.args["box"]:
            self.args["box"] = False
        if not self.args["line"]:
            self.args["line"] = False
    
        outargs = dict(zip(self.args.keys(), self.args.values()))
        print('')
        print('')
        print(outargs)
        print('')
        print('')
        print('')
        print('')

        self.parser = InputData()
        try:
            input(" ----- ROBOT ENABLED, PLEASE PRESS 'ENTER' TO CONTINUE ----- ")
        except Exception:
            print("")



    # ENSURE THE WAYPOINTS LIST IS CLEARED AT TERMINATION OF PROGRAM
    def clean_shutdown(self):
        print("Stopping arm...")
        try:
            self.STOP = True
            self.move(point_list = None)
        except:
            print("There may have been an error exiting")

        print("Stop successful, exiting...")

        return

    def sim_drone(self):
        M = self.parser.inputMatrix()

        point_list = list()
        i = 0
        for waypoint in M:
            #point = [ waypoint[2][0],-waypoint[2][1],-waypoint[2][2],waypoint[3][0],waypoint[3][1],waypoint[3][2] ]
            point = [ waypoint[2][0],-waypoint[2][1],-waypoint[2][2],0,0,0 ]
            point_list.append(point)

            print(point)
            if i > 150:         # Each point represent 0.1 seconds of flight time in simulator
                break
            else:
                i += 1

        self.move(wait=True, point_list=point_list, MAX_LIN_ACCL=2.5)

    # CONTAINS WAYPOINTS TO TRACE BOX AT START OF PROGRAM
    def trace_box(self):
        print("I am tracing a box")

        point_list = list()
        point = [0.0, 0.25, 0.0, 0.0, 0.0, 0.0]
        point_list.append(point)
        
        point = [0.0, 0.25, 0.1, 0.0, 0.0, 0.0]
        point_list.append(point)

        point = [0.0, -0.25, 0.1, 0.0, 0.0, 0.0]
        point_list.append(point)

        point = [0.0, -0.25, -0.1, 0.0, 0.0, 0.0]
        point_list.append(point)

        point = [0.0, 0.25, -0.1, 0.0, 0.0, 0.0]
        point_list.append(point)

        point = [0.0, 0.25, 0.0, 0.0, 0.0, 0.0]
        point_list.append(point)

        success = self.move(wait=True, point_list=point_list, MAX_LIN_SPD=0.5, MAX_LIN_ACCL=0.75)
        return success

    def follow_line(self):
        print("I am moving in a line")

        point_list = list()

        point = [0.0, 0.4, 0.0, 0.0, 0.0, 0.0]
        point_list.append(point)

        point = [0.0, -0.4, 0.0, 0.0, 0.0, 0.0]
        point_list.append(point)

        success = self.move(wait=True, point_list=point_list, MAX_LIN_SPD=1.0, MAX_LIN_ACCL=20.0)
        return success

    def moveToNeutral(self):
        print("\n --- Returning to neutral position (0.65, 0.0, 0.4, 0.0, 0.0, 0.0 ---")
        point = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        point_list = [point]

        success = self.move(wait=True, point_list=point_list, MAX_LIN_SPD=0.5, MAX_LIN_ACCL=0.75)
        return success


    # NEED TO TO SWITCH JOINT CONTROL MODE TO JOINT AND USE AN IK SOLVER TO INTERPOLATE JOINT POSITIONS

    # FUNCTION TO ABSTRACT CONTORL OF ARM
    def move(self, point_list, wait = True, MAX_LIN_SPD=7.0, MAX_LIN_ACCL=1.5):  # one point = [x_coord, y_coord, z_coord, x_deg, y_deg, z_deg]     
        try:
            limb = Limb()                                                     # point_list = [pointA, pointB, pointC, ...]
            traj_options = TrajectoryOptions()
            traj_options.interpolation_type = TrajectoryOptions.CARTESIAN
            traj = MotionTrajectory(trajectory_options=traj_options, limb=limb)
        except:
            print("There may have been an error while exiting")

        if self.STOP:
            traj.stop_trajectory()
            return True

        wpt_opts = MotionWaypointOptions(max_linear_speed=MAX_LIN_SPD, max_linear_accel=MAX_LIN_ACCL, corner_distance=0.002)
        
        for point in point_list:
            q_base = quaternion_from_euler(0, 0, math.pi/2)
            #q_rot = quaternion_from_euler(math.radians(point[3]), math.radians(point[4]), math.radians(point[5]))
            q_rot = quaternion_from_euler(point[3], point[4], point[5])
            q = quaternion_multiply(q_rot, q_base)

            newPose = PoseStamped()
            newPose.header = Header(stamp=rospy.Time.now(), frame_id='base')
            newPose.pose.position.x = point[0] + 0.65
            newPose.pose.position.y = point[1] + 0.0
            newPose.pose.position.z = point[2] + 0.4
            newPose.pose.orientation.x = q[0]
            newPose.pose.orientation.y = q[1]
            newPose.pose.orientation.z = q[2]
            newPose.pose.orientation.w = q[3]

            waypoint = MotionWaypoint(options=wpt_opts.to_msg(), limb=limb)
            waypoint.set_cartesian_pose(newPose, "right_hand", limb.joint_ordered_angles())
            traj.append_waypoint(waypoint.to_msg())

        if(wait):
            print(" \n --- Sending trajectory and waiting for finish --- \n")
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
            print("\n --- Sending trajector w/out waiting --- \n")
            traj.send_trajectory(wait_for_result=wait)
            success = True

        return success


    # MAIN CONTROL LOOP
    def fly(self, weather="calm"):
        print("Flying")

        self.moveToNeutral()

        if self.args["box"]:
            self.trace_box()
            self.moveToNeutral()

        if self.args["line"]:
            self.follow_line()
            self.moveToNeutral()
            return

        #self.sim_drone()
        self.move(wait=True, point_list=[[-0.011,0.046,0.015,-0.53,0.023,-6.5e06],[-0.012, 0.04, 0.014, -0.53, 0.022, -6.2e-06], [0.0, 0.0, 0.0, 0, 0, 0]])

        #rate = rospy.Rate(RATE)
        #while not rospy.is_shutdown():
        #    rate.sleep()

        return


# PROGRAM INITIALIZATION
print('')
print("Initializing node... ")
rospy.init_node("position_control")
print("Pose for arm set to front: ")
print("	Position: x: 0.65, y: 0.0, z: 0.5")
print("	Orientation: x: 0.0, y: 0.0, z: 0.0, w: 0.0\n")

print("Coordinate system is RHS - +z up, +x in front, +y to left\n\n")

drone = Drone()
rospy.on_shutdown(drone.clean_shutdown)
drone.fly()