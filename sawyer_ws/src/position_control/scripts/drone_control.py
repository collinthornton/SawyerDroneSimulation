#!/usr/bin/env python

"""
Intera SDK drone simulator
"""
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


class PositionControl:
    def __init__(self):
        print("Getting robot state... ")
        self.rs = RobotEnable(CHECK_VERSION)
        init_state = self.rs.state().enabled
        self.rs.enable()

        self.pose = PoseStamped()
        self.prevX = 0.65
        self.prevY = 0.0
        self.waypoints = []

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
        print('--------------------------------------------------------------------------------------------')
        print('')

    def gen_path(self):
        limb = Limb()
        for j in range (0, 1):
            if self.args["randomize"]:
                aX = random.uniform(0.0,0.17)
                aY = random.uniform(0.0,0.17)
                aZ = random.uniform(0.0,0.17)
                bX = 0#random.uniform(0.01,0.011)
                bY = 0#random.uniform(0.01,0.011)
                bZ = 0#random.uniform(0.01,0.011)
                gX = random.randint(0,1)
                gY = random.randint(0,1)
                gZ = random.randint(0,1)
                damper = 35

                print(aX, aY, aZ, bX, bY, bZ, gX, gY, gZ, damper)
            else:
                if self.args["condition"] == "rough":
                    aX = 0.1120
                    aY = 0.1230
                    aZ = 0.1568
                    bX = 0.0#0.0107
                    bY = 0.0#0.0108
                    bZ = 0.0#0.0120
      self.              gX = 0
                    gY = 0
                    gZ = 0
                    damper = 20
                elif self.args["condition"] == "calm":
                    aX = 0.0868659030530539
                    aY = 0.04920793027675307
                    aZ = 0.07766161850972929
                    bX = 0.0#10585086995477165
                    bY = 0.0#10244024420430944
                    bZ = 0.0#1094917954424499152
                    gX = 1
                    gY = 0
                    gZ = 0   
                    damper = 35
                elif self.args["condition"] == "average":
                    aX = 0.09035664457872972
                    aY = 0.06377560459928770
                    aZ = 0.05499189071730160
                    bX = 0.0#0.0107
                    bY = 0.0#0.0108
                    bZ = 0.0#0.0120
                    gX = 0
                    gY = 0
                    gZ = 0
                    damper = 38
                else:
                    print("'condition' arg not recognized, please restart the program")
                    exit(1)                 
            
            if gX == 0:
            	gX = -1
            if gY == 0:
            	gY = -1
            if gZ == 0:
            	gZ = -1
            for i in range (0, 240):
            	nextX = gX*math.exp(-1*bX*i)*math.sin(aX*math.pi*i)/damper + 0.65
            	nextY = gY*math.exp(-1*bY*i)*math.sin(aY*math.pi*i)/damper + 0.0
            	nextZ = gZ*math.exp(-1*bZ*i)*math.sin(aZ*math.pi*i)/damper + 0.5
            
            	roll  = (nextX - self.prevX)*4
            	pitch = (nextY - self.prevY)*2.25
            	q_base = quaternion_from_euler(0, math.pi/2, 0)
                q = quaternion_from_euler(0, pitch, -roll)
                q = quaternion_multiply(q_base, q)

            	self.prevX = nextX
            	self.prevY = nextY
            
            	newPose = PoseStamped()
            	newPose.header = Header(stamp=rospy.Time.now(), frame_id='base')
            	newPose.pose.position.x = nextX
            	newPose.pose.position.y = nextY
            	newPose.pose.position.z = nextZ
            	newPose.pose.orientation.x = q[0]
            	newPose.pose.orientation.y = q[1]
            	newPose.pose.orientation.z = q[2]
            	newPose.pose.orientation.w = q[3]
            
            	wpt_opts = MotionWaypointOptions(max_linear_speed=7.0, max_linear_accel=5.0, corner_distance=0.085)
            	waypoint = MotionWaypoint(options=wpt_opts.to_msg(), limb=limb)
            	waypoint.set_cartesian_pose(newPose, "right_hand", limb.joint_ordered_angles())
            	self.waypoints.append(copy(waypoint))
            	if len(self.waypoints) > 240:
            		self.waypoints.pop(0)

    def run(self):
        rate = rospy.Rate(100)
        limb = Limb()
        traj_options = TrajectoryOptions()
        traj_options.interpolation_type = TrajectoryOptions.CARTESIAN
        traj = MotionTrajectory(trajectory_options=traj_options, limb=limb)
    
        wpt_opts = MotionWaypointOptions(max_linear_speed=7.0, max_linear_accel=1.5, corner_distance=0.05)
        waypoint = MotionWaypoint(options=wpt_opts.to_msg(), limb=limb)
        
        q_base = quaternion_from_euler(0, math.pi/2, 0)
        q = quaternion_from_euler(0, 0, 0)
        q = quaternion_multiply(q_base, q)
        
        y_begin = 0.5
        z_begin = 0.5
        if self.args["box"]:
            init_loop = 6
        else:
            init_loop = 1
        for i in range(0,init_loop):
            traj.clear_waypoints()
            if i==0:
                y_begin = 0.0
                z_begin = 0.5
            elif i==1:
                y_begin = 0.15
                z_begin = 0.5
            elif i==2:
                y_begin = -0.15
                z_begin = 0.5
            elif i==3:
                y_begin = 0.0
                z_begin = 0.65
            elif i==4:
                y_begin = 0.0
                z_begin = 0.35
            else:
                y_begin = 0.0
                z_begin = 0.5
            
            self.pose.header = Header(stamp=rospy.Time.now(), frame_id='base')
            self.pose.pose.position.x = 0.65
            self.pose.pose.position.y = y_begin
            self.pose.pose.position.z = z_begin
            self.pose.pose.orientation.x = q[0]
            self.pose.pose.orientation.y = q[1]
            self.pose.pose.orientation.z = q[2]
            self.pose.pose.orientation.w = q[3]

            joint_angles = limb.joint_ordered_angles()
            waypoint.set_cartesian_pose(self.pose, "right_hand", joint_angles)
            
            rospy.loginfo("Sending initial waypoint...")t
            traj.append_waypoint(waypoint.to_msg())
            
            result = traj.send_trajectory()
            if result is None:
                    rospy.logerr('Trajectory FAILED to st
            
            elif result.result:
                rospy.loginfo('Motion controller successfully finished the trajectory!')
            else:
                rospy.logerr('Motion controller failed to complete the trajectory with error %s',
                        result.errorId)
                traj.clear_waypoints()

            if self.args["reset"]:
                return()


        
        l = Lights()
        l_name = 'head_green_light'
        initial_state = l.get_light_state(l_name)
        print("\nBlinking lights...\n")
        for i in range(0, 2):
        	state = not initial_state
        	l.set_light_state(l_name, state)
        	rospy.sleep(0.5)
        	state = not state
        	l.set_light_state(l_name, state)
        	rospy.sleep(0.5)
        
        l.set_light_state(l_name, True)
        
        traj.clear_waypoints()
        self.gen_path()
        for i in self.waypoints:
        	traj.append_waypoint(i.to_msg())
        
        print("Sending trajectory...")
        traj.send_trajectory(wait_for_result=False)
        	
        while not rospy.is_shutdown():
        	def clean_shutdown():
        		traj.stop_trajectory()
        		traj.clear_waypoints()
        
        		l = Lights()
        		l.set_light_state('head_green_light', False)
        		print("Rospy shutting down...")	
        	rospy.on_shutdown(clean_shutdown)
        
        	traj.clear_waypoints()	
        	self.gen_path()
        	for i in self.waypoints:
        		traj.append_waypoint(i.to_msg())
        
        	print("Waiting for old trajectory to complete...\n")
        	result = traj.wait_for_result()
        	if result is None:
        			rospy.logerr('Trajectory FAILED to send')
        
        	elif result.result:
        		rospy.loginfo('Motion controller successfully finished the trajectory!')
        	else:
        		rospy.logerr('Motion controller failed to complete the trajectory with error %s', result.errorId)
        
        	print("Sending trajectory...")
        	traj.send_trajectory(wait_for_result=False)
        	rate.sleep()
        return

print('')
print("Initializing node... ")
rospy.init_node("position_control")
print("Pose for arm set to front: ")
print("	Position: x: 0.5, y: 0.0, z: 0.5")
print("	Orientation: x: 0.0, y: 0.7, z: 0.0, w: 0.7\n\n")
position_control = PositionControl()
position_control.run()

print("\nExiting program.")
