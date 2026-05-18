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
<p align="center">
  <img src="https://github.com/user-attachments/assets/5dea9141-2600-4a56-9dfd-603bfe3a4289" width="70%" alt="Gazebo Simulation Map">
</p>


## Priority Protocol

| Priority | Trigger Condition | Relay Behavior | Tower Response |
|---|---|---|---|
| HIGH | Robot within 2.0m | Immediate relay | Emergency alert |
| MID | Robot within 3.0m | 2s delay per hop | Advisory logged |
| LOW | Default | No relay | Quiet log |

<p align="center">
  <img src="https://github.com/user-attachments/assets/c580c530-3ccd-4322-98ad-0c3350b5e149" width="70%" alt="Gazebo Simulation Map">
</p>

---

## System Requirements

- Ubuntu 20.04 LTS
- ROS1 Noetic
- Gazebo
- TurtleBot3 packages
- Python 3

---


## Running the Simulation

```bash
# Launch the multi-robot patrol simulation
roslaunch ros-mesh-communication [your launch file name].launch
```

---
<p align="center">
  <img src="https://github.com/user-attachments/assets/597aa2c0-dd6b-4eeb-9640-8d1e322b212b" width="70%" alt="Gazebo Simulation Map">
</p>


## Results Summary

| Metric | HIGH Priority | MID Priority |
|---|---|---|
| Average Latency | 0.0043s | 0.0017s |
| Maximum Latency | 0.0110s | 0.0070s |
| Delivery Rate | 100% | 100% |
| Duplicates per Message | ~3 | ~3 |

UUID-based filtering achieved a ~94% reduction in redundant message 
processing compared to an unfiltered baseline.
<p align="center">
  <video src="https://github.com/user-attachments/assets/e778cbbd-3071-4950-89bc-7c1ce158f0bc" width="85%" controls>
    Your browser does not support the video tag.
  </video>
</p>
---

## Authors

- Nanditha Maria George
- Kriselle Thomas
- Haninta Baby Joseph

Rajagiri School of Engineering and Technology (RSET), Kakkanad

---

## License

This project is for academic purposes.
