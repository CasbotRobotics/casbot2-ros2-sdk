#!/usr/bin/env python3
import argparse
import json
import math
import sys

from action_msgs.msg import GoalStatus
from casbot2_tools.contracts import TOPICS, SERVICES, validate_joint_arrays
import time

import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node

from geometry_msgs.msg import Twist
from sensor_msgs.msg import JointState, Imu
from std_msgs.msg import String
from std_srvs.srv import SetBool

from crb_ros_msg.action import BasicActionPlay
from crb_ros_msg.msg import UpperJointData, JointStateData
from crb_ros_msg.srv import (
    ActionEvent,
    GetRobotMode,
    GetRobotState,
    SetRobotMode,
    Voice,
)

try:
    from crb_ros_msg.action import VoicePlay
except ImportError:
    VoicePlay = None


def parse_bool(v: str) -> bool:
    value = str(v).lower()
    if value in ('1', 'true', 'yes', 'y', 'on'):
        return True
    if value in ('0', 'false', 'no', 'n', 'off'):
        return False
    raise argparse.ArgumentTypeError('布尔值必须是 true 或 false')


def parse_csv_str(s: str):
    return [x.strip() for x in s.split(",") if x.strip()]


def parse_csv_float(s: str):
    return [float(x.strip()) for x in s.split(",") if x.strip()]


