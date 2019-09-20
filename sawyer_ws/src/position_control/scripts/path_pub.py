#!/usr/bin/env python

import rospy
from nav_msgs.msg import Path
from geometry_msgs.msg import Pose, PoseStamped
from intera_core_msgs.msg import EndpointState
from std_msgs.msg import Header

class PathPub:
    def __init__(self):
        print("I am Groot")
        self.pub = rospy.Publisher('endpoint_path', Path, queue_size=10)

        rospy.Subscriber("/robot/limb/right/endpoint_state", EndpointState, self.callback)

        self.poses = list()
    def callback(self, msg):
        out = Path()
        in_pose = msg.pose
        pose_stamped = PoseStamped
        pose_stamped.pose = in_pose
        pose_stamped.header = msg.header
        pose_stamped.header.frame_id = 'base'
        out.header = msg.header
        out.header.frame_id = 'base'
        #out.header = msg.header
        self.poses.append(pose_stamped)
        out.poses = self.poses

        self.pub.publish(out)

        return()

    def run(self):
        rate = rospy.Rate(100)
        while not rospy.is_shutdown():
            if len(self.poses) > 300:
                while len(self.poses) > 300:
                    trash = self.poses.pop(len(self.poses)-1)
            rate.sleep()

rospy.init_node("path_pub")
pathPub = PathPub()
pathPub.run()