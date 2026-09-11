"""Check core status/telemetry, action completion and navigation transitions."""
from casbot2_tools.contracts import STATE_NAMES
from casbot2_py_tests.workflow_support import run_workflow


def sensors_and_actions(node):
    node.require_start()
    node.cmd_doctor(2.0)
    pose = node.pose()
    state = node.state()
    if state not in STATE_NAMES:
        raise RuntimeError(f'未知机器人状态: {state}')
    print(f'state={state} {STATE_NAMES[state]}, joint_count={len(pose)}')
    node.switch('/switch_autonomous', True)
    try:
        node.cmd_basic_action_play('wave_hand')
    finally:
        node.switch('/switch_autonomous', False)
    node.walk_ready()
    node.switch('/motion/switch_nav_mode', True)
    node.switch('/motion/switch_nav_mode', False)


def main():
    return run_workflow(sensors_and_actions)


if __name__ == '__main__':
    raise SystemExit(main())
