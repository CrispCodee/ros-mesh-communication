#!/usr/bin/env python3

import rospy
from std_msgs.msg import String
import json

class TowerNode:

    def __init__(self):
        rospy.init_node("tower_node")

        self.received_ids = set()

        self.sub = rospy.Subscriber("/mesh_topic", String, self.callback)

        rospy.loginfo("="*50)
        rospy.loginfo("  [TOWER] EMERGENCY RESPONSE TOWER ONLINE")
        rospy.loginfo("  [TOWER] Waiting for distress signals...")
        rospy.loginfo("="*50)

    def callback(self, msg):
        data = json.loads(msg.data)
        msg_id = data["id"]

        # duplicate filter
        if msg_id in self.received_ids:
            return
        self.received_ids.add(msg_id)

        rospy.loginfo(f"")

        if data["priority"] == "HIGH":
            rospy.loginfo(f"[TOWER] !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            rospy.loginfo(f"[TOWER] !!! EMERGENCY ALERT !!!")
            rospy.loginfo(f"[TOWER] !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            rospy.loginfo(f"[TOWER]   From     : {data['sender']}")
            rospy.loginfo(f"[TOWER]   Priority : {data['priority']}")
            rospy.loginfo(f"[TOWER]   Message  : {data['data']}")
            rospy.loginfo(f"[TOWER]   ACTION   : Notifying rescue team immediately!")
            rospy.loginfo(f"[TOWER] !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

        elif data["priority"] == "MID":
            rospy.loginfo(f"[TOWER] --- ADVISORY RECEIVED ---")
            rospy.loginfo(f"[TOWER]   From     : {data['sender']}")
            rospy.loginfo(f"[TOWER]   Priority : {data['priority']}")
            rospy.loginfo(f"[TOWER]   Message  : {data['data']}")
            rospy.loginfo(f"[TOWER]   ACTION   : Logged for monitoring")
            rospy.loginfo(f"[TOWER] ----------------")

        elif data["priority"] == "LOW":
            rospy.loginfo(f"[TOWER] [info] Low priority update from {data['sender']}: {data['data']}")

        rospy.loginfo(f"")

    def run(self):
        rospy.spin()


if __name__ == "__main__":
    node = TowerNode()
    node.run()