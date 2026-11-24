import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data as QOS
from px4_msgs.msg import OffboardControlMode, TrajectorySetpoint, VehicleCommand, VehicleLocalPosition


class Pilot(Node):
    def __init__(self):
        super().__init__("pilot")
        self.mode_pub = self.create_publisher(OffboardControlMode, "/fmu/in/offboard_control_mode", QOS)
        self.target_pub = self.create_publisher(TrajectorySetpoint, "/fmu/in/trajectory_setpoint", QOS)
        self.command_pub = self.create_publisher(VehicleCommand, "/fmu/in/vehicle_command", QOS)
        self.create_subscription(VehicleLocalPosition, "/fmu/out/vehicle_local_position_v1", self.on_position, QOS)
        self.height = 0.0
        self.ticks = 0
        self.create_timer(0.1, self.loop)

    def on_position(self, msg):
        self.height = max(0.0, -msg.z)

    def now(self):
        return self.get_clock().now().nanoseconds // 1000

    def command(self, cmd, p1=0.0, p2=0.0):
        self.command_pub.publish(VehicleCommand(command=cmd, param1=p1, param2=p2, target_system=1,
                                                target_component=1, source_system=1, source_component=1,
                                                from_external=True, timestamp=self.now()))

    def loop(self):
        self.mode_pub.publish(OffboardControlMode(position=True, timestamp=self.now()))
        self.target_pub.publish(TrajectorySetpoint(position=[0.0, 0.0, -5.0], yaw=0.0, timestamp=self.now()))
        if self.ticks == 10:
            self.command(VehicleCommand.VEHICLE_CMD_DO_SET_MODE, 1.0, 6.0)
            self.command(VehicleCommand.VEHICLE_CMD_COMPONENT_ARM_DISARM, 1.0)
            self.get_logger().info("Offboard mode, armed")
        if self.ticks % 10 == 0:
            self.get_logger().info(f"height {self.height:4.1f} m")
        if self.ticks == 150:
            self.command(VehicleCommand.VEHICLE_CMD_NAV_LAND)
            self.get_logger().info("Landing")
        if self.ticks > 160 and self.height < 0.2:
            self.get_logger().info("Landed")
            raise SystemExit
        self.ticks += 1


rclpy.init()
try:
    rclpy.spin(Pilot())
except SystemExit:
    pass
