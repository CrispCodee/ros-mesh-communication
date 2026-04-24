#!/usr/bin/env python3

import rospy
from std_msgs.msg import String
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
import json
import uuid
import math
import random


class MeshNode:

    def __init__(self):
        rospy.init_node("mesh_node")

        self.namespace = rospy.get_namespace().strip("/")

        self.pub = rospy.Publisher("/mesh_topic", String, queue_size=10)
        self.sub = rospy.Subscriber("/mesh_topic", String, self.callback)

        self.vel_pub = rospy.Publisher(f"/{self.namespace}/cmd_vel", Twist, queue_size=10)

        self.position = None
        self.other_positions = {}

        self.odom_sub = rospy.Subscriber(
            f"/{self.namespace}/odom",
            Odometry,
            self.odom_callback
        )

        self.pos_pub = rospy.Publisher("/positions", String, queue_size=10)
        self.pos_sub = rospy.Subscriber("/positions", String, self.pos_callback)

        self.received_ids = set()
        self.sent = False
        self.last_trigger_time = 0
        self.cooldown = 8

        # patrol
        self.last_turn_time = 0
        self.current_turn = 0.0

        self.rate = rospy.Rate(5)

        rospy.loginfo(f"{'='*50}")
        rospy.loginfo(f"  [{self.namespace.upper()}] NODE STARTED")
        rospy.loginfo(f"{'='*50}")

    def callback(self, msg):
        data = json.loads(msg.data)
        msg_id = data["id"]

        if msg_id in self.received_ids:
            return

        self.received_ids.add(msg_id)

        rospy.loginfo(f"")
        rospy.loginfo(f"[{self.namespace.upper()}] *** MESSAGE RECEIVED ***")
        rospy.loginfo(f"[{self.namespace.upper()}]   From     : {data['sender']}")
        rospy.loginfo(f"[{self.namespace.upper()}]   Msg ID   : {data['id'][:8]}...")
        rospy.loginfo(f"[{self.namespace.upper()}]   Priority : {data['priority']}")
        rospy.loginfo(f"[{self.namespace.upper()}]   Content  : {data['data']}")

        if data["priority"] == "HIGH":
            rospy.loginfo(f"[{self.namespace.upper()}]   ACTION   : HIGH PRIORITY - Relaying immediately")

        elif data["priority"] == "MID":
            rospy.loginfo(f"[{self.namespace.upper()}]   ACTION   : MID PRIORITY - Relaying with delay")

        elif data["priority"] == "LOW":
            rospy.loginfo(f"[{self.namespace.upper()}]   ACTION   : LOW PRIORITY - Not relaying")

        if self.namespace != data["sender"]:
            if data["priority"] == "HIGH":
                rospy.loginfo(f"[{self.namespace.upper()}]   RELAY    : Forwarding immediately")
                self.pub.publish(msg.data)

            elif data["priority"] == "MID":
                rospy.loginfo(f"[{self.namespace.upper()}]   RELAY    : Forwarding after 2s delay")
                rospy.sleep(2)
                self.pub.publish(msg.data)

            elif data["priority"] == "LOW":
                rospy.loginfo(f"[{self.namespace.upper()}]   RELAY    : Dropped (LOW priority)")

        rospy.loginfo(f"[{self.namespace.upper()}] *** END MESSAGE ***")
        rospy.loginfo(f"")

    def odom_callback(self, msg):
        self.position = msg.pose.pose.position

    def publish_position(self):
        if self.position is None:
            return

        msg = {
            "robot": self.namespace,
            "x": round(self.position.x, 3),
            "y": round(self.position.y, 3)
        }
        self.pos_pub.publish(json.dumps(msg))

    def pos_callback(self, msg):
        data = json.loads(msg.data)
        if data["robot"] != self.namespace:
            self.other_positions[data["robot"]] = (data["x"], data["y"])

    def check_distance(self):
        if self.position is None:
            return

        current_time = rospy.get_time()

        closest_robot = None
        min_dist = float('inf')

        for robot, (x, y) in list(self.other_positions.items()):
            dx = self.position.x - x
            dy = self.position.y - y
            dist = math.sqrt(dx**2 + dy**2)

            if dist < min_dist:
                min_dist = dist
                closest_robot = robot

        if min_dist < 0.3:
            move = Twist()
            move.linear.x = -0.1  # back up slightly
             # odd robots turn left, even robots turn right
            if self.namespace[-1] in ['1', '3']:
                move.angular.z = 1.5
            else:
                move.angular.z = -1.5
            self.vel_pub.publish(move)
            return

        if closest_robot and min_dist < 3.0 and (current_time - self.last_trigger_time > self.cooldown):
            rospy.loginfo(f"")
            rospy.loginfo(f"[{self.namespace.upper()}] --- PROXIMITY DETECTED ---")
            rospy.loginfo(f"[{self.namespace.upper()}]   My position   : ({self.position.x:.2f}, {self.position.y:.2f})")
            rospy.loginfo(f"[{self.namespace.upper()}]   Nearest robot : {closest_robot}")
            rospy.loginfo(f"[{self.namespace.upper()}]   Distance      : {min_dist:.2f}m")
            rospy.loginfo(f"[{self.namespace.upper()}]   Threshold     : 3.0m")

            self.last_trigger_time = current_time

            
            if min_dist < 1.0:
                self.send_distress("HIGH", "person_detected")
            elif min_dist < 3.0:
                self.send_distress("MID", "robot_nearby")
            

    def send_distress(self, priority, data_content):
        msg_id = str(uuid.uuid4())
        msg = {
            "id": msg_id,
            "sender": self.namespace,
            "priority": priority,
            "data": data_content
        }

        self.pub.publish(json.dumps(msg))

        rospy.loginfo(f"")
        rospy.loginfo(f"[{self.namespace.upper()}] *** DISTRESS SIGNAL SENT ***")
        rospy.loginfo(f"[{self.namespace.upper()}]   Msg ID   : {msg_id[:8]}...")
        rospy.loginfo(f"[{self.namespace.upper()}]   Priority : {priority}")
        rospy.loginfo(f"[{self.namespace.upper()}]   Content  : {data_content}")
        if self.position:
            rospy.loginfo(f"[{self.namespace.upper()}]   Position : ({self.position.x:.2f}, {self.position.y:.2f})")
        else:
            rospy.loginfo(f"[{self.namespace.upper()}]   Position : unknown")
        rospy.loginfo(f"")

    def patrol(self):
        current_time = rospy.get_time()

        # pick a new random direction every 3 seconds
        if current_time - self.last_turn_time > 3.0:
            self.current_turn = random.uniform(-1.0, 1.0)
            self.last_turn_time = current_time

        move = Twist()
        move.linear.x = 0.15
        move.angular.z = self.current_turn
        self.vel_pub.publish(move)

    def run(self):
        rospy.sleep(2)

        while not rospy.is_shutdown():
            self.publish_position()
            self.check_distance()
            self.patrol()
            self.rate.sleep()


if __name__ == "__main__":
    node = MeshNode()
    node.run()