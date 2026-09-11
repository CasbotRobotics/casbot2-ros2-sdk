"""T02: Check each transition, stopping immediately on rejection or timeout."""
from casbot2_py_tests.workflow_support import run_workflow


def switch_modes(node):
    node.require_start()
    for service in ('/switch_teleoperation', '/switch_autonomous'):
        node.switch(service, True)
        node.switch(service, False)


def main():
    return run_workflow(switch_modes)


if __name__ == '__main__':
    raise SystemExit(main())
