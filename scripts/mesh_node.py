#!/usr/bin/env python3

import rospy
from std_msgs.msg import String
import json
import uuid

class MeshNode:

    def __init__(self):
        rospy.init_node("mesh_node")

        # Identity
        self.namespace = rospy.get_namespace().strip("/")

        # Communication
        self.pub = rospy.Publisher("/mesh_topic", String, queue_size=10)
        self.sub = rospy.Subscriber("/mesh_topic", String, self.callback)

        # Memory (for duplicate filtering)
        self.received_ids = set()

        # Control sending once
        self.sent = False

        self.rate = rospy.Rate(1)

    # Callback = when message is received
    def callback(self, msg):
        data = json.loads(msg.data)
        msg_id = data["id"]

        # Duplicate filter
        if msg_id in self.received_ids:
            return

        self.received_ids.add(msg_id)

        rospy.loginfo(f"{self.namespace} processed: {data}")

    # Send distress (only robot1)
    def send_distress(self):
        msg = {
            "id": str(uuid.uuid4()),
            "sender": self.namespace,
            "priority": "HIGH",
            "data": "distress_signal"
        }

        self.pub.publish(json.dumps(msg))
        rospy.loginfo(f"{self.namespace} SENT distress signal")

    def run(self):
        while self.pub.get_num_connections() == 0:
            rospy.loginfo("Waiting for subscribers...")
            rospy.sleep(1)

        while not rospy.is_shutdown():
            if self.namespace == "robot1" and not self.sent:
                self.send_distress()
                self.sent = True

            self.rate.sleep()


if __name__ == "__main__":
    node = MeshNode()
    node.run()