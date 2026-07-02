<a id="chinese"></a>

中文 | [English](#english)

# CASBOT2 ROS 2 SDK

> **官方 ROS 2 二次开发 SDK** — 基于 ROS 2 Humble，提供消息定义、接口文档与可运行示例，用于 CASBOT2 机器人应用开发。

本仓库是 CASBOT2 的 **ROS 2 SDK**，包含：

- **ROS 2 接口包** `crb_ros_msg`（msg / srv / action）
- 可直接运行的 C++/Python 示例工程
- 覆盖核心接口的 workflow 测试脚本
- 开机自检、仿真联调、实机联调的操作指引
- 接口全覆盖调用示例（Service / Topic / Action）

## 核心文档（必读）

建议按以下顺序阅读：

| 文档 | 文件名 | 定位 |
| --- | --- | --- |
| [快速开始](docs/ROS2_快速开始.md) | `ROS2_快速开始.md` | 环境初始化与常用命令速查 |
| [CASBOT02 二次开发手册](docs/CASBOT02_二次开发手册.md) | `CASBOT02_二次开发手册.md` | **总览手册**：整机结构、传感器、SDK 说明、语音/技能/运控应用开发 |
| [ROS 2 运控接口参考](docs/ROS2_运控接口参考.md) | `ROS2_运控接口参考.md` | **运控主文档**：模式切换、Topic/Service/Action 定义、调用时序与安全约束 |
| [运动控制接口摘要](docs/ROS2_运动控制接口摘要.md) | `ROS2_运动控制接口摘要.md` | 发布版接口速查表 |
| [自定义消息包使用指南](docs/ROS2_自定义消息包使用指南.md) | `ROS2_自定义消息包使用指南.md` | `crb_ros_msg` 编译与引用 |

> 运控相关开发请优先阅读 [`ROS2_运控接口参考.md`](docs/ROS2_运控接口参考.md)，再结合 `examples/` 中的示例代码联调。

## SDK 组成

| 组件 | 路径 | 说明 |
| --- | --- | --- |
| ROS 2 接口包 | `packages/crb_ros_msg/` | SDK 核心：自定义 msg / srv / action |
| 示例与测试 | `examples/` | C++/Python demo、workflow、场景指引 |
| 开发文档 | `docs/` | 快速开始、二次开发手册、接口参考等 |

## 目录说明

- `packages/crb_ros_msg/`：**SDK 核心** — ROS 2 自定义消息包（msg/srv/action）
- `examples/README.md`：示例总导航（场景、接口、workflow、基础 demo）
- `examples/cpp/casbot2_cpp_demo/`：C++ 基础 demo 包
- `examples/python/casbot2_py_demo/`：Python 基础 demo 包
- `examples/workflows/cpp/casbot_cpp_test/`：C++ workflow 测试工程（t01~t05）
- `examples/workflows/python/casbot_py_test/`：Python workflow 测试脚本（t01~t05 + test_flow）
- `examples/scenarios/`：开机自检、仿真联调、实机联调
- `examples/interfaces/README.md`：接口全覆盖说明
- `examples/interfaces/python/all_interfaces_demo.py`：全接口 Python 调用工具
- `docs/`：SDK 文档（快速开始、二次开发手册、接口参考等）

## 环境要求

- Ubuntu 22.04
- **ROS 2 Humble**（本 SDK 基于 ROS 2，不支持 ROS 1）
- 已安装并可解析 SDK 接口包 `crb_ros_msg`

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

- [`docs/ROS2_快速开始.md`](docs/ROS2_快速开始.md)
- [`docs/CASBOT02_二次开发手册.md`](docs/CASBOT02_二次开发手册.md)
- [`docs/ROS2_运控接口参考.md`](docs/ROS2_运控接口参考.md) — 运控接口主文档（**优先阅读**）
- [`docs/ROS2_运动控制接口摘要.md`](docs/ROS2_运动控制接口摘要.md)
- [`docs/ROS2_自定义消息包使用指南.md`](docs/ROS2_自定义消息包使用指南.md)
- [`examples/interfaces/README.md`](examples/interfaces/README.md)

---

<a id="english"></a>

[中文](#chinese) | English

# CASBOT2 ROS 2 SDK

> **Official ROS 2 SDK for secondary development** — Built on ROS 2 Humble, providing interface definitions, documentation, and runnable examples for CASBOT2 application development.

This repository is the **ROS 2 SDK** for CASBOT2, including:

- **ROS 2 interface package** `crb_ros_msg` (msg / srv / action)
- Runnable C++ and Python demo packages
- Workflow test scripts for core interfaces
- Scenario guides for boot check, simulation, and real robot validation
- A full interface usage toolkit (Service / Topic / Action)

## Primary Documentation (Read First)

Recommended reading order:

| Document | Filename | Role |
| --- | --- | --- |
| [Quick Start](docs/ROS2_快速开始.md) | `ROS2_快速开始.md` | Environment setup and common commands |
| [CASBOT02 Development Manual](docs/CASBOT02_二次开发手册.md) | `CASBOT02_二次开发手册.md` | **Overview manual**: robot structure, sensors, SDK overview, voice/skills/motion development |
| [ROS 2 Motion Control Reference](docs/ROS2_运控接口参考.md) | `ROS2_运控接口参考.md` | **Primary motion doc**: modes, Topic/Service/Action definitions, call sequences, safety |
| [Motion Control API Summary](docs/ROS2_运动控制接口摘要.md) | `ROS2_运动控制接口摘要.md` | Release-edition API quick reference |
| [Custom Message Package Guide](docs/ROS2_自定义消息包使用指南.md) | `ROS2_自定义消息包使用指南.md` | Building and using `crb_ros_msg` |

> For motion-control development, read [`ROS2_运控接口参考.md`](docs/ROS2_运控接口参考.md) first, then use the examples under `examples/` as reference implementations.

## SDK Components

| Component | Path | Description |
| --- | --- | --- |
| ROS 2 interface package | `packages/crb_ros_msg/` | SDK core: custom msg / srv / action |
| Examples & tests | `examples/` | C++/Python demos, workflows, scenario guides |
| Documentation | `docs/` | Quick start, development manual, API reference |

## Repository Layout

- `packages/crb_ros_msg/`: **SDK core** — ROS 2 custom interface package (`msg` / `srv` / `action`)
- `examples/README.md`: unified examples index
- `examples/cpp/casbot2_cpp_demo/`: C++ base demos
- `examples/python/casbot2_py_demo/`: Python base demos
- `examples/workflows/cpp/casbot_cpp_test/`: C++ workflow tests (t01~t05)
- `examples/workflows/python/casbot_py_test/`: Python workflow tests (t01~t05 + test_flow)
- `examples/scenarios/`: boot check / simulation / real robot operation guides
- `examples/interfaces/README.md`: full interface usage guide
- `examples/interfaces/python/all_interfaces_demo.py`: unified Python interface runner
- `docs/`: SDK documentation (quick start, development manual, API reference)

## Requirements

- Ubuntu 22.04
- **ROS 2 Humble** (this SDK is ROS 2–based; ROS 1 is not supported)
- SDK interface package `crb_ros_msg` available in your ROS environment

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

- [`docs/ROS2_快速开始.md`](docs/ROS2_快速开始.md)
- [`docs/CASBOT02_二次开发手册.md`](docs/CASBOT02_二次开发手册.md)
- [`docs/ROS2_运控接口参考.md`](docs/ROS2_运控接口参考.md) — Primary motion-control interface reference (**read first**)
- [`docs/ROS2_运动控制接口摘要.md`](docs/ROS2_运动控制接口摘要.md)
- [`docs/ROS2_自定义消息包使用指南.md`](docs/ROS2_自定义消息包使用指南.md)
- [`examples/interfaces/README.md`](examples/interfaces/README.md)
