#!/usr/bin/env python3

import rospy
from std_msgs.msg import String
from geometry_msgs.msg import Twist
import json
import uuid


class MeshNode:

    def __init__(self):
        rospy.init_node("mesh_node")

        # 🧠 Identity
        self.namespace = rospy.get_namespace().strip("/")

        # 📡 Publishers
        self.pub = rospy.Publisher("/mesh_topic", String, queue_size=10)
        self.vel_pub = rospy.Publisher(f"/{self.namespace}/cmd_vel", Twist, queue_size=10)

        # 📡 Subscriber
        self.sub = rospy.Subscriber("/mesh_topic", String, self.callback)

        # 🧠 Memory
        self.received_ids = set()

        # 🚨 Send control
        self.sent = False

        self.rate = rospy.Rate(1)

    # 📡 Callback
    def callback(self, msg):
        data = json.loads(msg.data)
        msg_id = data["id"]

        # 🔁 Ignore duplicates
        if msg_id in self.received_ids:
            return

        self.received_ids.add(msg_id)

        rospy.loginfo(f"{self.namespace} RECEIVED: {data}")

        # 🚨 React to distress
        if data["priority"] == "HIGH":
            rospy.loginfo(f"{self.namespace} reacting to distress")

            if self.namespace != data["sender"]:
                self.move_forward()
                rospy.sleep(2)   # move for 2 seconds
                self.stop()

        # 📡 Relay
        if self.namespace != data["sender"]:
            rospy.loginfo(f"{self.namespace} RELAYING message")
            self.pub.publish(msg.data)

    # 🚨 Send distress
    def send_distress(self):
        msg = {
            "id": str(uuid.uuid4()),
            "sender": self.namespace,
            "priority": "HIGH",
            "data": "distress_signal"
        }

        self.pub.publish(json.dumps(msg))
        rospy.loginfo(f"{self.namespace} SENT distress signal")

    # 🤖 Movement
    def move_forward(self):
        move = Twist()
        move.linear.x = 0.2
        move.angular.z = 0.0
        self.vel_pub.publish(move)

    def run(self):
        rospy.sleep(2)

        while not rospy.is_shutdown():

            if self.namespace == "robot1" and not self.sent:
                self.send_distress()
                self.sent = True

            self.rate.sleep()
    def stop(self):
        move = Twist()
        move.linear.x = 0.0
        move.angular.z = 0.0
        self.vel_pub.publish(move)

if __name__ == "__main__":
    node = MeshNode()
    node.run()