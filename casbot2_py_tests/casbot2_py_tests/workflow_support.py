"""Explicit robot workflows; never collected or invoked by offline tests."""
import time

import rclpy
from sensor_msgs.msg import JointState
from std_msgs.msg import String
from std_srvs.srv import SetBool
from crb_ros_msg.srv import GetRobotState, SetRobotMode
from casbot2_tools.interface_cli import InterfaceDemo


class WorkflowNode(InterfaceDemo):
    def __init__(self):
        super().__init__()
        self.status = None
        self.joints = None
        self.joint_count = 0
        self.create_subscription(String, '/motion/status', self._status, 10)
        self.create_subscription(JointState, '/joint_states', self._joints, 10)

    def _status(self, msg):
        self.status = msg.data

    def _joints(self, msg):
        self.joints = msg
        self.joint_count += 1

    def wait(self, predicate, timeout=5.0):
        deadline = time.monotonic() + timeout
        while rclpy.ok() and time.monotonic() < deadline:
            rclpy.spin_once(self, timeout_sec=0.05)
            if predicate():
                return
        raise TimeoutError('等待反馈超时')

    def require_start(self):
        self.wait(lambda: self.status is not None and self.joints is not None)
        allowed = ('mode: READY, state: READY', 'mode: IDLE_MODE, state: STAND')
        if self.status not in allowed:
            raise RuntimeError(f'请先准备到 READY 或 IDLE_MODE/STAND；当前 {self.status}')

    def switch(self, name, enable):
        return self.call_service(SetBool, name, SetBool.Request(data=enable))

    def walk_ready(self):
        self.require_start()
        self.call_service(SetRobotMode, '/set_robot_mode', SetRobotMode.Request(mode_name='WALK'))
        self.status = None
        self.wait(lambda: self.status == 'mode: IDLE_MODE, state: STAND')

    def state(self):
        return self.call_service(GetRobotState, '/get_robot_state_srv_hl',
                                 GetRobotState.Request(start=True)).state

    def pose(self):
        count = self.joint_count
        self.wait(lambda: self.joint_count > count)
        msg = self.joints
        if not msg.name or len(msg.name) != len(msg.position):
            raise RuntimeError('关节反馈为空或数组长度不匹配')
        return dict(zip(msg.name, msg.position))

    def send_pose(self, pub, msg, positions, seconds=2.0):
        msg.name = list(positions)
        msg.position = list(positions.values())
        msg.velocity = [0.0] * len(positions)
        msg.effort = [0.0] * len(positions)
        self.publish_once(pub, msg)
        deadline = time.monotonic() + seconds
        while rclpy.ok() and time.monotonic() < deadline:
            msg.header.stamp = self.get_clock().now().to_msg()
            pub.publish(msg)
            rclpy.spin_once(self, timeout_sec=0.02)


def run_workflow(callback):
    rclpy.init()
    node = WorkflowNode()
    try:
        callback(node)
        print('PASS: 请求与反馈检查通过；运动质量仍需现场验收')
        return 0
    except (RuntimeError, ValueError, TimeoutError) as exc:
        print(f'FAIL: {exc}')
        return 1
    except KeyboardInterrupt:
        return 130
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
