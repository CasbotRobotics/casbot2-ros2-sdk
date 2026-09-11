"""Regression checks for runtime contracts, without DDS or robot commands."""
import ast
from concurrent.futures import Future
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from action_msgs.msg import GoalStatus
from crb_ros_msg.msg import JointStateData
from crb_ros_msg.srv import SetRobotMode
from casbot2_tools.contracts import TOPICS, SERVICES, pd_by_name, validate_joint_arrays
from casbot2_tools import interface_cli as cli

ROOT = Path(__file__).resolve().parents[3]


def ready(value):
    future = Future()
    future.set_result(value)
    return future


class RuntimeContracts(unittest.TestCase):
    def test_message_definitions_match_audited_baseline(self):
        baseline = json.loads((ROOT / 'runtime-contract.json').read_text())
        for name, digest in baseline['interfaces'].items():
            with self.subTest(interface=name):
                self.assertEqual(hashlib.sha256((ROOT / 'crb_ros_msg' / name).read_bytes()).hexdigest(), digest)

    def test_literal_python_endpoint_types(self):
        # Inspect actual constructors without importing/running hardware workflows.
        expected = {**TOPICS, **SERVICES}
        found = 0
        for directory in ('casbot2_py_demo', 'casbot2_py_tests/casbot2_py_tests', 'casbot2_tools'):
            for path in (ROOT / 'examples' / directory).rglob('*.py'):
                if '/test/' in str(path):
                    continue
                for call in ast.walk(ast.parse(path.read_text())):
                    if not isinstance(call, ast.Call) or not isinstance(call.func, ast.Attribute):
                        continue
                    if call.func.attr not in ('create_publisher', 'create_subscription', 'create_client', 'cmd_sub_topic'):
                        continue
                    if len(call.args) < 2 or not isinstance(call.args[1], ast.Constant):
                        continue
                    topic = call.args[1].value
                    if topic not in expected or not isinstance(call.args[0], ast.Name):
                        continue
                    with self.subTest(path=str(path), endpoint=topic):
                        self.assertEqual(call.args[0].id, expected[topic].split('/')[-1])
                        found += 1
        self.assertGreater(found, 20)

    def test_cpp_endpoint_types(self):
        found = 0
        for folder in ('casbot2_cpp_demo', 'casbot2_cpp_tests'):
            for path in (ROOT / 'examples' / folder).rglob('*.cpp'):
                for kind, cpp_type, topic in re.findall(
                    r'create_(publisher|subscription|client)<([\w:]+)>\(\s*"([^"]+)"', path.read_text()
                ):
                    expected = (SERVICES if kind == 'client' else TOPICS).get(topic)
                    if expected:
                        self.assertEqual(cpp_type.replace('::', '/'), expected, str(path))
                        found += 1
        self.assertGreater(found, 10)

    def test_compact_gains_with_interleaved_hand_joint(self):
        msg = JointStateData(
            name=['head_pitch_joint', 'left_thumb_metacarpal_joint', 'waist_yaw_joint'],
            position=[0.0, 0.0, 0.0], velocity=[0.0]*3, effort=[0.0]*3,
            kp=[30.0, 500.0], kd=[2.0, 5.0])
        self.assertEqual(pd_by_name(msg), {'head_pitch_joint': (30.0, 2.0), 'waist_yaw_joint': (500.0, 5.0)})
        msg.kp = [30.0, 0.0, 500.0]
        msg.kd = [2.0, 0.0, 5.0]
        with self.assertRaises(ValueError):
            pd_by_name(msg)

    def test_reject_nonfinite_duplicate_and_incomplete_gains(self):
        invalid = [(['head_yaw_joint'], [float('nan')], [], []),
                   (['head_yaw_joint']*2, [0.0]*2, [], []),
                   (['head_yaw_joint'], [0.0], [20.0], []),
                   (['head_yaw_joint'], [0.0], [-1.0], [2.0])]
        for values in invalid:
            with self.subTest(values=values), self.assertRaises(ValueError):
                validate_joint_arrays(*values)
        validate_joint_arrays(['head_yaw_joint'], [0.0], [], [])

    def test_bad_cli_arguments_fail_before_node_creation(self):
        for args in [('switch_nav_mode', '--enable', 'flase'),
                     ('pub_cmd_vel', '--hz', 'nan'),
                     ('pub_cmd_vel', '--seconds', '-1'),
                     ('pub_whole_cmd', '--names', 'head_yaw_joint', '--positions', '0', '--kp', '1')]:
            result = subprocess.run([sys.executable, str(ROOT / 'examples/casbot2_tools/casbot2_tools/interface_cli.py'), *args],
                                    capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertNotIn('Traceback', result.stderr)

    def test_rejected_service_raises_and_releases_client(self):
        client = Mock()
        client.wait_for_service.return_value = True
        client.call_async.return_value = ready(SetRobotMode.Response(success=False))
        node = Mock()
        node.create_client.return_value = client
        with patch.object(cli.rclpy, 'spin_until_future_complete'), self.assertRaises(RuntimeError):
            cli.InterfaceDemo.call_service(node, SetRobotMode, '/set_robot_mode', SetRobotMode.Request(mode_name='WALK'))
        node.destroy_client.assert_called_once_with(client)

    def test_service_timeout_is_not_success(self):
        client = Mock()
        client.wait_for_service.return_value = True
        client.call_async.return_value = Future()
        node = Mock()
        node.create_client.return_value = client
        with patch.object(cli.rclpy, 'spin_until_future_complete'), self.assertRaises(TimeoutError):
            cli.InterfaceDemo.call_service(node, SetRobotMode, '/set_robot_mode', SetRobotMode.Request())
        self.assertTrue(client.call_async.return_value.cancelled())

    def test_ros_action_success_with_false_business_result_is_failure(self):
        handle = Mock(accepted=True)
        handle.get_result_async.return_value = ready(SimpleNamespace(
            status=GoalStatus.STATUS_SUCCEEDED, result=SimpleNamespace(if_success=False)))
        client = Mock()
        client.wait_for_server.return_value = True
        client.send_goal_async.return_value = ready(handle)
        with patch.object(cli, 'ActionClient', return_value=client), patch.object(cli.rclpy, 'spin_until_future_complete'):
            with self.assertRaisesRegex(RuntimeError, 'if_success=false'):
                cli.InterfaceDemo.run_action(Mock(), object, '/basic_action_play', object())
        client.destroy.assert_called_once()

    def test_action_timeout_requests_cancellation(self):
        handle = Mock(accepted=True)
        handle.get_result_async.return_value = Future()
        handle.cancel_goal_async.return_value = ready(None)
        client = Mock()
        client.wait_for_server.return_value = True
        client.send_goal_async.return_value = ready(handle)
        with patch.object(cli, 'ActionClient', return_value=client), patch.object(cli.rclpy, 'spin_until_future_complete'):
            with self.assertRaises(TimeoutError):
                cli.InterfaceDemo.run_action(Mock(), object, '/basic_action_play', object())
        handle.cancel_goal_async.assert_called_once()