class InterfaceDemo(Node):
    def __init__(self):
        super().__init__("casbot2_interface_cli")

    def call_service(self, srv_type, name, req, timeout=5.0):
        cli = self.create_client(srv_type, name)
        try:
            if not cli.wait_for_service(timeout_sec=timeout):
                raise RuntimeError(f'服务不可用: {name}')
            future = cli.call_async(req)
            rclpy.spin_until_future_complete(self, future, timeout_sec=timeout)
            if not future.done():
                future.cancel()
                raise TimeoutError(f'服务响应超时，执行状态未知: {name}')
            response = future.result()
            if response is None:
                raise RuntimeError(f'服务没有响应: {name}')
            if hasattr(response, 'success') and not response.success:
                raise RuntimeError(f'{name} 请求失败: {response}')
            if hasattr(response, 'error_code') and response.error_code != 0:
                raise RuntimeError(f'{name}: error_code={response.error_code}, {response.msg}')
            return response
        finally:
            self.destroy_client(cli)

    def publish_once(self, pub, msg, timeout=3.0):
        deadline = time.monotonic() + timeout
        while rclpy.ok() and pub.get_subscription_count() == 0:
            if time.monotonic() >= deadline:
                raise TimeoutError(f'没有匹配的订阅者: {pub.topic_name}')
            rclpy.spin_once(self, timeout_sec=0.05)
        pub.publish(msg)
        # Allow the middleware to send before destroying the node.
        rclpy.spin_once(self, timeout_sec=0.1)

    def cmd_doctor(self, seconds):
        deadline = time.monotonic() + seconds
        while rclpy.ok() and time.monotonic() < deadline:
            rclpy.spin_once(self, timeout_sec=0.1)
        topics = dict(self.get_topic_names_and_types())
        services = dict(self.get_service_names_and_types())
        failed = False
        for label, actual, expected in [('Topic', topics, TOPICS), ('Service', services, SERVICES)]:
            for name, type_name in expected.items():
                types = actual.get(name, [])
                # Topics created by a subscriber can appear even with no publisher.
                if not types:
                    print(f'MISSING {label} {name}: expected {type_name}')
                    failed = True
                elif set(types) != {type_name}:
                    print(f'MISMATCH {label} {name}: {types}, expected {type_name}')
                    failed = True
                else:
                    print(f'OK {label} {name}: {type_name}')
        if failed:
            raise RuntimeError('接口图与核对基准不一致；检查运行版本、namespace 和 remapping')
        print('类型匹配；该检查不证明状态反馈、运动效果或动作资源可用')

    def cmd_get_robot_mode(self):
        resp = self.call_service(GetRobotMode, "get_robot_mode", GetRobotMode.Request())
        if resp:
            print(f"mode={resp.mode}, mode_name={resp.mode_name}")

    def cmd_set_robot_mode(self, mode: str):
        req = SetRobotMode.Request()
        req.mode_name = mode
        resp = self.call_service(SetRobotMode, "/set_robot_mode", req)
        if resp:
            print(f"success={resp.success}")

    def cmd_get_robot_state(self):
        req = GetRobotState.Request()
        req.start = True
        resp = self.call_service(GetRobotState, "get_robot_state_srv_hl", req)
        if resp:
            print(f"state={resp.state}")

    def cmd_switch_bool(self, srv_name: str, enable: bool):
        req = SetBool.Request()
        req.data = enable
        resp = self.call_service(SetBool, srv_name, req)
        if resp:
            print(f"{srv_name}: success={resp.success}, message={resp.message}")

    def cmd_pub_cmd_vel(self, vx, wz, seconds, hz, topic='/navigation/cmd_vel'):
        pub = self.create_publisher(Twist, topic, 10)
        msg = Twist()
        msg.linear.x = vx
        msg.angular.z = wz
        try:
            self.publish_once(pub, msg)
            end = time.monotonic() + seconds
            while time.monotonic() < end and rclpy.ok():
                pub.publish(msg)
                rclpy.spin_once(self, timeout_sec=0.0)
                time.sleep(1.0 / hz)
        finally:
            if rclpy.ok():
                for _ in range(3):
                    pub.publish(Twist())
                    rclpy.spin_once(self, timeout_sec=0.05)
        print('速度指令已发送，并发送了零速度；请从反馈确认停止')

    def cmd_pub_upper(self, names, positions, vel_scale=0.05, kp=None, kd=None):
        validate_joint_arrays(names, positions, kp or [], kd or [])
        pub = self.create_publisher(UpperJointData, "/upper_body_debug/joint_cmd", 10)
        msg = UpperJointData()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.time_ref = 0.0
        msg.vel_scale = float(vel_scale)
        msg.name = names
        msg.position = positions
        msg.velocity = [0.0] * len(names)
        msg.effort = [0.0] * len(names)
        msg.kp = kp or []
        msg.kd = kd or []
        self.publish_once(pub, msg)
        print("upper joint cmd 已发送")

    def cmd_pub_whole(self, names, positions, kp=None, kd=None):
        validate_joint_arrays(names, positions, kp or [], kd or [])
        # Preserve the rest of the measured pose rather than generating partial
        # upper-body arrays in the runtime dispatcher.
        snapshot = []
        sub = self.create_subscription(JointState, '/joint_states', snapshot.append, 10)
        try:
            deadline = time.monotonic() + 3.0
            while not snapshot and time.monotonic() < deadline:
                rclpy.spin_once(self, timeout_sec=0.05)
            if not snapshot:
                raise TimeoutError('缺少 /joint_states，不能补全全身姿态')
            measured = snapshot[-1]
            if not measured.name or len(measured.name) != len(measured.position):
                raise ValueError('实测关节数组为空或长度不匹配')
            pose = dict(zip(measured.name, measured.position))
            if not set(names) <= set(pose):
                raise ValueError('命令包含当前反馈中不存在的关节')
            if kp or kd:
                if set(names) != set(pose):
                    raise ValueError('显式 PD 全身命令须提供反馈中的完整 name/position 及紧凑 kp/kd')
            else:
                pose.update(zip(names, positions))
                names, positions = list(pose), list(pose.values())
            validate_joint_arrays(names, positions, kp or [], kd or [])
        finally:
            self.destroy_subscription(sub)
        pub = self.create_publisher(JointStateData, "/motion/debug/joint_cmd", 10)
        msg = JointStateData()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = names
        msg.position = positions
        msg.velocity = [0.0] * len(names)
        msg.effort = [0.0] * len(names)
        msg.kp = kp if kp else []
        msg.kd = kd if kd else []
        self.publish_once(pub, msg)
        print("whole joint cmd 已发送")

    def cmd_sub_topic(self, msg_type, topic: str, seconds: float):
        count = {"n": 0}

        def cb(_msg):
            count["n"] += 1

        self.create_subscription(msg_type, topic, cb, 10)
        end = time.time() + seconds
        while time.time() < end and rclpy.ok():
            rclpy.spin_once(self, timeout_sec=0.1)
        print(f"{topic} 收到消息: {count['n']} 条")
        if count['n'] == 0:
            raise TimeoutError(f'{topic} 没有收到反馈；检查模式、类型和 QoS')

    def cmd_sub_status(self, seconds: float):
        status = {"motion_status": 0, "robot_state": 0}
        self.create_subscription(String, "/motion/status", lambda _m: status.__setitem__("motion_status", status["motion_status"] + 1), 10)
        self.create_subscription(String, "/motion/robot_state", lambda _m: status.__setitem__("robot_state", status["robot_state"] + 1), 10)
        end = time.time() + seconds
        while time.time() < end and rclpy.ok():
            rclpy.spin_once(self, timeout_sec=0.1)
        print(f"/motion/status={status['motion_status']}, /motion/robot_state={status['robot_state']}")

    def run_action(self, action_type, name, goal, timeout=30.0):
        client = ActionClient(self, action_type, name)
        try:
            if not client.wait_for_server(timeout_sec=5.0):
                raise RuntimeError(f'Action 不可用: {name}')
            future = client.send_goal_async(goal)
            rclpy.spin_until_future_complete(self, future, timeout_sec=5.0)
            if not future.done():
                raise TimeoutError(f'{name} 目标响应超时，接受状态未知')
            handle = future.result()
            if handle is None or not handle.accepted:
                raise RuntimeError(f'{name} 目标被拒绝')
            future = handle.get_result_async()
            try:
                rclpy.spin_until_future_complete(self, future, timeout_sec=timeout)
                if not future.done():
                    raise TimeoutError(f'{name} 等待结果超时')
            except (TimeoutError, KeyboardInterrupt):
                cancel = handle.cancel_goal_async()
                rclpy.spin_until_future_complete(self, cancel, timeout_sec=3.0)
                raise
            wrapped = future.result()
            if wrapped.status != GoalStatus.STATUS_SUCCEEDED:
                raise RuntimeError(f'{name}: status={wrapped.status}')
            if hasattr(wrapped.result, 'if_success') and not wrapped.result.if_success:
                raise RuntimeError(f'{name}: if_success=false（模式、资源或起始姿态不满足）')
            print(f'{name}: {wrapped.result}')
            return wrapped.result
        finally:
            client.destroy()

    def cmd_basic_action_play(self, action_type):
        goal = BasicActionPlay.Goal()
        goal.type = action_type
        return self.run_action(BasicActionPlay, '/basic_action_play', goal)

    def cmd_voice_service(self, t: str, content_type: str, content: str):
        req = Voice.Request()
        req.type = t
        req.content_type = content_type
        req.content = content
        resp = self.call_service(Voice, "/voice_svr", req)
        if resp:
            print(f"voice_svr success={resp.success}, msg={resp.msg}")

    def cmd_voice_play(self, wav):
        if VoicePlay is None:
            raise RuntimeError('当前 crb_ros_msg 未提供 VoicePlay')
        goal = VoicePlay.Goal()
        goal.wav_path = wav
        return self.run_action(VoicePlay, '/action_voice_play', goal)

    def cmd_event_skill(self, action_type: str, blocking: bool):
        req = ActionEvent.Request()
        req.event_id = ""
        req.event_type = "ExecSkill"
        req.blocking = blocking
        req.param_json = json.dumps(
            {
                "payload": json.dumps({"action_type": action_type}),
                "target_tree": "basic_action_play",
            }
        )
        resp = self.call_service(ActionEvent, "/casbot/event_service", req)
        if resp:
            print(f"event_service error_code={resp.error_code}, msg={resp.msg}")


