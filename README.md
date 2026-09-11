<a id="chinese"></a>

**简体中文** · [English](#english)

<div align="center">

# CASBOT2 ROS 2 SDK

**CASBOT2 人形机器人开发工具包**

ROS 2 Humble · Ubuntu 22.04 · C++ / Python

[快速开始](#quick-start-cn) · [接口定义](crb_ros_msg/) · [开发示例](examples/) · [开发文档](examples/docs/index.md)

</div>

---

## 简介

CASBOT2 ROS 2 SDK 为机器人二次开发提供消息、服务与动作定义，以及 C++ / Python 示例、命令行工具和联调程序。仿真与实机共用同一套客户端接口和环境加载方式。

| 组成 | 内容 |
| --- | --- |
| **接口定义** | 自定义 `msg`、`srv`、`action`，独立维护在 `crb_ros_msg/` |
| **开发示例** | 状态监听、模式切换、导航、关节调试与动作调用 |
| **配套工具** | 接口命令行工具、只读检查与离线回归 |
| **开发文档** | 安装指南、接口参考、仿真与实机联调说明 |

## 仓库结构

```text
casbot2-ros2-sdk/
├── crb_ros_msg/     ROS 2 消息、服务与动作定义
├── examples/        示例、工具及配套开发资料
├── README.md        项目介绍与快速开始
└── LICENSE          许可证
```

进入 [`examples/`](examples/) 可查看五个配套包；文档、配置和脚本分别集中在其 `docs/`、`config/`、`scripts/` 子目录。

| 目录 | 用途 |
| --- | --- |
| [casbot2_cpp_demo](examples/casbot2_cpp_demo/) | C++ 客户端示例 |
| [casbot2_py_demo](examples/casbot2_py_demo/) | Python 客户端示例 |
| [casbot2_tools](examples/casbot2_tools/) | 接口 CLI 与只读检查 |
| [casbot2_cpp_tests](examples/casbot2_cpp_tests/) | C++ 分步联调程序 |
| [casbot2_py_tests](examples/casbot2_py_tests/) | Python 联调流程与离线回归 |
| [docs](examples/docs/) | 开发文档、更新记录与安全说明 |
| [config](examples/config/) | YAML / JSON 配置及文档依赖 |
| [scripts](examples/scripts/) | 环境加载、构建、测试及文档生成脚本 |

<a id="quick-start-cn"></a>

## 快速开始

### 1. 准备环境

- Ubuntu 22.04 与 ROS 2 Humble。
- `colcon`、`rosdep`、C++ 编译工具及 ROS 2 配套 Python。
- `rosdep` 已完成初始化与更新。

机器人主程序、MuJoCo 仿真程序、Docker 镜像、模型及动作资源由配套软件提供。请使用与目标机器人版本匹配的资源，详见[仿真快速开始](examples/docs/getting-started/sim.md)。

### 2. 获取与编译

以下命令在仓库根目录执行，`colcon` 会递归发现全部六个 ROS 2 包。

```bash
git clone https://github.com/CasbotRobotics/casbot2-ros2-sdk.git
cd casbot2-ros2-sdk

source /opt/ros/humble/setup.bash
rosdep install --from-paths crb_ros_msg examples --ignore-src --rosdistro humble -y
colcon build
source install/setup.bash
```

仅需接口定义时，可单独构建消息包：

```bash
colcon build --packages-select crb_ros_msg
source install/setup.bash
ros2 interface show crb_ros_msg/msg/JointStateData
```

### 3. 连接与查询

先启动配套仿真或机器人主程序，将 DDS 域号设为与目标一致。跨设备通信使用 `ROS_LOCALHOST_ONLY=0`；纯本机隔离环境可使用 `1`。

```bash
# 示例域号，请与目标配置一致
export ROS_DOMAIN_ID=72
export ROS_LOCALHOST_ONLY=0
source examples/scripts/setup_env.sh

ros2 run casbot2_tools interface_cli get_robot_mode
ros2 run casbot2_py_demo monitor_topics_demo
```

首次接入从状态查询与监听开始。运动类示例会发送控制指令，请按[运动控制指南](examples/docs/dev-guide/motion-control.md)操作，并阅读[操作安全说明](examples/docs/safety.md)。

已安装的仿真程序可通过 `bash examples/scripts/start_sim.sh <程序> [参数...]` 启动。容器的 DDS 环境变量及网络配置需按交付说明单独传入。

## 常用入口

| 用途 | 命令 |
| --- | --- |
| CLI 帮助 | `ros2 run casbot2_tools interface_cli --help` |
| 只读接口检查 | `ros2 run casbot2_tools interface_cli doctor` |
| Python 状态监听 | `ros2 run casbot2_py_demo monitor_topics_demo` |
| C++ 状态监听 | `ros2 run casbot2_cpp_demo monitor_topics_demo` |
| Python 状态查询 | `ros2 run casbot2_py_tests get_state_test` |
| C++ 状态查询 | `ros2 run casbot2_cpp_tests get_state_test` |

更多入口见[示例目录说明](examples/docs/examples.md)。目录整理不改变 ROS 包名与 `ros2 run` 命令。

## 构建与测试

```bash
bash examples/scripts/build.sh
bash examples/scripts/test.sh
```

`test.sh` 仅执行不创建 ROS 节点的离线回归。仿真／实机流程通过 `ros2 run` 显式运行，详见 [Workflow 测试](examples/docs/testing/workflow.md)。

## 开发文档

[文档首页](examples/docs/index.md) · [安装与编译](examples/docs/getting-started/quickstart.md) · [接口工具](examples/docs/api/interfaces.md) · [运动控制](examples/docs/dev-guide/motion-control.md) · [常见问题](examples/docs/troubleshooting/common-errors.md)

文档采用 MkDocs Material，构建独立于 ROS 2，需要 Python 3.11+：

```bash
python3.11 -m venv .venv-docs
source .venv-docs/bin/activate
python -m pip install -r examples/config/requirements.txt
python -m mkdocs serve -f examples/config/mkdocs.yml
```

默认预览地址为 `http://127.0.0.1:8000/`。严格构建使用 `python -m mkdocs build -f examples/config/mkdocs.yml --strict`。托管配置与维护方法见[文档部署指南](examples/docs/deployment.md)。

## 版本兼容

接口已对照 `hl_motion/main` 提交 `c3b2902`（2026-09-07）及消息子模块 `3228d83` 核对。23 个公共定义一致，另保留 `ActionPlay`、`SwitchMode` 两个历史扩展。

标准全身 Topic 使用 `sensor_msgs/msg/JointState`，带增益的 Topic 使用 `/motion/debug/` 前缀。`VoicePlay.action` 为可选配套接口，未包含在本仓库。

```bash
python3 examples/scripts/check_runtime_contract.py --motion /path/to/hl_motion
```

验证范围与服务端限制见[兼容性说明](examples/docs/about/compatibility.md)。编译及离线检查不能替代仿真／实机运动验收。

[更新记录](examples/docs/changelog.md) · [操作安全](examples/docs/safety.md) · [安全问题](examples/docs/security.md) · [许可证](LICENSE)

[返回中文顶部](#chinese) · [Switch to English →](#english)

---

<a id="english"></a>

[简体中文](#chinese) · **English**

<div align="center">

# CASBOT2 ROS 2 SDK

**Development kit for the CASBOT2 humanoid robot**

ROS 2 Humble · Ubuntu 22.04 · C++ / Python

[Quick Start](#quick-start-en) · [Interfaces](crb_ros_msg/) · [Examples](examples/) · [Documentation](examples/docs/index.md)

</div>

---

## Overview

The CASBOT2 ROS 2 SDK provides message, service and action definitions, C++ / Python examples, command-line tools and integration workflows. The same client interfaces and environment setup support simulation and physical robots.

| Component | Contents |
| --- | --- |
| **Interfaces** | Custom `msg`, `srv` and `action` definitions in the standalone `crb_ros_msg/` package |
| **Examples** | State monitoring, mode switching, navigation, joint debugging and action calls |
| **Tools** | Interface CLI, read-only checks and offline regression tests |
| **Documentation** | Installation, API reference, simulation and robot integration guides |

## Repository Layout

```text
casbot2-ros2-sdk/
├── crb_ros_msg/     ROS 2 message, service and action definitions
├── examples/        Examples, tools and supporting development resources
├── README.md        Project overview and quick start
└── LICENSE          License
```

Open [`examples/`](examples/) to browse the five companion packages. Documentation, configuration and scripts are grouped in its `docs/`, `config/` and `scripts/` subdirectories.

| Directory | Purpose |
| --- | --- |
| [casbot2_cpp_demo](examples/casbot2_cpp_demo/) | C++ client examples |
| [casbot2_py_demo](examples/casbot2_py_demo/) | Python client examples |
| [casbot2_tools](examples/casbot2_tools/) | Interface CLI and read-only checks |
| [casbot2_cpp_tests](examples/casbot2_cpp_tests/) | C++ integration workflows |
| [casbot2_py_tests](examples/casbot2_py_tests/) | Python workflows and offline regression tests |
| [docs](examples/docs/) | Developer guides, changelog and safety information |
| [config](examples/config/) | YAML / JSON configuration and documentation dependencies |
| [scripts](examples/scripts/) | Environment, build, test and documentation generation scripts |

<a id="quick-start-en"></a>

## Quick Start

### 1. Requirements

- Ubuntu 22.04 and ROS 2 Humble.
- `colcon`, `rosdep`, C++ build tools and the Python environment supplied with ROS 2.
- An initialized and updated `rosdep` installation.

Robot runtime software, MuJoCo binaries, Docker images, models and motion resources are distributed separately. Use resources matching your robot version; see [Simulation Quick Start](examples/docs/getting-started/sim.md).

### 2. Clone and Build

Run these commands from the repository root. `colcon` discovers all six ROS 2 packages recursively.

```bash
git clone https://github.com/CasbotRobotics/casbot2-ros2-sdk.git
cd casbot2-ros2-sdk

source /opt/ros/humble/setup.bash
rosdep install --from-paths crb_ros_msg examples --ignore-src --rosdistro humble -y
colcon build
source install/setup.bash
```

To build only the interface package:

```bash
colcon build --packages-select crb_ros_msg
source install/setup.bash
ros2 interface show crb_ros_msg/msg/JointStateData
```

### 3. Connect and Query

Start the supplied simulator or robot runtime and match its DDS domain. Use `ROS_LOCALHOST_ONLY=0` across machines; `1` is suitable for an isolated local setup.

```bash
# Example domain; match your runtime configuration
export ROS_DOMAIN_ID=72
export ROS_LOCALHOST_ONLY=0
source examples/scripts/setup_env.sh

ros2 run casbot2_tools interface_cli get_robot_mode
ros2 run casbot2_py_demo monitor_topics_demo
```

Begin with state queries and monitoring. Motion examples send control commands; follow the [motion control guide](examples/docs/dev-guide/motion-control.md) and read the [safety instructions](examples/docs/safety.md) before running them.

Launch an installed simulator with `bash examples/scripts/start_sim.sh <program> [arguments...]`. Configure the container's DDS variables and networking according to its delivery instructions.

## Common Commands

| Task | Command |
| --- | --- |
| CLI help | `ros2 run casbot2_tools interface_cli --help` |
| Read-only interface check | `ros2 run casbot2_tools interface_cli doctor` |
| Python state monitoring | `ros2 run casbot2_py_demo monitor_topics_demo` |
| C++ state monitoring | `ros2 run casbot2_cpp_demo monitor_topics_demo` |
| Python state query | `ros2 run casbot2_py_tests get_state_test` |
| C++ state query | `ros2 run casbot2_cpp_tests get_state_test` |

See the [package guide](examples/docs/examples.md) for more examples. Package names and `ros2 run` commands are unchanged by the directory reorganization.

## Build and Test

```bash
bash examples/scripts/build.sh
bash examples/scripts/test.sh
```

`test.sh` runs offline regression tests without creating ROS nodes. Run simulation and robot workflows explicitly with `ros2 run`; see [Workflow Tests](examples/docs/testing/workflow.md).

## Documentation

[Documentation Home](examples/docs/index.md) · [Installation](examples/docs/getting-started/quickstart.md) · [Interface CLI](examples/docs/api/interfaces.md) · [Motion Control](examples/docs/dev-guide/motion-control.md) · [Troubleshooting](examples/docs/troubleshooting/common-errors.md)

The documentation uses MkDocs Material and Python 3.11+. Building it does not require ROS 2.

```bash
python3.11 -m venv .venv-docs
source .venv-docs/bin/activate
python -m pip install -r examples/config/requirements.txt
python -m mkdocs serve -f examples/config/mkdocs.yml
```

The default preview address is `http://127.0.0.1:8000/`. Validate the site with `python -m mkdocs build -f examples/config/mkdocs.yml --strict`. See the [deployment guide](examples/docs/deployment.md) for hosting configuration and maintenance.

## Compatibility

The interfaces were checked against `hl_motion/main` commit `c3b2902` (2026-09-07) and message submodule `3228d83`. All 23 shared definitions match; `ActionPlay` and `SwitchMode` remain as legacy SDK extensions.

Standard whole-body topics use `sensor_msgs/msg/JointState`; topics carrying PD gains use the `/motion/debug/` prefix. `VoicePlay.action` is an optional runtime interface and is not included in this repository.

```bash
python3 examples/scripts/check_runtime_contract.py --motion /path/to/hl_motion
```

See [Compatibility](examples/docs/about/compatibility.md) for validation scope and runtime limitations. Build and offline checks do not replace simulation or physical robot acceptance tests.

[Changelog](examples/docs/changelog.md) · [Safety](examples/docs/safety.md) · [Security](examples/docs/security.md) · [License](LICENSE)

[Back to English](#english) · [返回中文版 →](#chinese)
