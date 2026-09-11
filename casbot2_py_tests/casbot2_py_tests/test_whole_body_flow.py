"""Whole-body position test using a full measured pose and default runtime PD.

Requires debug_mode_params.use_default_kp_kd=true. Only head_yaw is changed;
other joints are held at their measured starting positions.
"""
from crb_ros_msg.msg import JointStateData
from casbot2_py_tests.workflow_support import run_workflow


def whole_body(node):
    node.require_start()
    initial = node.pose()
    if 'head_yaw_joint' not in initial:
        raise RuntimeError('反馈缺少 head_yaw_joint')
    target = dict(initial)
    target['head_yaw_joint'] += 0.05
    pub = node.create_publisher(JointStateData, '/motion/debug/joint_cmd', 10)
    node.switch('/motion/whole_body_debug', True)
    try:
        node.send_pose(pub, JointStateData(), target)
        actual = node.pose()['head_yaw_joint']
        if abs(actual - target['head_yaw_joint']) > 0.03:
            raise RuntimeError(f'头部反馈未到达目标: {actual}')
    finally:
        if node.context.ok():
            node.send_pose(pub, JointStateData(), initial)
            node.switch('/motion/whole_body_debug', False)


def main():
    return run_workflow(whole_body)


if __name__ == '__main__':
    raise SystemExit(main())
