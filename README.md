<a id="chinese"></a>

中文 | [English](#english)

# CASBOT2 二次开发示例仓库

本仓库用于 CASBOT2 的 ROS 2 二次开发，包含：

- 可直接运行的 C++/Python 示例工程
- 覆盖核心接口的 workflow 测试脚本
- 开机自检、仿真联调、实机联调的操作指引
- 接口全覆盖调用示例（Service / Topic / Action）

## 核心文档（必读）

> **[`docs/二开文档（ros2接口部分）（26.06.29）.md`](docs/二开文档（ros2接口部分）（26.06.29）.md)** 是本仓库的 **ROS 2 运控接口权威参考**，基于 `hl_motion` 源码整理，涵盖模式切换、Topic/Service/Action 定义、调用时序与安全约束。
>
> 进行二次开发或联调前，**请先阅读该文档**，再对照 `examples/` 中的示例代码。其他文档（快速开始、运动控制接口摘要等）均为辅助说明，以该文档为准。

| 文档 | 定位 |
|---|---|
| **[二开文档（ros2接口部分）](docs/二开文档（ros2接口部分）（26.06.29）.md)** | **主文档**：接口总览、模式说明、详细调用示例、关节名速查 |
| [快速开始](docs/快速开始.md) | 环境初始化与常用命令速查 |
| [运动控制接口](docs/运动控制接口.md) | 发布版接口摘要 |
| [ROS2 自定义消息包使用指南](docs/ROS2_自定义消息包使用指南.md) | `crb_ros_msg` 编译与引用 |

## 目录说明

- `packages/crb_ros_msg/`：ROS 2 自定义消息包（msg/srv/action）
- `examples/README.md`：示例总导航（场景、接口、workflow、基础 demo）
- `examples/cpp/casbot2_cpp_demo/`：C++ 基础 demo 包
- `examples/python/casbot2_py_demo/`：Python 基础 demo 包
- `examples/workflows/cpp/casbot_cpp_test/`：C++ workflow 测试工程（t01~t05）
- `examples/workflows/python/casbot_py_test/`：Python workflow 测试脚本（t01~t05 + test_flow）
- `examples/scenarios/`：开机自检、仿真联调、实机联调
- `examples/interfaces/README.md`：接口全覆盖说明
- `examples/interfaces/python/all_interfaces_demo.py`：全接口 Python 调用工具
- `docs/`：手册、接口、快速开始、发布说明等文档

## 环境要求

- Ubuntu 22.04
- ROS 2 Humble
- 已安装并可解析 `crb_ros_msg`

推荐环境初始化：

```bash
source /opt/ros/humble/setup.bash
source /workspace/prod_casbot02_basic/install/setup.bash 2>/dev/null || true
source /workspace/HLmotion/setup.bash 2>/dev/null || source /workspace/hl_motion/setup.bash 2>/dev/null || true
```

## 快速开始

### 1) 运行基础 Python Demo

```bash
cd examples/python
colcon build --packages-select casbot2_py_demo
source install/setup.bash
ros2 run casbot2_py_demo control_demo
```

### 2) 运行 C++ Workflow Demo

```bash
cd examples/workflows/cpp/casbot_cpp_test
colcon build --packages-select casbot_cpp_test
source install/setup.bash
ros2 run casbot_cpp_test t01_get_state
```

### 3) 运行接口全覆盖工具

```bash
python3 examples/interfaces/python/all_interfaces_demo.py --help
```

## 安全提示

- 首次联调请从低速、小幅度关节指令开始
- 每次发控制命令前先确认当前模式
- 调试模式需有安全员在场，并确保急停可用

## 相关文档

- **[`docs/二开文档（ros2接口部分）（26.06.29）.md`](docs/二开文档（ros2接口部分）（26.06.29）.md)** — ROS 2 运控接口主文档（**优先阅读**）
- `docs/快速开始.md`
- `docs/二次开发手册.md`
- `docs/运动控制接口.md`
- `docs/ROS2_自定义消息包使用指南.md`
- `examples/interfaces/README.md`

---

<a id="english"></a>

[中文](#chinese) | English

# CASBOT2 Secondary Development Examples

This repository provides ROS 2 secondary development assets for CASBOT2, including:

- Runnable C++ and Python demo packages
- Workflow test scripts for core interfaces
- Scenario guides for boot check, simulation, and real robot validation
- A full interface usage toolkit (Service / Topic / Action)

## Primary Documentation (Read First)

> **[`docs/二开文档（ros2接口部分）（26.06.29）.md`](docs/二开文档（ros2接口部分）（26.06.29）.md)** is the **authoritative ROS 2 motion-control interface reference** for this repository. It is derived from the `hl_motion` source and covers mode switching, Topic/Service/Action definitions, call sequences, and safety constraints.
>
> **Read this document before** secondary development or integration testing, then use the examples under `examples/` as reference implementations. Other docs (quick start, motion API summary, etc.) are supplementary; this document takes precedence.

| Document | Role |
|---|---|
| **[二开文档（ros2接口部分）](docs/二开文档（ros2接口部分）（26.06.29）.md)** | **Primary**: interface overview, modes, detailed examples, joint name lookup |
| [快速开始](docs/快速开始.md) | Environment setup and common commands |
| [运动控制接口](docs/运动控制接口.md) | Release-edition API summary |
| [ROS2 自定义消息包使用指南](docs/ROS2_自定义消息包使用指南.md) | Building and using `crb_ros_msg` |

## Repository Layout

- `packages/crb_ros_msg/`: ROS 2 custom interface package (`msg` / `srv` / `action`)
- `examples/README.md`: unified examples index
- `examples/cpp/casbot2_cpp_demo/`: C++ base demos
- `examples/python/casbot2_py_demo/`: Python base demos
- `examples/workflows/cpp/casbot_cpp_test/`: C++ workflow tests (t01~t05)
- `examples/workflows/python/casbot_py_test/`: Python workflow tests (t01~t05 + test_flow)
- `examples/scenarios/`: boot check / simulation / real robot operation guides
- `examples/interfaces/README.md`: full interface usage guide
- `examples/interfaces/python/all_interfaces_demo.py`: unified Python interface runner
- `docs/`: manuals, API docs, quick start, release notes

## Requirements

- Ubuntu 22.04
- ROS 2 Humble
- `crb_ros_msg` available in your ROS environment

Recommended shell initialization:

```bash
source /opt/ros/humble/setup.bash
source /workspace/prod_casbot02_basic/install/setup.bash 2>/dev/null || true
source /workspace/HLmotion/setup.bash 2>/dev/null || source /workspace/hl_motion/setup.bash 2>/dev/null || true
```

## Quick Start

### 1) Run Python base demo

```bash
cd examples/python
colcon build --packages-select casbot2_py_demo
source install/setup.bash
ros2 run casbot2_py_demo control_demo
```

### 2) Run C++ workflow demo

```bash
cd examples/workflows/cpp/casbot_cpp_test
colcon build --packages-select casbot_cpp_test
source install/setup.bash
ros2 run casbot_cpp_test t01_get_state
```

### 3) Run full interface tool

```bash
python3 examples/interfaces/python/all_interfaces_demo.py --help
```

## Safety Notes

- Start with low speed and small joint commands
- Always confirm current robot mode before control commands
- Keep a safety operator and emergency stop ready during debug mode

## Documentation

- **[`docs/二开文档（ros2接口部分）（26.06.29）.md`](docs/二开文档（ros2接口部分）（26.06.29）.md)** — Primary ROS 2 motion-control interface reference (**read first**)
- `docs/快速开始.md`
- `docs/二次开发手册.md`
- `docs/运动控制接口.md`
- `docs/ROS2_自定义消息包使用指南.md`
- `examples/interfaces/README.md`
