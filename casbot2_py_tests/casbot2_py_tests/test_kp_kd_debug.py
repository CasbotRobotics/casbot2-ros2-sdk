"""Read back applied PD gains; runtime configuration is managed outside the SDK."""
import argparse
from crb_ros_msg.msg import JointStateData
from casbot2_tools.contracts import pd_by_name
from casbot2_py_tests.workflow_support import run_workflow


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--joint', default='head_pitch_joint')
    parser.add_argument('--expected-kp', type=float)
    parser.add_argument('--expected-kd', type=float)
    args = parser.parse_args()
    if (args.expected_kp is None) != (args.expected_kd is None):
        parser.error('expected-kp 和 expected-kd 必须成对提供')

    def check(node):
        received = []
        node.create_subscription(JointStateData, '/motion/debug/joint_state', received.append, 10)
        node.wait(lambda: bool(received), timeout=10.0)
        gains = pd_by_name(received[-1])
        if args.joint not in gains:
            raise RuntimeError(f'反馈中没有 {args.joint} 的增益')
        kp, kd = gains[args.joint]
        print(f'{args.joint}: kp={kp}, kd={kd}')
        if args.expected_kp is not None:
            if abs(kp - args.expected_kp) > 1e-6 or abs(kd - args.expected_kd) > 1e-6:
                raise RuntimeError('当前生效增益与期望值不符')
    return run_workflow(check)


if __name__ == '__main__':
    raise SystemExit(main())
