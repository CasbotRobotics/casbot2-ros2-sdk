"""READY/IDLE_MODE → WALK → NAVIGATION → velocity → zero → IDLE_MODE.

No automatic ZERO reset: damping is not a generic recovery/stop command.
"""
from casbot2_py_tests.workflow_support import run_workflow


def walk(node):
    node.walk_ready()
    node.switch('/motion/switch_nav_mode', True)
    try:
        node.status = None
        node.wait(lambda: node.status is not None and 'mode: NAVIGATION,' in node.status)
        before = node.joint_count
        node.cmd_pub_cmd_vel(0.2, 0.0, 2.0, 20.0)
        node.wait(lambda: node.joint_count > before)
        # GetRobotMode reports WALK for many modes; use actual RobotState here.
        node.wait(lambda: node.state() == 3)
    finally:
        if node.context.ok():
            node.switch('/motion/switch_nav_mode', False)


def main():
    return run_workflow(walk)


if __name__ == '__main__':
    raise SystemExit(main())