def build_parser():
    p = argparse.ArgumentParser(description="CASBOT2 全接口示例工具")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser('doctor', help='只读检查运控图中的话题和服务类型')
    s.add_argument('--seconds', type=float, default=3.0)
    s = sub.add_parser('nav_upper_body_debug')
    s.add_argument('--enable', type=parse_bool, required=True)
    sub.add_parser("get_robot_mode")
    s = sub.add_parser("set_robot_mode")
    s.add_argument("--mode", required=True, choices=["ZERO", "STAND", "WALK"])
    sub.add_parser("get_robot_state")

    s = sub.add_parser("switch_nav_mode")
    s.add_argument("--enable", type=parse_bool, required=True)
    s = sub.add_parser("switch_teleoperation")
    s.add_argument("--enable", type=parse_bool, required=True)
    s = sub.add_parser("switch_autonomous")
    s.add_argument("--enable", type=parse_bool, required=True)
    s = sub.add_parser("upper_body_debug")
    s.add_argument("--enable", type=parse_bool, required=True)
    s = sub.add_parser("whole_body_debug")
    s.add_argument("--enable", type=parse_bool, required=True)

    s = sub.add_parser("pub_cmd_vel")
    s.add_argument("--topic", choices=["/navigation/cmd_vel", "/upper_body_debug/cmd_vel"], default="/navigation/cmd_vel")
    s.add_argument("--vx", type=float, default=0.2)
    s.add_argument("--wz", type=float, default=0.0)
    s.add_argument("--seconds", type=float, default=2.0)
    s.add_argument("--hz", type=float, default=10.0)

    s = sub.add_parser("pub_upper_cmd")
    s.add_argument("--names", required=True)
    s.add_argument("--positions", required=True)
    s.add_argument("--vel-scale", type=float, default=0.05)
    s.add_argument("--kp", default="")
    s.add_argument("--kd", default="")

    s = sub.add_parser("pub_whole_cmd")
    s.add_argument("--names", required=True)
    s.add_argument("--positions", required=True)
    s.add_argument("--kp", default="")
    s.add_argument("--kd", default="")

    s = sub.add_parser("sub_motion_debug_joint_state")
    s.add_argument("--seconds", type=float, default=3.0)
    s = sub.add_parser("sub_motion_joint_state")
    s.add_argument("--seconds", type=float, default=3.0)
    s = sub.add_parser("sub_joint_states")
    s.add_argument("--seconds", type=float, default=3.0)
    s = sub.add_parser("sub_joint_control")
    s.add_argument("--seconds", type=float, default=3.0)
    s = sub.add_parser("sub_status")
    s.add_argument("--seconds", type=float, default=3.0)
    s = sub.add_parser("sub_imu")
    s.add_argument("--topic", default="/imu")
    s.add_argument("--seconds", type=float, default=3.0)

    s = sub.add_parser("basic_action_play")
    s.add_argument("--type", default="wave_hand")

    s = sub.add_parser("voice_service")
    s.add_argument("--type", required=True)
    s.add_argument("--content-type", default="")
    s.add_argument("--content", default="")

    s = sub.add_parser("voice_play")
    s.add_argument("--wav", required=True)

    s = sub.add_parser("event_skill")
    s.add_argument("--action-type", default="wave_hand")
    s.add_argument("--blocking", type=parse_bool, default=False)
    return p


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.cmd == "voice_play" and VoicePlay is None:
        parser.error("当前 crb_ros_msg 未提供 VoicePlay，请加载配套的兼容接口包")

    try:
        for key in ('vx', 'wz', 'seconds', 'hz', 'vel_scale'):
            value = getattr(args, key, None)
            if value is not None and not math.isfinite(value):
                raise ValueError(f'{key} 必须是有限数值')
            if key in ('seconds', 'hz') and value is not None and value <= 0:
                raise ValueError(f'{key} 必须大于零')
        if hasattr(args, 'vel_scale') and not 0 < args.vel_scale <= 1:
            raise ValueError('vel-scale 必须在 (0, 1]')
        if args.cmd in ('pub_upper_cmd', 'pub_whole_cmd'):
            validate_joint_arrays(parse_csv_str(args.names), parse_csv_float(args.positions),
                                  parse_csv_float(args.kp), parse_csv_float(args.kd))
    except ValueError as exc:
        parser.error(str(exc))

    rclpy.init()
    node = InterfaceDemo()
    try:
        if args.cmd == "doctor":
            node.cmd_doctor(args.seconds)
        elif args.cmd == "nav_upper_body_debug":
            node.cmd_switch_bool("/motion/nav_upper_body_debug", args.enable)
        elif args.cmd == "get_robot_mode":
            node.cmd_get_robot_mode()
        elif args.cmd == "set_robot_mode":
            node.cmd_set_robot_mode(args.mode)
        elif args.cmd == "get_robot_state":
            node.cmd_get_robot_state()
        elif args.cmd == "switch_nav_mode":
            node.cmd_switch_bool("/motion/switch_nav_mode", args.enable)
        elif args.cmd == "switch_teleoperation":
            node.cmd_switch_bool("/switch_teleoperation", args.enable)
        elif args.cmd == "switch_autonomous":
            node.cmd_switch_bool("/switch_autonomous", args.enable)
        elif args.cmd == "upper_body_debug":
            node.cmd_switch_bool("/motion/upper_body_debug", args.enable)
        elif args.cmd == "whole_body_debug":
            node.cmd_switch_bool("/motion/whole_body_debug", args.enable)
        elif args.cmd == "pub_cmd_vel":
            node.cmd_pub_cmd_vel(args.vx, args.wz, args.seconds, args.hz, args.topic)
        elif args.cmd == "pub_upper_cmd":
            node.cmd_pub_upper(parse_csv_str(args.names), parse_csv_float(args.positions), args.vel_scale, parse_csv_float(args.kp), parse_csv_float(args.kd))
        elif args.cmd == "pub_whole_cmd":
            kp = parse_csv_float(args.kp) if args.kp else []
            kd = parse_csv_float(args.kd) if args.kd else []
            node.cmd_pub_whole(parse_csv_str(args.names), parse_csv_float(args.positions), kp, kd)
        elif args.cmd == "sub_motion_joint_state":
            node.cmd_sub_topic(JointState, "/motion/joint_state", args.seconds)
        elif args.cmd == "sub_motion_debug_joint_state":
            node.cmd_sub_topic(JointStateData, "/motion/debug/joint_state", args.seconds)
        elif args.cmd == "sub_joint_states":
            node.cmd_sub_topic(JointState, "/joint_states", args.seconds)
        elif args.cmd == "sub_joint_control":
            node.cmd_sub_topic(JointState, "/joint_control", args.seconds)
        elif args.cmd == "sub_status":
            node.cmd_sub_status(args.seconds)
        elif args.cmd == "sub_imu":
            node.cmd_sub_topic(Imu, args.topic, args.seconds)
        elif args.cmd == "basic_action_play":
            node.cmd_basic_action_play(args.type)
        elif args.cmd == "voice_service":
            node.cmd_voice_service(args.type, args.content_type, args.content)
        elif args.cmd == "voice_play":
            node.cmd_voice_play(args.wav)
        elif args.cmd == "event_skill":
            node.cmd_event_skill(args.action_type, args.blocking)
    except (RuntimeError, TimeoutError, ValueError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 130
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    sys.exit(main())
