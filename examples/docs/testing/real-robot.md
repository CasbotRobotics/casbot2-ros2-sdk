!!! danger "实机联调前置条件"
    确认急停可用、安全员在场、机器人支撑与周围环境符合交付规程。先做状态查询，再按顺序执行控制测试。

<a id="chinese"></a>

中文 | [English](#english)

# 运行实机测试

## 目标

按照安全顺序完成实机接口验证，覆盖模式切换、行走、上身调试和全身调试。

## 安全前提

- 周围有安全员
- 初始使用低速、低增益
- 实机已完成站立准备，急停可用

## 推荐测试流程

1. 开机自检（`boot_check.md`）
2. 模式服务检查（`get_state_test`、`switch_mode_test`）
3. 低速行走验证（`cmd_vel_test`）
4. 上身调试验证（`upper_body_debug_test`）
5. 全身调试验证（`test_whole_body_flow.py`）
6. Debug 增益验证（`test_kp_kd_debug.py`）

## 实机执行建议

- 先执行 Python 快速检查脚本，再执行 C++ 稳定测试程序。
- 每一阶段结束后回到 `STAND` 或 `ZERO`，再进入下一阶段。

## 典型命令

```bash
# 从 SDK 仓库根目录执行
ros2 run casbot2_py_tests get_state_test
ros2 run casbot2_py_tests switch_mode_test
ros2 run casbot2_py_tests cmd_vel_test
```

## 判定标准

- 服务调用成功率高
- 关节反馈连续且无异常跳变
- 模式切换符合预期，不出现不可恢复状态


---

<a id="english"></a>

[中文](#chinese) | English

# Real Robot Validation Workflow

## Goal

Complete real robot interface validation in a safe order, covering mode switching, walking, upper-body debug, and whole-body debug.

## Safety Preconditions

- Safety operator is present
- Start with low speed and low gains
- Robot is ready in standing state and emergency stop is available

## Recommended Test Flow

1. Boot check (`boot_check.md`)
2. Mode service checks (`get_state_test`, `switch_mode_test`)
3. Low-speed walking check (`cmd_vel_test`)
4. Upper-body debug check (`upper_body_debug_test`)
5. Whole-body debug check (`test_whole_body_flow.py`)
6. Debug gain check (`test_kp_kd_debug.py`)

## Execution Suggestions

- Run Python quick checks first, then C++ stability tests.
- Return to `STAND` or `ZERO` after each stage before entering the next stage.

## Typical Commands

```bash
# 从 SDK 仓库根目录执行
ros2 run casbot2_py_tests get_state_test
ros2 run casbot2_py_tests switch_mode_test
ros2 run casbot2_py_tests cmd_vel_test
```

## Pass Criteria

- High service call success rate
- Continuous joint feedback without abnormal jumps
- Mode switches behave as expected without unrecoverable state
