#!/usr/bin/env python

import rospy, random, math, argparse
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

RATE = 10                  # Hz
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

        self.l = Lights()
        self.l_name = 'head_green_light'
        self.r_name = 'head_red_light'

        ap = argparse.ArgumentParser()
        ap.add_argument("-c", "--condition", type=str, help="Condition of the environment: calm, average, rough")
        ap.add_argument("-r", "--randomize", action='store_true', help="Randomly generate trajectory, overrides condition (true/false)")
        ap.add_argument("-b", "--box", action='store_true', help="Test box edges at progam startup (true/false)")
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

        self.parser = InputData()

        # ENABLE RED LIGHT WHILE WAITING FOR USER INPUT
        self.l.set_light_state(self.r_name, on=True)
        try:
            input(" ----- ROBOT ENABLED, PLEASE PRESS 'ENTER' TO CONTINUE ----- ")
        except Exception:
            print("")

        # ENABLE GREEN LIGHT WHEN PROGRAM IS RUNNING
        self.l.set_light_state(self.r_name, on=False)
        self.l.set_light_state(self.l_name, on=True)



    # ENSURE THE WAYPOINTS LIST IS CLEARED AT TERMINATION OF PROGRAM
    def clean_shutdown(self):
        print("Stopping arm...")
        try:
            self.STOP = True
            self.move(point_list = None)
            self.l.set_light_state(self.l_name, on=False)
        except:
            print("There may have been an error exiting")

        print("Stop successful, exiting...")

        return

    # INPUT THE SIMULATED TRAJECTORY AND PUSH TO OUTPUT TO move()
    def sim_drone(self):
        M = self.parser.inputMatrix()

        point_list = list()

        for x in range(0,350,3): # TIME IN FLIGHT SIM = 0.1*RANGE
            point = [ M[x][2][0],-M[x][2][1],-M[x][2][2],-M[x][3][0],M[x][3][1],M[x][3][2] ]
            #point = [ M[x][2][0],-M[x][2][1],-M[x][2][2],0,0,0 ]
            point_list.append(point)

            print(point)

        self.move(wait=True, point_list=point_list, MAX_SPD_RATIO=0.8, MAX_JOINT_ACCL=[10.0, 8.0, 10.0, 10.0, 12.0, 12.0, 12.0])

    # CONTAINS WAYPOINTS TO TRACE BOX
    def trace_box(self):
        print("I am tracing a box")

        point_list = list()
        point_list.append([0.0, 0.25, 0.0, 0.0, 0.0, 0.0])
        self.move(point_list=point_list)

        point_list = list()
        point_list.append([0.0, 0.25, 0.1, 0.0, 0.0, 0.0])
        self.move(point_list=point_list)

        point_list = list()
        point_list.append([0.0, -0.25, 0.1, 0.0, 0.0, 0.0])
        self.move(point_list=point_list)

        point_list = list()
        point_list.append([0.0, -0.25, -0.1, 0.0, 0.0, 0.0])
        self.move(point_list=point_list)

        point_list = list()
        point_list.append([0.0, 0.25, -0.1, 0.0, 0.0, 0.0])
        self.move(point_list=point_list)

        point_list = list()
        point_list.append([0.0, 0.25, 0.0, 0.0, 0.0, 0.0])
        self.move(point_list=point_list)

        return

    # MOVE TO ORIGIN DEFINED IN move()
    def moveToNeutral(self):
        print("\n --- Returning to neutral position (0.65, 0.0, 0.5, 0.0, 0.0, 0.0) ---")
        point = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        point_list = [point]

        success = self.move(wait=True, point_list=point_list, MAX_SPD_RATIO=0.2)
        return success

    # FUNCTION TO ABSTRACT CONTORL OF ARM
    def move(self, point_list = None, wait = True, MAX_SPD_RATIO=0.4, MAX_JOINT_ACCL=[7.0, 5.0, 8.0, 8.0, 8.0, 8.0, 8.0]):  # one point in point_list = [x_coord, y_coord, z_coord, x_deg, y_deg, z_deg]     
        try:
            limb = Limb()                                                     # point_list = [pointA, pointB, pointC, ...]
            traj_options = TrajectoryOptions()
            traj_options.interpolation_type = TrajectoryOptions.JOINT
            traj = MotionTrajectory(trajectory_options=traj_options, limb=limb)

            if self.STOP:
                traj.stop_trajectory()
                return True

            wpt_opts = MotionWaypointOptions(max_joint_speed_ratio=MAX_SPD_RATIO, max_joint_accel=MAX_JOINT_ACCL)
            waypoint = MotionWaypoint(options=wpt_opts.to_msg(), limb=limb)

            angles = limb.joint_ordered_angles()
            waypoint.set_joint_angles(joint_angles=angles)
            traj.append_waypoint(waypoint.to_msg())

            for point in point_list:
                #q_base = quaternion_from_euler(0, math.pi/2, 0)
                q_base = quaternion_from_euler(0, 0, 0)
                #q_rot = quaternion_from_euler(math.radians(point[3]), math.radians(point[4]), math.radians(point[5]))      # USE THIS IF ANGLES ARE IN DEGREES
                q_rot = quaternion_from_euler(point[3], point[4], point[5])                                                 # USE THIS IF ANGLES ARE IN RADIANS
                q = quaternion_multiply(q_rot, q_base)

                # DEFINE ORIGIN
                origin = {
                    'x' : 0.65,
                    'y' : 0.0,
                    'z' : 0.4
                }

                # CREATE CARTESIAN POSE FOR IK REQUEST
                newPose = PoseStamped()
                newPose.header = Header(stamp=rospy.Time.now(), frame_id='base')
                newPose.pose.position.x = point[0] + origin['x']
                newPose.pose.position.y = point[1] + origin['y']
                newPose.pose.position.z = point[2] + origin['z']
                newPose.pose.orientation.x = q[0]
                newPose.pose.orientation.y = q[1]
                newPose.pose.orientation.z = q[2]
                newPose.pose.orientation.w = q[3]

                # REQUEST IK SERVICE FROM ROS
                ns = "ExternalTools/right/PositionKinematicsNode/IKService"
                iksvc = rospy.ServiceProxy(ns, SolvePositionIK)
                ikreq = SolvePositionIKRequest()

                # SET THE NEW POSE AS THE IK REQUEST
                ikreq.pose_stamp.append(newPose)
                ikreq.tip_names.append('right_hand')

                # ATTEMPT TO CALL THE SERVICE
                try:
                    rospy.wait_for_service(ns, 5.0)
                    resp = iksvc(ikreq)
                except:
                    print("IK SERVICE CALL FAILED")
                    return

                # HANDLE RETURN 
                if (resp.result_type[0] > 0):
                    joint_angles = resp.joints[0].position

                    # APPEND JOINT ANGLES TO NEW WAYPOINT
                    waypoint.set_joint_angles(joint_angles=joint_angles)
                    traj.append_waypoint(waypoint.to_msg())
                else:
                    print("INVALID POSE")
                    print(resp.result_type[0])

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

        except rospy.ROSInterruptException:
            print("User interrupt detected. Exiting before trajectory completes")
        
    # MAIN CONTROL LOOP
    def fly(self, weather="calm"):
        print("Flying")

        self.moveToNeutral()

        if self.args["reset"]:
            self.l.set_light_state(self.l_name, on=False)
            return

        if self.args["box"]:
            self.trace_box()
            self.moveToNeutral()

        self.sim_drone()
        #self.move(wait=True, point_list=[[0,0,0,1.159/2,0,0]])

        #rate = rospy.Rate(RATE)
        #while not rospy.is_shutdown():
        #    rate.sleep()

        self.l.set_light_state(self.l_name, on=False)

        return


# PROGRAM INITIALIZATION
print('')
print("Initializing node... ")
rospy.init_node("drone_sim_joints")
print("Pose for arm set to front: ")
print("	Position: x: 0.65, y: 0.0, z: 0.5")
print("	Orientation: x: 0.0, y: 0.0, z: 0.0, w: 0.0\n")

print("Coordinate system is RHS - +z up, +x in front, +y to left\n\n")

drone = Drone()
rospy.on_shutdown(drone.clean_shutdown)
drone.fly()