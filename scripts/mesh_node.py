#!/usr/bin/env python3

import rospy
from std_msgs.msg import String

def callback(msg):
    rospy.loginfo(f"{namespace} received: {msg.data}")

if __name__ == "__main__":
    rospy.init_node("mesh_node")

    namespace = rospy.get_namespace().strip("/")

    pub = rospy.Publisher("/mesh_topic", String, queue_size=10)
    sub = rospy.Subscriber("/mesh_topic", String, callback)

    rate = rospy.Rate(1)

    while not rospy.is_shutdown():

        # Only robot1 sends messages
        if namespace == "robot1":
            message = "distress_signal"
            rospy.loginfo(f"{namespace} sending: {message}")
            pub.publish(message)

        rate.sleep()