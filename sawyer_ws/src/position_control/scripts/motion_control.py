#!/usr/bin/env python

# Copyright (c) 2013-2018, Rethink Robotics Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Intera RSDK Inverse Kinematics Example
"""
import rospy, random
from geometry_msgs.msg import (
    PoseStamped,
    Pose,
)
from std_msgs.msg import Header, Bool
from sensor_msgs.msg import JointState

from intera_core_msgs.srv import (
    SolvePositionIK,
    SolvePositionIKRequest,
)
import intera_interface
from intera_interface import CHECK_VERSION, Limb, Lights

from intera_motion_msgs.msg import TrajectoryOptions
from intera_motion_interface import (
	MotionTrajectory,
	MotionWaypoint,
	MotionWaypointOptions
)


class PositionControl:
    def __init__(self):

	self.commandPub = rospy.Publisher("/arm_motion_command", Pose, queue_size=10)
	rospy.Subscriber("/robot/joint_states", JointState, self.recv_curr_position)

        print("Getting robot state... ")
        self.rs = intera_interface.RobotEnable(CHECK_VERSION)
        init_state = self.rs.state().enabled
        self.rs.enable()

        self.pose = PoseStamped()
	self.waypoints = []

	self.curr_position = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

    def recv_curr_position(self, msg):
	if msg.name[0] == "right_gripper_l_finger_joint":
		return


	inter_msg = dict(zip(msg.name, msg.position))
	inter_msg.pop("torso_t0")
	inter_msg.pop("head_pan")

	counter = 0
	for i in inter_msg.values():
		self.curr_position[counter] = i
		counter += 1

	return

    def gen_rand_waypoint(self):
	newX = (random.random()/5) - 0.1
	newY = (random.random()/5) - 0.7
	newZ = (random.random()/5) + 0.4
	
	newPose = PoseStamped()
	newPose.header = Header(stamp=rospy.Time.now(), frame_id='base')
	newPose.pose.position.x = newX
	newPose.pose.position.y = newY
	newPose.pose.position.z = newZ
	newPose.pose.orientation.x = 0.5
	newPose.pose.orientation.y = -0.5
	newPose.pose.orientation.z = 0.5
	newPose.pose.orientation.w = 0.5

	limb = Limb()
	wpt_opts = MotionWaypointOptions(max_joint_speed_ratio=1.0, max_joint_accel=1.0, corner_distance=0.05)
	waypoint = MotionWaypoint(options=wpt_opts.to_msg(), limb=limb)
	waypoint.set_cartesian_pose(newPose, "right_hand", limb.joint_ordered_angles())

	self.waypoints.append(waypoint)

    def run(self):
        rate = rospy.Rate(100)
	limb = Limb()
	traj_options = TrajectoryOptions()
	traj_options.interpolation_type = TrajectoryOptions.CARTESIAN
	traj = MotionTrajectory(trajectory_options=traj_options, limb=limb)

	wpt_opts = MotionWaypointOptions(max_joint_speed_ratio=0.5, max_joint_accel=0.5, corner_distance=0.05)
	waypoint = MotionWaypoint(options=wpt_opts.to_msg(), limb=limb)

	self.pose.header = Header(stamp=rospy.Time.now(), frame_id='base')
	self.pose.pose.position.x = 0.0
	self.pose.pose.position.y = -0.6
	self.pose.pose.position.z = 0.5
	self.pose.pose.orientation.x = 0.5
	self.pose.pose.orientation.y = -0.5
	self.pose.pose.orientation.z = 0.5
	self.pose.pose.orientation.w = 0.5

	joint_angles = limb.joint_ordered_angles()
	waypoint.set_cartesian_pose(self.pose, "right_hand", joint_angles)
	self.waypoints.append(waypoint)

	rospy.loginfo("Sending inital waypoint: %s", self.waypoints[0].to_string())
	traj.append_waypoint(self.waypoints[0].to_msg())

	result = traj.send_trajectory()
	if result is None:
    		rospy.logerr('Trajectory FAILED to send')

	elif result.result:
	    rospy.loginfo('Motion controller successfully finished the trajectory!')
	else:
	    rospy.logerr('Motion controller failed to complete the trajectory with error %s',
			 result.errorId)
	    traj.clear_waypoints()

	l = Lights()
	l_name = 'head_green_light'
	initial_state = l.get_light_state(l_name)
	for i in range(0, 2):
		state = not initial_state
		l.set_light_state(l_name, state)
		rospy.sleep(0.5)
		state = not state
		l.set_light_state(l_name, state)
		rospy.sleep(0.5)

	l.set_light_state(l_name, True)

	for i in range(0, 19):
		self.gen_rand_waypoint()

	sendCommand = True
        
        while not rospy.is_shutdown():
		traj.clear_waypoints()
		for i in range(0, 19):
			self.waypoints.pop(i)
			self.gen_rand_waypoint()
			
		for point in self.waypoints: 
			traj.append_waypoint(point.to_msg())

		print(len(self.waypoints))
		result = traj.send_trajectory(wait_for_result=True)

		self.firstShutdown = True
		def clean_shutdown():
			if self.firstShutdown:
				print("STOPPING TRAJECTORY")
				traj.stop_trajectory()
				traj.clear_waypoints()

				l = Lights()
				l.set_light_state('head_green_light', False)		
				self.firstShutdown = False
		rospy.on_shutdown(clean_shutdown)
            	rate.sleep()
        return

print("Initializing node... ")
rospy.init_node("position_control")
print("Pose for arm set to right: ")
print("	Position: x: 0.0, y: -0.75, z: 0.5")
print("	Orientation: x: 0.5, y: -0.5, z: 0.5, w: 0.5\n\n")
position_control = PositionControl()
position_control.run()

print("\nExiting program.")
