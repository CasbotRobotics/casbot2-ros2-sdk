import time

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from std_srvs.srv import SetBool



class BasicControlDemo(Node):
    def __init__(self) -> None:
        super().__init__("casbot2_py_control_demo")
        self.nav_mode_cli = self.create_client(SetBool, "/motion/switch_nav_mode")
        self.cmd_vel_pub = self.create_publisher(Twist, "/navigation/cmd_vel", 10)

    def switch_nav_mode(self, enable_nav: bool) -> bool:
        if not self.nav_mode_cli.wait_for_service(timeout_sec=3.0):
            self.get_logger().error("Service /motion/switch_nav_mode not available")
            return False
        req = SetBool.Request()
        req.data = enable_nav
        future = self.nav_mode_cli.call_async(req)
        rclpy.spin_until_future_complete(self, future, timeout_sec=3.0)
        resp = future.result()
        if resp is None:
            self.get_logger().error("Failed to call /motion/switch_nav_mode")
            return False
        target = "NAVIGATION" if enable_nav else "IDLE_MODE"
        self.get_logger().info(
            f"switch_nav_mode({target}): success={resp.success}, msg={resp.message}"
        )
        return bool(resp.success)

    def send_cmd_vel(self, vx: float, wz: float) -> None:
        msg = Twist()
        msg.linear.x = float(vx)
        msg.angular.z = float(wz)
        self.cmd_vel_pub.publish(msg)


def main() -> None:
    rclpy.init()
    node = BasicControlDemo()

    entered = False
    exited = False
    try:
        entered = node.switch_nav_mode(True)
        if not entered:
            return 1
        for _ in range(20):
            if not rclpy.ok():
                break
            node.send_cmd_vel(0.2, 0.0)
            rclpy.spin_once(node, timeout_sec=0.0)
            time.sleep(0.1)
    finally:
        if entered and rclpy.ok():
            for _ in range(10):
                node.send_cmd_vel(0.0, 0.0)
                rclpy.spin_once(node, timeout_sec=0.05)
            exited = node.switch_nav_mode(False)
            if not exited:
                node.get_logger().error('退出导航失败，请检查 /motion/status')
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
    return 0 if exited else 1


if __name__ == "__main__":
    raise SystemExit(main())
