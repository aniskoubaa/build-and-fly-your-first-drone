import math
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data as QOS
from px4_msgs.msg import OffboardControlMode, TrajectorySetpoint, VehicleCommand, VehicleLocalPosition

SQUARE = [[0.0, 0.0, -5.0],
          [10.0, 0.0, -5.0],
          [10.0, 10.0, -5.0],
          [0.0, 10.0, -5.0],
          [0.0, 0.0, -5.0]]


class Pilot(Node):
    def __init__(self):
        super().__init__("pilot")
        self.mode_pub = self.create_publisher(OffboardControlMode, "/fmu/in/offboard_control_mode", QOS)
        self.target_pub = self.create_publisher(TrajectorySetpoint, "/fmu/in/trajectory_setpoint", QOS)
        self.command_pub = self.create_publisher(VehicleCommand, "/fmu/in/vehicle_command", QOS)
        self.create_subscription(VehicleLocalPosition, "/fmu/out/vehicle_local_position_v1", self.on_position, QOS)
        self.pos = [0.0, 0.0, 0.0]
        self.ticks = 0
        self.step = 0
        self.landing = False
        self.create_timer(0.1, self.loop)

    def on_position(self, msg):
        self.pos = [msg.x, msg.y, msg.z]

    def now(self):
        return self.get_clock().now().nanoseconds // 1000

    def command(self, cmd, p1=0.0, p2=0.0):
        self.command_pub.publish(VehicleCommand(command=cmd, param1=p1, param2=p2, target_system=1,
                                                target_component=1, source_system=1, source_component=1,
                                                from_external=True, timestamp=self.now()))

    def loop(self):
        target = SQUARE[self.step]
        self.mode_pub.publish(OffboardControlMode(position=True, timestamp=self.now()))
        self.target_pub.publish(TrajectorySetpoint(position=target, yaw=0.0, timestamp=self.now()))
        if self.ticks == 10:
            self.command(VehicleCommand.VEHICLE_CMD_DO_SET_MODE, 1.0, 6.0)
            self.command(VehicleCommand.VEHICLE_CMD_COMPONENT_ARM_DISARM, 1.0)
            self.get_logger().info("Offboard mode, armed")
        if math.dist(self.pos, target) < 0.5 and not self.landing:
            self.get_logger().info(f"Reached point {self.step}: {target}")
            if self.step < len(SQUARE) - 1:
                self.step += 1
            else:
                self.command(VehicleCommand.VEHICLE_CMD_NAV_LAND)
                self.get_logger().info("Landing")
                self.landing = True
        if self.landing and -self.pos[2] < 0.2:
            self.get_logger().info("Landed")
            raise SystemExit
        self.ticks += 1


rclpy.init()
try:
    rclpy.spin(Pilot())
except SystemExit:
    pass
