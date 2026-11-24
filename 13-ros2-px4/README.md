# Episode 13: ROS 2 + PX4 for beginners

Video: https://youtu.be/-oroXuus-3I

Three ROS 2 Python nodes that talk to PX4 through the uXRCE-DDS bridge, in the Gazebo simulator.

| File | What it does |
|---|---|
| `01_listen.py` | Reads `/fmu/out/vehicle_local_position_v1` and `/fmu/out/vehicle_status_v1`, prints the height and the armed state every second |
| `01_listen_wrong_qos.py` | The same node with the default QoS (`10`): it receives **nothing**. PX4 publishes with best-effort QoS, so a subscriber must use `qos_profile_sensor_data` |
| `02_takeoff.py` | Offboard mode: streams a setpoint 5 m above home, switches to Offboard, arms, climbs, lands about 14 s later |
| `03_square.py` | Offboard mode: flies a 10 m square at 5 m height, then lands |

## Tested with

- Ubuntu 24.04, ROS 2 Jazzy
- PX4-Autopilot v1.17.0, Gazebo Harmonic, model `gz_x500`
- Micro XRCE-DDS Agent v2.4.3
- QGroundControl 5.1.5 (keep it open: PX4 1.17 will not arm with no ground station connected)

## Install (one time)

1. ROS 2 Jazzy: https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html
2. PX4 and Gazebo:
   ```bash
   git clone --recursive -b v1.17.0 https://github.com/PX4/PX4-Autopilot.git ~/PX4-Autopilot
   bash ~/PX4-Autopilot/Tools/setup/ubuntu.sh
   ```
3. Micro XRCE-DDS Agent:
   ```bash
   git clone -b v2.4.3 https://github.com/eProsima/Micro-XRCE-DDS-Agent.git
   cd Micro-XRCE-DDS-Agent && mkdir build && cd build
   cmake .. && make && sudo make install && sudo ldconfig /usr/local/lib/
   ```
4. The PX4 messages for ROS 2 (branch matching PX4 1.17):
   ```bash
   mkdir -p ~/ws/src && cd ~/ws/src
   git clone -b release/1.17 https://github.com/PX4/px4_msgs.git
   cd ~/ws && colcon build
   ```

## Run

Terminal 1, the Agent:
```bash
MicroXRCEAgent udp4 -p 8888
```

Terminal 2, PX4 with Gazebo (wait for `Ready for takeoff`):
```bash
cd ~/PX4-Autopilot
make px4_sitl gz_x500
```

Open QGroundControl. Then, in terminal 3:
```bash
source /opt/ros/jazzy/setup.bash
source ~/ws/install/setup.bash
python3 01_listen.py      # or 02_takeoff.py, 03_square.py
```

Check the topics with `ros2 topic list` (they start with `/fmu/out/` and `/fmu/in/`).

## Notes

- PX4 uses NED coordinates: z points down, so 5 m up is `z = -5.0`.
- Offboard mode needs a stream of `OffboardControlMode` and `TrajectorySetpoint` (here at 10 Hz) **before**
  switching to Offboard; if the stream stops, PX4 leaves Offboard (failsafe).
- `VEHICLE_CMD_DO_SET_MODE` with `param1 = 1`, `param2 = 6` selects the Offboard mode.
- Some message topics carry a version suffix in PX4 1.17 (`vehicle_local_position_v1`, `vehicle_status_v1`).
  Use `ros2 topic list` if your PX4 version names them differently.
