"""T04: Publish bounded navigation velocity; NAVIGATION must already be active."""
from casbot2_py_tests.workflow_support import run_workflow


def cmd_vel(node):
    node.wait(lambda: node.status is not None)
    if not node.status.startswith('mode: NAVIGATION,'):
        raise RuntimeError(f'需要 NAVIGATION，当前 {node.status}')
    node.cmd_pub_cmd_vel(0.2, 0.0, 2.0, 20.0)


def main():
    return run_workflow(cmd_vel)


if __name__ == '__main__':
    raise SystemExit(main())
