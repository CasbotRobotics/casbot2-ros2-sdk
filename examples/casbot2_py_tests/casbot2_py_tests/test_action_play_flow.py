"""Check that WHOLE_BODY_DEBUG → ACTION_PLAY is rejected, then play from READY/IDLE.

Requires installed wave_hand.data matching the robot's initial pose.
"""
from std_srvs.srv import SetBool
import rclpy
from casbot2_py_tests.workflow_support import run_workflow


def action_flow(node):
    node.require_start()
    node.switch('/motion/whole_body_debug', True)
    try:
        # A negative transition test must distinguish rejection from timeout.
        cli = node.create_client(SetBool, '/switch_autonomous')
        try:
            if not cli.wait_for_service(timeout_sec=5.0):
                raise RuntimeError('switch_autonomous 不可用')
            future = cli.call_async(SetBool.Request(data=True))
            rclpy.spin_until_future_complete(node, future, timeout_sec=5.0)
            if not future.done() or future.result() is None:
                raise TimeoutError('不能将服务超时认定为拒绝切换')
            if future.result().success:
                raise RuntimeError('当前运行版本允许 WHOLE_BODY_DEBUG → ACTION_PLAY，与基准不一致')
        finally:
            node.destroy_client(cli)
    finally:
        node.switch('/motion/whole_body_debug', False)
    node.switch('/switch_autonomous', True)
    try:
        node.cmd_basic_action_play('wave_hand')
    finally:
        node.switch('/switch_autonomous', False)


def main():
    return run_workflow(action_flow)


if __name__ == '__main__':
    raise SystemExit(main())
