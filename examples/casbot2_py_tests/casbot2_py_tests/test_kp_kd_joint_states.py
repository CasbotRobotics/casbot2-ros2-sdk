"""Read compact PD feedback in WHOLE_BODY_DEBUG; never switch mode automatically."""
from crb_ros_msg.msg import JointStateData
from casbot2_tools.contracts import pd_by_name
from casbot2_py_tests.workflow_support import run_workflow


def check_pd(node):
    received = []
    node.create_subscription(JointStateData, '/motion/debug/joint_state', received.append, 10)
    node.wait(lambda: bool(received), timeout=10.0)
    gains = pd_by_name(received[-1])
    print(f'{len(received[-1].name)} 个位置反馈，{len(gains)} 组非灵巧手 kp/kd')
    # Zero is a valid gain; nonzero is not a universal validity criterion.


def main():
    return run_workflow(check_pd)


if __name__ == '__main__':
    raise SystemExit(main())
