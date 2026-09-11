"""T01: Query actual RobotState and receive status without changing modes."""
from casbot2_tools.contracts import STATE_NAMES
from casbot2_py_tests.workflow_support import run_workflow


def get_state(node):
    state = node.state()
    if state not in STATE_NAMES:
        raise RuntimeError(f'未知状态: {state}')
    print(f'GetRobotState: {state} ({STATE_NAMES[state]})')
    node.wait(lambda: node.status is not None)
    print(node.status)


def main():
    return run_workflow(get_state)


if __name__ == '__main__':
    raise SystemExit(main())
