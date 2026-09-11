<a id="chinese"></a>

中文 | [English](#english)

# 运行仿真

## 目标

在 MuJoCo 仿真环境验证模式切换、速度控制、上身调试与动作流程。

## 推荐顺序

1. 启动仿真与 `hlorin` 主进程
2. 执行开机自检（见 `boot_check.md`）
3. 运行基础控制脚本：
   - `switch_mode_test.py`
   - `cmd_vel_test.py`
   - `upper_body_debug_test.py`
4. 运行流程测试脚本：
   - `test_walk_flow.py`
   - `test_upper_body_flow.py`
   - `test_whole_body_flow.py`
   - `test_sensors_and_actions_flow.py`

## Python 运行示例

```bash
# 从 SDK 仓库根目录执行
ros2 run casbot2_py_tests get_state_test
ros2 run casbot2_py_tests test_walk_flow
```

## C++ 运行示例

```bash
# 从 SDK 仓库根目录执行
colcon build --packages-up-to casbot2_cpp_tests
source install/setup.bash
ros2 run casbot2_cpp_tests get_state_test
ros2 run casbot2_cpp_tests cmd_vel_test
```

## 注意事项

- 仿真分支可能与实机接口略有差异，需以当前 binary 为准。
- 部分动作在仿真下可能受限（例如腿部锁定导致动作返回失败）。


---

<a id="english"></a>

[中文](#chinese) | English

# Simulation Workflow

## Goal

Validate mode switching, velocity control, upper-body debug, and action flow in MuJoCo simulation.

## Recommended Sequence

1. Start simulation and `hlorin`
2. Run boot check (`boot_check.md`)
3. Run base control scripts:
   - `switch_mode_test.py`
   - `cmd_vel_test.py`
   - `upper_body_debug_test.py`
4. Run flow tests:
   - `test_walk_flow.py`
   - `test_upper_body_flow.py`
   - `test_whole_body_flow.py`
   - `test_sensors_and_actions_flow.py`

## Python Example

```bash
# 从 SDK 仓库根目录执行
ros2 run casbot2_py_tests get_state_test
ros2 run casbot2_py_tests test_walk_flow
```

## C++ Example

```bash
# 从 SDK 仓库根目录执行
colcon build --packages-up-to casbot2_cpp_tests
source install/setup.bash
ros2 run casbot2_cpp_tests get_state_test
ros2 run casbot2_cpp_tests cmd_vel_test
```

## Notes

- Simulation branch and real robot interfaces may differ; follow current binary behavior.
- Some actions can be limited in simulation (for example, leg lock causing action failure).
