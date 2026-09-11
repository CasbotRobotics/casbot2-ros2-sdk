"""Check example contracts against built ROS types without starting ROS nodes.

Run after sourcing ROS 2 and this SDK's install/setup.bash:
    python3 -m unittest discover -s casbot2_py_tests/test -v
"""

from contextlib import redirect_stdout
import importlib.util
from importlib import metadata
import io
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace
import unittest

from crb_ros_msg.srv import ActionEvent, Voice


ROOT = Path(__file__).resolve().parents[2]
CLI = ROOT / 'casbot2_tools/casbot2_tools/interface_cli.py'


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


interface_demo = load_module('interface_demo', CLI)


class ExampleContracts(unittest.TestCase):
    def test_installed_python_entry_points(self):
        expected = {
            'casbot2_tools': {'interface_cli'},
            'casbot2_py_demo': {
                'basic_control_demo', 'service_mode_demo', 'debug_joint_demo',
                'monitor_topics_demo', 'action_voice_demo',
            },
            'casbot2_py_tests': {
                'get_state_test', 'switch_mode_test', 'joint_states_test',
                'cmd_vel_test', 'upper_body_debug_test', 'test_walk_flow',
                'test_upper_body_flow', 'test_whole_body_flow',
                'test_sensors_and_actions_flow', 'test_kp_kd_debug',
                'test_kp_kd_joint_states', 'test_action_play_flow',
            },
        }
        for package, names in expected.items():
            with self.subTest(package=package):
                entries = [ep for ep in metadata.distribution(package).entry_points
                           if ep.group == 'console_scripts']
                self.assertEqual({ep.name for ep in entries}, names)
                # Import entry functions without invoking workflows or creating ROS nodes.
                for entry in entries:
                    self.assertTrue(callable(entry.load()), entry.name)

    def test_installed_cli_entry(self):
        result = subprocess.run(
            ['ros2', 'run', 'casbot2_tools', 'interface_cli', '--help'],
            capture_output=True, text=True, timeout=10,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('get_robot_mode', result.stdout)

    def test_cli_help_without_robot(self):
        result = subprocess.run(
            [sys.executable, str(CLI), '--help'], capture_output=True, text=True, timeout=10
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('get_robot_mode', result.stdout)
        self.assertIn('voice_play', result.stdout)

    @unittest.skipIf(interface_demo.VoicePlay is not None, 'Optional VoicePlay is installed')
    def test_missing_audio_action_reports_error_before_node_creation(self):
        result = subprocess.run(
            [sys.executable, str(CLI), 'voice_play', '--wav', 'test.wav'],
            capture_output=True, text=True, timeout=10,
        )
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn('未提供 VoicePlay', result.stderr)
        self.assertNotIn('Traceback', result.stderr)

    def test_action_demo_imports_with_current_interfaces(self):
        module = load_module(
            'action_voice_demo',
            ROOT / 'casbot2_py_demo/casbot2_py_demo/action_voice_demo.py',
        )
        self.assertTrue(callable(module.main))

    def test_voice_response_uses_generated_fields(self):
        def call_service(srv_type, name, request):
            self.assertIs(srv_type, Voice)
            self.assertEqual(name, '/voice_svr')
            self.assertIsInstance(request, Voice.Request)
            self.assertEqual(request.content, '你好')
            return Voice.Response(success=True, msg='ok')

        output = io.StringIO()
        with redirect_stdout(output):
            interface_demo.InterfaceDemo.cmd_voice_service(
                SimpleNamespace(call_service=call_service), 'question', 'text', '你好'
            )
        self.assertIn('success=True, msg=ok', output.getvalue())

    def test_event_response_uses_generated_fields_on_success_and_error(self):
        for error_code in (0, 7):
            with self.subTest(error_code=error_code):
                def call_service(srv_type, name, request):
                    self.assertIs(srv_type, ActionEvent)
                    self.assertEqual(name, '/casbot/event_service')
                    self.assertIsInstance(request, ActionEvent.Request)
                    self.assertEqual(request.event_type, 'ExecSkill')
                    return ActionEvent.Response(error_code=error_code, msg='event response')

                output = io.StringIO()
                with redirect_stdout(output):
                    interface_demo.InterfaceDemo.cmd_event_skill(
                        SimpleNamespace(call_service=call_service), 'wave_hand', False
                    )
                self.assertIn(f'error_code={error_code}, msg=event response', output.getvalue())


if __name__ == '__main__':
    unittest.main()
