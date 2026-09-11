# 运动控制

本页依据 `hl_motion/main` 提交 `c3b2902ea53f0267ae3ef12b2fdc178c7162ea54`（2026-09-07）核对。
接口定义基准是该提交锁定的 `crb_ros_msg` 子模块 `3228d83f5629727eb2a8440bf9fd46c9f9fcedbf`。
[核对记录](../about/compatibility.md)说明验证范围与尚未完成的实机验收。

## 状态与模式

`/get_robot_state_srv_hl` 使用 `crb_ros_msg/srv/GetRobotState`；`start` 当前未被服务端使用，调用不会启动机器人。

| state | 含义 |
| --- | --- |
| 0 | UNDEFINED |
| 1 | DAMPING |
| 2 | READY |
| 3 | STAND |
| 4 | WALKING |
| 5 | RUNNING |
| 255 | EMERGENCY_STOP |

`/get_robot_mode` 返回的是兼容映射，而非内部模式枚举：

| 内部模式 | mode | mode_name |
| --- | --- | --- |
| UNDEFINED / DAMPING | 2 | ZERO |
| READY | 3 | STAND |
| 其他模式 | 4 | WALK |

因此，查询结果 `WALK` **不能证明进入了导航或调试模式**。应同时读取 `/motion/status`，
其格式为 `mode: NAVIGATION, state: STAND`；`/motion/robot_state` 还包含动作播放器和遥操作状态。
二者为 `std_msgs/msg/String`，当前约 10 Hz 发布。

`/set_robot_mode` 只接受 `ZERO`、`STAND`、`WALK`，分别请求 `DAMPING`、`READY`、`IDLE_MODE`。
接口注释中的 `TREAD` 没有对应实现。`ZERO` 会进入阻尼，不能当成通用停止或自动恢复步骤。

```bash
ros2 run casbot2_tools interface_cli get_robot_state
ros2 run casbot2_tools interface_cli get_robot_mode
ros2 topic echo /motion/status --once
```

## 模式切换服务

以下服务全部使用 `std_srvs/srv/SetBool`。必须检查响应 `success`；存在服务不代表当前状态允许切换。

| 服务 | true | false |
| --- | --- | --- |
| `/motion/switch_nav_mode` | 进入 NAVIGATION；通常先到 IDLE_MODE/STAND，也允许从 ACTION_PLAY 进入 | 请求 IDLE_MODE；通常要求已停止到 STAND |
| `/switch_teleoperation` | 从 READY 或 IDLE_MODE/STAND 进入 TELEOPERATION | 依当前状态返回 READY 或 IDLE_MODE；需确实在 TELEOPERATION |
| `/switch_autonomous` | 从 READY、IDLE_MODE/STAND 或 NAVIGATION 进入 ACTION_PLAY | 播放器须 Idle，返回上一个模式 |
| `/motion/upper_body_debug` | 从 READY 或 IDLE_MODE/STAND 进入 UPPER_BODY_DEBUG | 依状态返回 READY 或 IDLE_MODE |
| `/motion/whole_body_debug` | 从 READY 或 IDLE_MODE/STAND 进入 WHOLE_BODY_DEBUG | 返回上一个模式；需确实在 WHOLE_BODY_DEBUG |
| `/motion/nav_upper_body_debug` | 只在 NAVIGATION 打开并行上身调试 | 关闭并行调试，导航上身恢复固定姿态 |

`/switch_drive_mode` 不在该基准中。`/motion/switch_nav_mode(false)` 返回 IDLE_MODE，不能写成 TELEOPERATION。
WHOLE_BODY_DEBUG 不能直接切换 ACTION_PLAY；先退出调试。模式守卫还依赖实际运动状态，以上不是任意状态下的成功承诺。

## 导航速度

`/navigation/cmd_vel` 的类型是 `geometry_msgs/msg/Twist`。通常需要 NAVIGATION；
从 NAVIGATION 进入的 ACTION_PLAY 也能接收导航速度。
当前回调使用 `linear.x` 和 `angular.z` 做映射，不使用 `linear.y`，且只在前后移动达到映射阈值时处理转向。
不能据此接口假定支持横移或原地旋转。

下面步骤会产生运动，先完成[实机联调准备](../testing/real-robot.md)：

```bash
ros2 run casbot2_tools interface_cli set_robot_mode --mode WALK
ros2 run casbot2_tools interface_cli switch_nav_mode --enable true
ros2 run casbot2_tools interface_cli pub_cmd_vel --vx 0.2 --wz 0 --seconds 2 --hz 20
# 从反馈确认 state: STAND 后再退出
ros2 run casbot2_tools interface_cli switch_nav_mode --enable false
```

CLI 在结束和可处理的中断时重复发送零速度。不要依赖断流自动停车：当前导航回调记录时间，
但使用速度的路径没有完整的超时清零；进程被强制终止、网络断开时无法保证补发停止指令。

