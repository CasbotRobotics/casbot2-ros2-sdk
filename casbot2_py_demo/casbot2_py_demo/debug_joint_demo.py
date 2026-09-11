"""Upper-body then whole-body hold commands; default PD configuration required."""
import time
import rclpy
from sensor_msgs.msg import JointState
from crb_ros_msg.msg import JointStateData, UpperJointData
from casbot2_tools.interface_cli import InterfaceDemo


class DebugJointDemo(InterfaceDemo):
    def __init__(self):
        super().__init__()
        self.latest = None
        self.create_subscription(JointState, '/joint_states', self.on_state, 10)

    def on_state(self, msg):
        self.latest = msg

    def run(self):
        deadline = time.monotonic() + 5.0
        while self.latest is None and time.monotonic() < deadline:
            rclpy.spin_once(self, timeout_sec=0.05)
        if self.latest is None or not self.latest.name:
            raise RuntimeError('缺少 /joint_states，不能构造保持姿态命令')
        names = list(self.latest.name)
        positions = list(self.latest.position)
        index = names.index('left_shoulder_pitch_joint')
        for service, msg, topic in (
            ('/motion/upper_body_debug', UpperJointData(vel_scale=0.05), '/upper_body_debug/joint_cmd'),
            ('/motion/whole_body_debug', JointStateData(), '/motion/debug/joint_cmd'),
        ):
            # Whole-body messages include every measured joint, retaining leg/arm pose.
            msg.name = [names[index]] if isinstance(msg, UpperJointData) else names
            msg.position = [positions[index]] if isinstance(msg, UpperJointData) else positions
            msg.velocity = [0.0] * len(msg.name)
            msg.effort = [0.0] * len(msg.name)
            pub = self.create_publisher(type(msg), topic, 10)
            self.cmd_switch_bool(service, True)
            try:
                for _ in range(20):
                    msg.header.stamp = self.get_clock().now().to_msg()
                    self.publish_once(pub, msg)
            finally:
                self.cmd_switch_bool(service, False)


def main():
    rclpy.init()
    node = DebugJointDemo()
    try:
        node.run()
        return 0
    except (RuntimeError, ValueError, TimeoutError) as exc:
        node.get_logger().error(str(exc))
        return 1
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    raise SystemExit(main())
