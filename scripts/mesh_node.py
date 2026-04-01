#!/usr/bin/env python3

import rospy
from std_msgs.msg import String
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
import json
import uuid
import math


class MeshNode:

    def __init__(self):
        rospy.init_node("mesh_node")

        self.last_trigger_time = 0
        self.cooldown = 3   # seconds

        # 🧠 Identity
        self.namespace = rospy.get_namespace().strip("/")

        # 📡 Communication
        self.pub = rospy.Publisher("/mesh_topic", String, queue_size=10)
        self.sub = rospy.Subscriber("/mesh_topic", String, self.callback)

        # 🤖 Movement
        self.vel_pub = rospy.Publisher(f"/{self.namespace}/cmd_vel", Twist, queue_size=10)

        # 📍 Position
        self.position = None
        self.other_positions = {}

        self.odom_sub = rospy.Subscriber(
            f"/{self.namespace}/odom",
            Odometry,
            self.odom_callback
        )

        self.pos_pub = rospy.Publisher("/positions", String, queue_size=10)
        self.pos_sub = rospy.Subscriber("/positions", String, self.pos_callback)

        # 🧠 Memory
        self.received_ids = set()

        self.sent = False

        self.rate = rospy.Rate(5)

    # 📡 MESSAGE CALLBACK
    def callback(self, msg):
        data = json.loads(msg.data)
        msg_id = data["id"]

        if msg_id in self.received_ids:
            return

        self.received_ids.add(msg_id)

        rospy.loginfo(f"{self.namespace} RECEIVED: {data}")

        if data["priority"] == "HIGH":
            if self.namespace != data["sender"]:
                self.move_forward()
                rospy.sleep(2)
                self.stop()

        if self.namespace != data["sender"]:
            rospy.loginfo(f"{self.namespace} RELAYING")
            self.pub.publish(msg.data)

    # 📍 ODOM
    def odom_callback(self, msg):
        self.position = msg.pose.pose.position

    # 📡 SHARE POSITION
    def publish_position(self):
        if self.position is None:
            return

        msg = {
            "robot": self.namespace,
            "x": self.position.x,
            "y": self.position.y
        }

        self.pos_pub.publish(json.dumps(msg))

    # 📡 RECEIVE POSITIONS
    def pos_callback(self, msg):
        data = json.loads(msg.data)

        if data["robot"] != self.namespace:
            self.other_positions[data["robot"]] = (data["x"], data["y"])

    # 📏 DISTANCE CHECK
    def check_distance(self):
        if self.position is None:
            return

        for robot, (x, y) in list(self.other_positions.items()):
            dx = self.position.x - x
            dy = self.position.y - y

            dist = math.sqrt(dx**2 + dy**2)

            rospy.loginfo(f"{self.namespace} distance to {robot}: {dist}")

            if dist < 3.0:
                rospy.loginfo(f"{self.namespace} CLOSE to {robot}")

                if self.namespace == "robot1" and not self.sent:
                    self.send_distress()
                    self.sent = True

                # 🤖 MOVE TOWARD THAT ROBOT
                self.move_towards(x, y)
        
    
    
    # 🚨 SEND DISTRESS
    def send_distress(self):
        msg = {
            "id": str(uuid.uuid4()),
            "sender": self.namespace,
            "priority": "HIGH",
            "data": "distress_signal"
        }

        self.pub.publish(json.dumps(msg))
        rospy.loginfo(f"{self.namespace} SENT distress")

    # 🤖 MOVE
    def move_forward(self):
        move = Twist()
        move.linear.x = 0.2
        self.vel_pub.publish(move)

    def stop(self):
        move = Twist()
        self.vel_pub.publish(move)

    # 🔁 MAIN LOOP
    def run(self):
        rospy.sleep(2)

        while not rospy.is_shutdown():
            self.publish_position()
            self.check_distance()
            self.rate.sleep()

    def move_towards(self, target_x, target_y):
        move = Twist()

        dx = target_x - self.position.x
        dy = target_y - self.position.y

        angle = math.atan2(dy, dx)

        move.linear.x = 0.2

        # 🔥 LIMIT rotation speed (PUT IT HERE)
        move.angular.z = max(min(angle, 1.0), -1.0)

        self.vel_pub.publish(move)

if __name__ == "__main__":
    node = MeshNode()
    node.run()