UPPER_BODY_DEBUG 下可使用 `/upper_body_debug/cmd_vel`。
NAVIGATION 中需要同时控制上身时，先调用 `nav_upper_body_debug --enable true`，上身仍向 `/upper_body_debug/joint_cmd` 发送。
退出前将速度置零，并关闭并行上身调试。

## 全身调试与反馈

| Topic | 类型 | 作用 |
| --- | --- | --- |
| `/motion/joint_cmd` | `sensor_msgs/msg/JointState` | 标准全身命令，使用默认 PD |
| `/motion/joint_state` | `sensor_msgs/msg/JointState` | 标准实测反馈 |
| `/motion/debug/joint_cmd` | `crb_ros_msg/msg/JointStateData` | 自定义增益全身命令 |
| `/motion/debug/joint_state` | `crb_ros_msg/msg/JointStateData` | 实测位置及当前生效 PD |
| `/motion/imu` | `sensor_msgs/msg/Imu` | 全身调试 IMU |
| `/motion/current_mode` | `std_msgs/msg/Int32` | 内部模式值，WHOLE_BODY_DEBUG 为 7 |
| `/motion/cmd_vel` | `geometry_msgs/msg/Twist` | 全身调试速度反馈 |
| `/joint_states` | `sensor_msgs/msg/JointState` | 常规实测关节状态 |
| `/joint_control` | `sensor_msgs/msg/JointState` | 常规输出指令镜像，不是实测反馈 |

前七个 Topic 的处理/反馈位于 WHOLE_BODY_DEBUG 更新路径。节点可以出现在 ROS 图中，但未进入模式时不会持续发布反馈。
`/joint_states` 和 `/joint_control` 不含 `kp/kd`。上述控制与反馈通常为 Reliable、Volatile、KeepLast(10)。

不要混用两条全身命令通道：当前实现优先使用缓存的 debug 命令，未显式清除该缓存时标准命令可能持续被遮蔽。
全身命令建议从完整实测姿态构建，只修改目标关节，避免省略上身关节导致服务端构造空名称或零目标。

```bash
ros2 run casbot2_tools interface_cli sub_joint_states --seconds 3
# 以下两项需已进入 WHOLE_BODY_DEBUG
ros2 run casbot2_tools interface_cli sub_motion_joint_state --seconds 3
ros2 run casbot2_tools interface_cli sub_motion_debug_joint_state --seconds 3
```

## 上身与增益

`/upper_body_debug/joint_cmd` 使用 `UpperJointData`，需要 UPPER_BODY_DEBUG 或 NAVIGATION 的并行调试开关。
关节命令使用反馈中的完整名称；腿为 `leg_l1_joint`…`leg_l6_joint`、`leg_r1_joint`…`leg_r6_joint`。

`JointStateData` 的 `name/position/velocity/effort` 必须等长。
自定义 PD 取决于运控配置 `debug_mode_params.use_default_kp_kd`：

- `true`：使用运行配置的默认增益，示例可留空 `kp/kd`；填写增益不代表会生效。
- `false`：为非灵巧手关节提供完整增益。SDK 统一按 `name` 顺序跳过灵巧手，构造紧凑 `kp/kd` 数组。
- debug 反馈增益也跳过灵巧手。不能用 `msg.kp[i]` 直接索引任意 `msg.name[i]`；工具中的 `pd_by_name` 提供映射。

部分上身校验路径也接受与 name 等长的增益；全身调度的消费方式并不一致。
为兼容当前 main，SDK 统一使用紧凑格式，避免为灵巧手填零占位。

关节调试双语言源码及保持姿态示例见[关节调试](debug.md)。

## 动作播放

`/basic_action_play` 使用 `BasicActionPlay`，Goal `type` 是运行端 `.data` 文件的名称（不带扩展名）。
通常先进入 ACTION_PLAY，确认动作文件和机器人自由度/手型匹配，当前姿态满足动作第一帧检查。
服务器可在 ROS Action 状态 SUCCEEDED 的同时返回 `if_success=false`，客户端必须检查二者。

接口定义包含 `Feedback.state`，但当前 ActionPlayer 实现没有发布反馈；不能用“未收到反馈”判断播放失败。
收到 Goal 接受也不等于动作执行成功。

```bash
ros2 run casbot2_tools interface_cli switch_autonomous --enable true
ros2 run casbot2_tools interface_cli basic_action_play --type wave_hand
# 播放结束且播放器 Idle 后
ros2 run casbot2_tools interface_cli switch_autonomous --enable false
```

`wave_hand` 等名称取决于交付动作资源；SDK 不随仓库提供这些轨迹文件。

## 外部组件

`/voice_svr`、`/casbot/event_service`、相机、雷达及音频 Action 不由此次 hl_motion 主程序提供。
保留相关类型和工具作为集成入口，使用前须独立核查提供方与字段语义。
`VoicePlay` 定义未包含在本 SDK。`ActionPlay`、`SwitchMode` 是 SDK 保留的历史扩展，不能据此假定 hl_motion 存在对应服务端。
