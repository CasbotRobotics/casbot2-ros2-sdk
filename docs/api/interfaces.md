<a id="chinese"></a>

中文 | [English](#english)

# 接口全覆盖示例

本文档给出 CASBOT2 常用接口的“可执行示例入口”。
配套脚本：`ros2 run casbot2_tools interface_cli`

`voice_play` 是可选功能，需要配套机器人软件提供 `VoicePlay.action`；本仓库未包含该定义。
缺少时命令会明确报错，其他接口与 `--help` 仍可使用。

## 使用前准备

```bash
source scripts/setup_env.sh
```

如果你在本仓库内开发，建议先编译自定义消息包：

```bash
colcon build --packages-up-to casbot2_tools
source install/setup.bash
```

## 1. 模式与状态类 Service

- `get_robot_mode`
  ```bash
  ros2 run casbot2_tools interface_cli get_robot_mode
  ```
- `/set_robot_mode`（`ZERO`/`STAND`/`WALK`）
  ```bash
  ros2 run casbot2_tools interface_cli set_robot_mode --mode WALK
  ```
- `get_robot_state_srv_hl`
  ```bash
  ros2 run casbot2_tools interface_cli get_robot_state
  ```
- `/motion/switch_nav_mode`
  ```bash
  ros2 run casbot2_tools interface_cli switch_nav_mode --enable true
  ```
- `/switch_teleoperation`
  ```bash
  ros2 run casbot2_tools interface_cli switch_teleoperation --enable true
  ```
- `/switch_autonomous`
  ```bash
  ros2 run casbot2_tools interface_cli switch_autonomous --enable true
  ```
- `/motion/upper_body_debug`
  ```bash
  ros2 run casbot2_tools interface_cli upper_body_debug --enable true
  ```
- `/motion/whole_body_debug`
  ```bash
  ros2 run casbot2_tools interface_cli whole_body_debug --enable true
  ```

## 2. 控制类 Topic

- `/navigation/cmd_vel`
  ```bash
  ros2 run casbot2_tools interface_cli pub_cmd_vel --vx 0.2 --wz 0.0 --seconds 2
  ```
- `/upper_body_debug/joint_cmd` (`UpperJointData`)
  ```bash
  ros2 run casbot2_tools interface_cli pub_upper_cmd \
    --names left_shoulder_pitch_joint,right_shoulder_pitch_joint \
    --positions 0.05,0.05 --vel-scale 0.05
  ```
- `/motion/debug/joint_cmd` (`JointStateData`，可选 `--kp` / `--kd`)
  ```bash
  ros2 run casbot2_tools interface_cli pub_whole_cmd \
    --names head_yaw_joint,head_pitch_joint \
    --positions 0.1,-0.05
  ```

## 3. 订阅类 Topic

- `/motion/debug/joint_state`
  ```bash
  ros2 run casbot2_tools interface_cli sub_motion_debug_joint_state --seconds 3
  ```
- `/joint_states`
  ```bash
  ros2 run casbot2_tools interface_cli sub_joint_states --seconds 3
  ```
- `/joint_control`
  ```bash
  ros2 run casbot2_tools interface_cli sub_joint_control --seconds 3
  ```
- `/motion/status` + `/motion/robot_state`
  ```bash
  ros2 run casbot2_tools interface_cli sub_status --seconds 3
  ```
- `/imu`（或 `/motion/imu`）
  ```bash
  ros2 run casbot2_tools interface_cli sub_imu --topic /imu --seconds 3
  ```

## 4. 动作与应用接口

- `basic_action_play`（`BasicActionPlay`）
  ```bash
  ros2 run casbot2_tools interface_cli basic_action_play --type wave_hand
  ```
- `/voice_svr`（`Voice` Service）
  ```bash
  ros2 run casbot2_tools interface_cli voice_service --type rtc_start
  ros2 run casbot2_tools interface_cli voice_service --type question --content "你好"
  ```
- `/action_voice_play`（`VoicePlay` Action）
  ```bash
  ros2 run casbot2_tools interface_cli voice_play --wav test.wav
  ```
- `/casbot/event_service`（`ActionEvent`）
  ```bash
  ros2 run casbot2_tools interface_cli event_skill --action-type wave_hand
  ```


---

<a id="english"></a>

[中文](#chinese) | English

# Full Interface Coverage Examples

This document lists executable examples for common CASBOT2 interfaces.
Companion script: `ros2 run casbot2_tools interface_cli`

The optional `voice_play` command requires a compatible `VoicePlay.action` from the robot software.
This repository does not include that definition. Other commands and `--help` remain available without it.

## Prerequisites

```bash
source scripts/setup_env.sh
```

If you are developing inside this repository, build the custom interface package first:

```bash
colcon build --packages-up-to casbot2_tools
source install/setup.bash
```

## 1. Mode/State Services

- `get_robot_mode`
  ```bash
  ros2 run casbot2_tools interface_cli get_robot_mode
  ```
- `/set_robot_mode` (`ZERO`/`STAND`/`WALK`)
  ```bash
  ros2 run casbot2_tools interface_cli set_robot_mode --mode WALK
  ```
- `get_robot_state_srv_hl`
  ```bash
  ros2 run casbot2_tools interface_cli get_robot_state
  ```
- `/motion/switch_nav_mode`
  ```bash
  ros2 run casbot2_tools interface_cli switch_nav_mode --enable true
  ```
- `/switch_teleoperation`
  ```bash
  ros2 run casbot2_tools interface_cli switch_teleoperation --enable true
  ```
- `/switch_autonomous`
  ```bash
  ros2 run casbot2_tools interface_cli switch_autonomous --enable true
  ```
- `/motion/upper_body_debug`
  ```bash
  ros2 run casbot2_tools interface_cli upper_body_debug --enable true
  ```
- `/motion/whole_body_debug`
  ```bash
  ros2 run casbot2_tools interface_cli whole_body_debug --enable true
  ```

## 2. Control Topics

- `/navigation/cmd_vel`
  ```bash
  ros2 run casbot2_tools interface_cli pub_cmd_vel --vx 0.2 --wz 0.0 --seconds 2
  ```
- `/upper_body_debug/joint_cmd` (`UpperJointData`)
  ```bash
  ros2 run casbot2_tools interface_cli pub_upper_cmd     --names left_shoulder_pitch_joint,right_shoulder_pitch_joint     --positions 0.05,0.05 --vel-scale 0.05
  ```
- `/motion/debug/joint_cmd` (`JointStateData`, optional `--kp` / `--kd`)
  ```bash
  ros2 run casbot2_tools interface_cli pub_whole_cmd     --names head_yaw_joint,head_pitch_joint     --positions 0.1,-0.05
  ```

## 3. Subscription Topics

- `/motion/debug/joint_state`
  ```bash
  ros2 run casbot2_tools interface_cli sub_motion_debug_joint_state --seconds 3
  ```
- `/joint_states`
  ```bash
  ros2 run casbot2_tools interface_cli sub_joint_states --seconds 3
  ```
- `/joint_control`
  ```bash
  ros2 run casbot2_tools interface_cli sub_joint_control --seconds 3
  ```
- `/motion/status` + `/motion/robot_state`
  ```bash
  ros2 run casbot2_tools interface_cli sub_status --seconds 3
  ```
- `/imu` (or `/motion/imu`)
  ```bash
  ros2 run casbot2_tools interface_cli sub_imu --topic /imu --seconds 3
  ```

## 4. Action / Application Interfaces

- `basic_action_play` (`BasicActionPlay`)
  ```bash
  ros2 run casbot2_tools interface_cli basic_action_play --type wave_hand
  ```
- `/voice_svr` (`Voice` service)
  ```bash
  ros2 run casbot2_tools interface_cli voice_service --type rtc_start
  ros2 run casbot2_tools interface_cli voice_service --type question --content "你好"
  ```
- `/action_voice_play` (`VoicePlay` action)
  ```bash
  ros2 run casbot2_tools interface_cli voice_play --wav test.wav
  ```
- `/casbot/event_service` (`ActionEvent`)
  ```bash
  ros2 run casbot2_tools interface_cli event_skill --action-type wave_hand
  ```

## ROS 2 CLI 速查

!!! warning "控制命令前置模式"
    查询和订阅可作为首次连接检查。设置模式、发布速度、关节命令和播放动作前，必须满足运控指南的模式条件。

| 属性 | 值 |
| --- | --- |
| 查询模式 | `ros2 service call get_robot_mode crb_ros_msg/srv/GetRobotMode '{}'` |
| 查询状态 | `ros2 service call get_robot_state_srv_hl crb_ros_msg/srv/GetRobotState '{start: true}'` |
| 关节反馈 | `ros2 topic echo /motion/debug/joint_state --once` |
| IMU | `ros2 topic echo /imu --once` |
| 查看传感器话题 | `ros2 topic list -t` |
| 预设动作 | `ros2 action send_goal /basic_action_play crb_ros_msg/action/BasicActionPlay '{type: wave_hand}' --feedback` |

## 预设技能

| 技能 | target_tree / action_type |
| --- | --- |
| 点赞 | `basic_action_play` / `thumb_up` |
| 挥手 | `basic_action_play` / `wave_hand` |
| 比心 | `basic_action_play` / `heart_gesture` |
| 恭喜 | `basic_action_play` / `congratulation_gesture` |
| 剪刀手 | `basic_action_play` / `v_gesture` |
| 握手 | `hand_shake` |
| 自我介绍 | `self_introduction` |
| 石头剪刀布 | `rock_paper_scissors` / `rock`、`scissors`、`paper` |

技能资源依赖目标软件版本；数据格式和部署说明见[二次开发手册](../dev-guide/secondary-development.md)。

## 当前 main 补充接口

```bash
# 只读接口图检查
ros2 run casbot2_tools interface_cli doctor
# 标准 JointState 反馈（WHOLE_BODY_DEBUG 内）
ros2 run casbot2_tools interface_cli sub_motion_joint_state --seconds 3
# NAVIGATION 中启用并行上身调试
ros2 run casbot2_tools interface_cli nav_upper_body_debug --enable true
# UPPER_BODY_DEBUG 中发送速度
ros2 run casbot2_tools interface_cli pub_cmd_vel --topic /upper_body_debug/cmd_vel --vx 0.1 --seconds 1
```

`/motion/debug/joint_state` 需 WHOLE_BODY_DEBUG；普通监听使用 `/joint_states`。
所有语音与技能事件接口由外部组件提供，动作名依赖交付资源；详见[运动控制](../dev-guide/motion-control.md)。
