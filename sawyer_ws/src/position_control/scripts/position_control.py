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
import rospy
from geometry_msgs.msg import (
    PoseStamped,
    Pose,
    Quaternion,
)
from std_msgs.msg import Header, Bool
from sensor_msgs.msg import JointState

from intera_core_msgs.srv import (
    SolvePositionIK,
    SolvePositionIKRequest,
)
import intera_interface
from intera_interface import CHECK_VERSION

class PositionControl:
    def __init__(self):

	self.pub = rospy.Publisher('send_next_command', Bool, queue_size=1)
	self.commandPub = rospy.Publisher("/arm_motion_command", Pose, queue_size=10)
        rospy.Subscriber("/arm_motion_command", Pose, self.recv)
	rospy.Subscriber("/robot/joint_states", JointState, self.recv_curr_position)

        print("Getting robot state... ")
        rs = intera_interface.RobotEnable(CHECK_VERSION)
        init_state = rs.state().enabled

        rs.enable()

        self.pose = PoseStamped()
	self.command = Pose()
	#self.command.position.x = 0.75
	#self.command.position.z = 0.65
        self.commandRecv = False

	self.sendNext = Bool()
	self.sendNext.data = True

	self.limb_joints = None

    def recv(self, msg):
        hdr = Header(stamp=rospy.Time.now(), frame_id='base')
        self.pose.header = hdr
        self.pose.pose.orientation = msg.orientation
	self.pose.pose.position = msg.position

        self.commandRecv = True
        return

    def recv_curr_position(self, msg):
	if msg.name[0] == "right_gripper_l_finger_joint":
		return

	self.curr_position = dict(zip(msg.name, msg.position))
	try:	
		self.curr_position.pop("head_pan")
		self.curr_position.pop("torso_t0")
	except:
		return

	return

    def ik_service_client(self):
        ns = "ExternalTools/right/PositionKinematicsNode/IKService"
        iksvc = rospy.ServiceProxy(ns, SolvePositionIK)
        ikreq = SolvePositionIKRequest()

        ikreq.pose_stamp.append(self.pose)
        ikreq.tip_names.append('right_hand')

        ikreq.seed_mode = ikreq.SEED_USER
        seed = JointState()
        seed.name = ['right_j0', 'right_j1', 'right_j2', 'right_j3', 'right_j4', 'right_j5', 'right_j6']
        seed.position = [self.curr_position["right_j0"], self.curr_position["right_j1"], self.curr_position["right_j2"], self.curr_position["right_j3"], self.curr_position["right_j4"], self.curr_position["right_j5"], self.curr_position["right_j6"]]
        ikreq.seed_angles.append(seed)

        try:
            rospy.wait_for_service(ns, 5.0)
            resp = iksvc(ikreq)
        except (rospy.ServiceException, rospy.ROSException), e:
            rospy.logerr("Service call failed: %s" % (e,))
            return False

        if (resp.result_type[0] > 0):
	    seed_str = {
	                ikreq.SEED_USER: 'User Provided Seed',
	                ikreq.SEED_CURRENT: 'Current Joint Angles',
	                ikreq.SEED_NS_MAP: 'Nullspace Setpoints',
	               }.get(resp.result_type[0], 'None')
	    
	    self.limb_joints = dict(zip(resp.joints[0].name, resp.joints[0].position))
        else:
            rospy.logerr("INVALID POSE - No Valid Joint Solution Found.")
            rospy.logerr("Result Error %d", resp.result_type[0])
            return False

        return True

    def run(self):
        rate = rospy.Rate(100)
        limb = intera_interface.Limb("right")
        
        while not rospy.is_shutdown():
		    
		#if self.sendNext.data:
			#self.command.position.x -= 0.1
			#self.command.position.y = -0.75
			#self.command.position.z -= 0.05
			#self.command.orientation.x = .5
			#self.command.orientation.y = -0.5
			#self.command.orientation.z = .5
			#self.command.orientation.w = 0.5
		
			#self.commandPub.publish(self.command)
	    
            	if self.commandRecv:	

			if self.ik_service_client():
				#self.sendNext.data = False
				#self.pub.publish(self.sendNext)
						
				limb.move_to_joint_positions(self.limb_joints, timeout=10.0, threshold=intera_interface.settings.JOINT_ANGLE_TOLERANCE)
		
			self.commandRecv = False
            
	    	if self.limb_joints != None:
		    for i in self.limb_joints:
			     error = abs(self.curr_position[i] - self.limb_joints[i])
			     if error >= .05:
				     self.sendNext.data = False
				     break
			     else:
				     self.sendNext.data = True
	    	else:
			self.sendNext.data = True

	    	self.pub.publish(self.sendNext)
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
