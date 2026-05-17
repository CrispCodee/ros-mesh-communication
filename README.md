# ROS Mesh Communication — Priority-Based Multi-Robot Disaster Area Patrol

A ROS1-based mesh communication system where multiple TurtleBot3 robots 
patrol a simulated disaster area and relay distress messages to a central 
tower node using a priority-based protocol with duplicate filtering.

---

## Overview

This project implements a decentralized mesh communication network for 
multi-robot systems using ROS1 Noetic and Gazebo. Four TurtleBot3 Burger 
robots autonomously patrol a simulated disaster environment, detect proximity 
events, and relay messages to a stationary tower node based on message 
priority. UUID-based duplicate filtering ensures redundant messages are 
suppressed at the tower.

---

## Features

- Priority-based message relay (HIGH / MID / LOW)
- UUID-based duplicate message filtering
- Autonomous patrol with collision avoidance
- Multi-robot mesh communication via ROS topics
- Simulated in Gazebo with TurtleBot3 Burger robots

---

## Running the Simulation

```bash
# Launch the multi-robot patrol simulation
roslaunch ros-mesh-communication [your launch file name].launch
```

---

## Authors

- Nanditha Maria George
- Kriselle Thomas
- Haninta Baby Joseph

Rajagiri School of Engineering and Technology (RSET), Kakkanad

---

## License

This project is for academic purposes.
