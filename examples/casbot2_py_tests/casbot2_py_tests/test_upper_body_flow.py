"""Small relative upper-body motion, with feedback and return to initial pose."""
from crb_ros_msg.msg import UpperJointData
from casbot2_py_tests.workflow_support import run_workflow


def upper_body(node):
    node.require_start()
    pose = node.pose()
    joint = 'left_shoulder_pitch_joint'
    if joint not in pose:
        raise RuntimeError(f'反馈缺少 {joint}')
    initial = {joint: pose[joint]}
    target = {joint: pose[joint] + 0.05}
    pub = node.create_publisher(UpperJointData, '/upper_body_debug/joint_cmd', 10)
    node.switch('/motion/upper_body_debug', True)
    try:
        node.send_pose(pub, UpperJointData(vel_scale=0.05), target)
        actual = node.pose()[joint]
        if abs(actual - target[joint]) > 0.03:
            raise RuntimeError(f'手臂反馈未到达目标: {actual}')
    finally:
        if node.context.ok():
            node.send_pose(pub, UpperJointData(vel_scale=0.05), initial)
            node.switch('/motion/upper_body_debug', False)


def main():
    return run_workflow(upper_body)


if __name__ == '__main__':
    raise SystemExit(main())
