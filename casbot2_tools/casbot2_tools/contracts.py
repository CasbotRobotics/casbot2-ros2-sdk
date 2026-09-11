"""Public client contracts verified against hl_motion main c3b2902 (2026-09-07)."""

import math


TOPICS = {
    '/joint_states': 'sensor_msgs/msg/JointState',
    '/joint_control': 'sensor_msgs/msg/JointState',
    '/motion/joint_cmd': 'sensor_msgs/msg/JointState',
    '/motion/joint_state': 'sensor_msgs/msg/JointState',
    '/motion/debug/joint_cmd': 'crb_ros_msg/msg/JointStateData',
    '/motion/debug/joint_state': 'crb_ros_msg/msg/JointStateData',
    '/upper_body_debug/joint_cmd': 'crb_ros_msg/msg/UpperJointData',
    '/upper_body_debug/cmd_vel': 'geometry_msgs/msg/Twist',
    '/navigation/cmd_vel': 'geometry_msgs/msg/Twist',
    '/motion/status': 'std_msgs/msg/String',
    '/motion/robot_state': 'std_msgs/msg/String',
    '/motion/imu': 'sensor_msgs/msg/Imu',
    '/motion/current_mode': 'std_msgs/msg/Int32',
    '/motion/cmd_vel': 'geometry_msgs/msg/Twist',
}

SERVICES = {
    '/get_robot_mode': 'crb_ros_msg/srv/GetRobotMode',
    '/set_robot_mode': 'crb_ros_msg/srv/SetRobotMode',
    '/get_robot_state_srv_hl': 'crb_ros_msg/srv/GetRobotState',
    **{name: 'std_srvs/srv/SetBool' for name in (
        '/motion/switch_nav_mode', '/motion/nav_upper_body_debug',
        '/motion/upper_body_debug', '/motion/whole_body_debug',
        '/switch_teleoperation', '/switch_autonomous',
    )},
}

STATE_NAMES = {
    0: 'UNDEFINED', 1: 'DAMPING', 2: 'READY', 3: 'STAND',
    4: 'WALKING', 5: 'RUNNING', 255: 'EMERGENCY_STOP',
}


def is_hand_joint(name):
    return name.startswith(('left_', 'right_')) and any(
        f'_{finger}_' in name for finger in ('thumb', 'index', 'middle', 'ring', 'pinky')
    )


def validate_joint_arrays(names, positions, kp=(), kd=()):
    """Use compact PD arrays: walk name order, skipping dexterous hand joints.

    Empty PD arrays require runtime use_default_kp_kd=true. This function cannot
    infer runtime configuration or robot joint limits.
    """
    if not names or len(set(names)) != len(names) or len(names) != len(positions):
        raise ValueError('names 必须非空且无重复，并与 positions 等长')
    if any(not name or not name.endswith('_joint') for name in names):
        raise ValueError('使用 /joint_states 中的完整关节名（_joint 后缀）')
    if not all(math.isfinite(v) for v in (*positions, *kp, *kd)):
        raise ValueError('关节位置和增益必须是有限数值')
    count = sum(not is_hand_joint(name) for name in names)
    if kp or kd:
        if len(kp) != count or len(kd) != count:
            raise ValueError('kp/kd 必须成对提供，长度为非灵巧手关节数')
        if any(v < 0 for v in (*kp, *kd)):
            raise ValueError('kp/kd 不能为负数')


def pd_by_name(msg):
    """Decode compact /motion/debug/joint_state gains without hand placeholders."""
    names = [name for name in msg.name if not is_hand_joint(name)]
    if not names or len(msg.kp) != len(names) or len(msg.kd) != len(names):
        raise ValueError('反馈 kp/kd 长度必须等于非灵巧手关节数')
    validate_joint_arrays(msg.name, msg.position, msg.kp, msg.kd)
    if len(msg.velocity) != len(msg.name) or len(msg.effort) != len(msg.name):
        raise ValueError('反馈 name/position/velocity/effort 长度不一致')
    return {name: (kp, kd) for name, kp, kd in zip(names, msg.kp, msg.kd)}
