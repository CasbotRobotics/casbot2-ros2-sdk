"""Query state, request WALK, then enter and leave each supported control mode."""
import rclpy
from casbot2_tools.interface_cli import InterfaceDemo


class ServiceModeDemo(InterfaceDemo):
    def run(self):
        self.cmd_get_robot_mode()
        self.cmd_get_robot_state()
        self.cmd_set_robot_mode('WALK')
        for service in ('/motion/switch_nav_mode', '/switch_teleoperation', '/switch_autonomous'):
            self.cmd_switch_bool(service, True)
            self.cmd_switch_bool(service, False)


def main():
    rclpy.init()
    node = ServiceModeDemo()
    try:
        node.run()
        return 0
    except (RuntimeError, TimeoutError) as exc:
        node.get_logger().error(str(exc))
        return 1
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    raise SystemExit(main())
