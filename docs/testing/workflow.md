# Workflow 测试

这些程序是与机器人或仿真服务交互的集成验证示例，运行时需要目标服务。它们不是可在无 ROS 环境直接运行的单元测试。

## 不连接机器人的回归检查

`casbot2_py_tests/test/` 检查 CLI 帮助、可选音频接口缺失和生成服务类型的响应字段。
先加载 ROS 2 与已编译的 SDK，再运行：

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
bash scripts/test.sh
```

这组检查不创建 ROS 节点，也不发送机器人指令。

## 分步验证

在 SDK 根目录完成编译并加载 `install/setup.bash` 后：

| 步骤 | Python 文件 | C++ 入口 | 作用 |
| --- | --- | --- | --- |
| 1 | `get_state_test.py` | `get_state_test` | 查询状态 |
| 2 | `switch_mode_test.py` | `switch_mode_test` | 切换模式 |
| 3 | `joint_states_test.py` | `joint_states_test` | 订阅关节状态 |
| 4 | `cmd_vel_test.py` | `cmd_vel_test` | 发布速度 |
| 5 | `upper_body_debug_test.py` | `upper_body_debug_test` | 上身调试 |

Python 程序位于 `casbot2_py_tests/casbot2_py_tests/`：

```bash
ros2 run casbot2_py_tests get_state_test
```

C++ 包位于 `casbot2_cpp_tests/`，从仓库根目录编译：

```bash
colcon build --packages-up-to casbot2_cpp_tests
source install/setup.bash
ros2 run casbot2_cpp_tests get_state_test
```

## 完整流程

Python 目录包含 `test_walk_flow.py`、`test_upper_body_flow.py`、`test_whole_body_flow.py` 和 `test_sensors_and_actions_flow.py`，
分别覆盖行走、上身、全身以及传感器与动作流程。

运行前检查脚本参数、机器人模式及资源配置，并按[开机自检](boot-check.md)、[仿真联调](simulation.md)、[实机联调](real-robot.md)执行。
不能因为文件以 `test_` 开头就将其加入无条件执行的 CI 测试；其中包含运动控制操作。

## 当前 main 的流程前提

完整运动流程要求初始 `/motion/status` 为 `mode: READY, state: READY` 或 `mode: IDLE_MODE, state: STAND`，
不自动使用 ZERO 恢复。行走流程进入 NAVIGATION 后才发送速度，结束补发零速度并等待 STAND。
上身/全身流程从实测姿态构造相对目标，依赖 `use_default_kp_kd=true`。
`test_action_play_flow` 先验证全身调试不能直接进入动作模式，再退出调试播放；需配套动作文件。

增益测试改为只读回读，不在一次测试中假定运行端同时配置了默认增益和显式增益：

```bash
# 运行端已进入 WHOLE_BODY_DEBUG
ros2 run casbot2_py_tests test_kp_kd_joint_states
ros2 run casbot2_py_tests test_kp_kd_debug --joint head_pitch_joint
# 可与现场预期值核对（数值由操作者按运行配置填写）
ros2 run casbot2_py_tests test_kp_kd_debug --help
```

旧 `--tc 1 2 3 4 5` 参数已移除，避免把缺少反馈、未运动或一次发布成功误判成增益验证通过。
