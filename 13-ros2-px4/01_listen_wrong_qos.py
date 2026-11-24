import rclpy
from rclpy.node import Node
from px4_msgs.msg import VehicleLocalPosition, VehicleStatus


class Listener(Node):
    def __init__(self):
        super().__init__("listener")
        qos = 10
        self.create_subscription(VehicleLocalPosition, "/fmu/out/vehicle_local_position_v1", self.on_position, qos)
        self.create_subscription(VehicleStatus, "/fmu/out/vehicle_status_v1", self.on_status, qos)
        self.height = 0.0
        self.armed = False
        self.create_timer(1.0, self.report)

    def on_position(self, msg):
        self.height = max(0.0, -msg.z)

    def on_status(self, msg):
        self.armed = msg.arming_state == VehicleStatus.ARMING_STATE_ARMED

    def report(self):
        self.get_logger().info(f"height {self.height:5.1f} m   armed {self.armed}")


rclpy.init()
rclpy.spin(Listener())
