<div align="center">

# CASBOT2 ROS 2 SDK

**CASBOT2 人形机器人二次开发工具包**<br>
**ROS 2 development kit for the CASBOT2 humanoid robot**

[![ROS 2 SDK](https://github.com/CasbotRobotics/casbot2-ros2-sdk/actions/workflows/ros.yml/badge.svg?branch=main)](https://github.com/CasbotRobotics/casbot2-ros2-sdk/actions/workflows/ros.yml)
[![Documentation](https://github.com/CasbotRobotics/casbot2-ros2-sdk/actions/workflows/docs.yml/badge.svg?branch=main)](https://github.com/CasbotRobotics/casbot2-ros2-sdk/actions/workflows/docs.yml)

[快速开始 · Quick Start](#quick-start) · [接口定义 · Interfaces](crb_ros_msg/) · [开发示例 · Examples](examples/) · [文档 · Documentation](docs/index.md)

</div>

## 简介 · Overview

CASBOT2 ROS 2 SDK 提供机器人二次开发所需的消息、服务与动作定义，以及 C++ / Python 示例、命令行工具和联调程序。仿真与实机使用同一套客户端接口和环境加载方式。

The CASBOT2 ROS 2 SDK provides message, service and action definitions, C++ / Python examples, command-line tools and integration workflows. The same client interfaces and environment setup support simulation and physical robots.

| 功能 · Component | 说明 · Description |
| --- | --- |
| **ROS 2 接口 · Interfaces** | 自定义 `msg`、`srv`、`action` 定义 · Custom message, service and action definitions |
| **开发示例 · Examples** | C++ / Python 状态查询、模式切换与运动控制 · State monitoring, mode switching and motion control |
| **接口工具 · Tools** | 统一 CLI 与只读接口检查 · A unified CLI and read-only interface checks |
| **联调验证 · Validation** | 仿真／实机流程与离线回归 · Integration workflows and offline regression tests |
| **开发文档 · Documentation** | 入门指南、接口参考与在线文档构建 · Getting started, API reference and documentation builds |

## 环境要求 · Requirements

| 项目 · Item | 要求 · Requirement |
| --- | --- |
| 操作系统 · Operating system | Ubuntu 22.04 |
| ROS 2 | Humble |
| 开发环境 · Development tools | `colcon`、`rosdep`、C++ 编译工具、ROS 2 配套 Python · C++ build tools and the Python environment supplied with ROS 2 |
| 文档构建 · Documentation only | Python 3.11+ |

机器人主程序、MuJoCo 仿真程序、Docker 镜像及模型／动作资源由配套软件提供，未随本仓库分发。请使用与目标机器人版本匹配的资源，参见[仿真快速开始](docs/getting-started/sim.md)。

Robot runtime software, MuJoCo binaries, Docker images, models and motion resources are distributed separately. Use the resources supplied for your robot version; see [Simulation Quick Start](docs/getting-started/sim.md).

## 仓库结构 · Repository Layout

接口包独立保留在根目录；示例、工具与测试统一放在 `examples/`，进入该目录即可查看全部配套开发包。

The interface package lives at the repository root. All example, tool and test packages are grouped under `examples/`.

```text
casbot2-ros2-sdk/
├── crb_ros_msg/                 # ROS 2 接口定义 / Interface definitions
│   ├── msg/
│   ├── srv/
│   └── action/
├── examples/                    # 配套开发包 / Examples, tools and tests
│   ├── casbot2_cpp_demo/         # C++ 示例 / C++ examples
│   ├── casbot2_py_demo/          # Python 示例 / Python examples
│   ├── casbot2_tools/            # 命令行工具 / CLI tools
│   ├── casbot2_cpp_tests/        # C++ 联调 / C++ integration workflows
│   └── casbot2_py_tests/         # Python 联调与回归 / Workflows and regression tests
├── docs/                        # 开发文档 / Documentation
├── scripts/                     # 环境、构建与测试 / Setup, build and test scripts
├── .github/workflows/           # 持续集成 / CI workflows
├── mkdocs.yml                   # 文档站点配置 / Documentation configuration
├── requirements.txt             # 文档依赖 / Documentation dependencies
└── README.md
```

<a id="quick-start"></a>

## 快速开始 · Quick Start

### 1. 获取与构建 · Clone and build

先安装 ROS 2 Humble 与开发工具，并完成 `rosdep` 初始化、更新。以下命令均在仓库根目录执行；`colcon` 会递归发现全部 6 个 ROS 2 包。

Install ROS 2 Humble and the development tools, then initialize and update `rosdep`. Run the following commands from the repository root; `colcon` discovers all six ROS 2 packages recursively.

```bash
git clone https://github.com/CasbotRobotics/casbot2-ros2-sdk.git
cd casbot2-ros2-sdk

source /opt/ros/humble/setup.bash
rosdep install --from-paths crb_ros_msg examples --ignore-src --rosdistro humble -y
colcon build
source install/setup.bash
```

仅构建接口包 · Build only the interface package:

```bash
colcon build --packages-select crb_ros_msg
source install/setup.bash
ros2 interface show crb_ros_msg/msg/JointStateData
```

### 2. 连接目标 · Connect to the runtime

先启动配套仿真或机器人主程序，将 DDS 域号设为与目标一致。跨设备通信使用 `ROS_LOCALHOST_ONLY=0`；纯本机隔离环境可使用 `1`。

Start the supplied simulator or robot runtime and match its DDS domain. Use `ROS_LOCALHOST_ONLY=0` for communication across machines; `1` is suitable for an isolated local setup.

```bash
# 示例域号，请与目标配置一致 / Example domain; match your runtime
export ROS_DOMAIN_ID=72
export ROS_LOCALHOST_ONLY=0
source scripts/setup_env.sh

ros2 run casbot2_tools interface_cli get_robot_mode
ros2 run casbot2_py_demo monitor_topics_demo
```

如需通过统一环境启动已安装的仿真程序，可使用 `bash scripts/start_sim.sh <程序> [参数...]`。容器的 DDS 环境变量与网络配置须按交付说明单独传入。

To launch an installed simulator with the SDK environment, use `bash scripts/start_sim.sh <program> [arguments...]`. Configure the container's DDS variables and networking according to its delivery instructions.

### 3. 使用示例 · Run examples

包名和 `ros2 run` 命令保持不变，完整目录说明见 [examples/README.md](examples/README.md)。

Package names and `ros2 run` commands remain unchanged. See [examples/README.md](examples/README.md) for the complete package guide.

| 用途 · Task | 命令 · Command |
| --- | --- |
| CLI 帮助 · CLI help | `ros2 run casbot2_tools interface_cli --help` |
| 接口检查 · Interface check | `ros2 run casbot2_tools interface_cli doctor` |
| Python 状态监听 · Python monitoring | `ros2 run casbot2_py_demo monitor_topics_demo` |
| C++ 状态监听 · C++ monitoring | `ros2 run casbot2_cpp_demo monitor_topics_demo` |
| Python 状态查询 · Python state query | `ros2 run casbot2_py_tests get_state_test` |
| C++ 状态查询 · C++ state query | `ros2 run casbot2_cpp_tests get_state_test` |

运动示例会发送控制指令。首次接入先读取状态，再按[运控指南](docs/dev-guide/motion-control.md)执行模式切换与控制；运行前阅读 [SAFETY.md](SAFETY.md)。

Motion examples send control commands. Begin with state monitoring, follow the [motion control guide](docs/dev-guide/motion-control.md), and read [SAFETY.md](SAFETY.md) before running them.

## 构建与测试 · Build and Test

```bash
source scripts/setup_env.sh
bash scripts/build.sh
bash scripts/test.sh
```

`test.sh` 仅执行不创建 ROS 节点的离线回归。仿真与实机流程通过 `ros2 run` 显式运行，详见 [Workflow 测试](docs/testing/workflow.md)。

`test.sh` runs offline regression tests without creating ROS nodes. Run simulation and robot workflows explicitly with `ros2 run`; see [Workflow Tests](docs/testing/workflow.md).

## 开发文档 · Documentation

| 阅读目标 · Topic | 文档入口 · Guide |
| --- | --- |
| 安装与接入 · Installation | [环境准备](docs/getting-started/environment.md) · [安装与编译](docs/getting-started/quickstart.md) |
| 接口调用 · API usage | [接口工具](docs/api/interfaces.md) · [自定义消息包](docs/api/custom-messages.md) |
| 运动与关节 · Motion and joints | [运动控制](docs/dev-guide/motion-control.md) · [关节调试](docs/dev-guide/debug.md) |
| 应用开发 · Application development | [Python](docs/dev-guide/python.md) · [C++](docs/dev-guide/cpp.md) · [二次开发手册](docs/dev-guide/secondary-development.md) |
| 联调验证 · Integration | [开机自检](docs/testing/boot-check.md) · [仿真](docs/testing/simulation.md) · [实机](docs/testing/real-robot.md) |
| 问题排查 · Troubleshooting | [常见问题](docs/troubleshooting/common-errors.md) |

本地预览文档 · Preview documentation locally:

```bash
python3.11 -m venv .venv-docs
source .venv-docs/bin/activate
python -m pip install -r requirements.txt
python -m mkdocs serve
```

默认地址为 `http://127.0.0.1:8000/`。运行 `python -m mkdocs build --strict` 检查文档。文档构建独立于 ROS 2，Read the Docs 接入、Webhook、PR 预览与版本管理见[部署指南](docs/deployment.md)。正式站点地址以维护者配置的 RTD 项目为准。

The default preview address is `http://127.0.0.1:8000/`. Validate the site with `python -m mkdocs build --strict`. Documentation builds do not require ROS 2. See the [deployment guide](docs/deployment.md) for Read the Docs setup, webhooks, PR previews and versions. The public documentation address is determined by the configured RTD project.

## 版本兼容 · Compatibility

接口已对照 `hl_motion/main` 提交 `c3b2902`（2026-09-07）及其消息子模块 `3228d83` 核对。23 个公共定义一致，另保留 `ActionPlay`、`SwitchMode` 两个历史扩展。标准全身 Topic 使用 `sensor_msgs/msg/JointState`；带增益的 Topic 使用 `/motion/debug/` 前缀。

The interfaces were checked against `hl_motion/main` commit `c3b2902` (2026-09-07) and its message submodule `3228d83`. All 23 shared definitions match; `ActionPlay` and `SwitchMode` remain as legacy SDK extensions. Standard whole-body topics use `sensor_msgs/msg/JointState`; topics carrying PD gains use the `/motion/debug/` prefix.

```bash
python3 scripts/check_runtime_contract.py --motion /path/to/hl_motion
```

`VoicePlay.action` 是可选配套接口，未包含在本仓库。验证范围及服务端限制见[兼容性说明](docs/about/compatibility.md)。编译和离线检查不能替代 MuJoCo／实机运动验收。

`VoicePlay.action` is an optional runtime interface and is not included in this repository. See [Compatibility](docs/about/compatibility.md) for validation scope and runtime limitations. Build and offline checks do not replace simulation or physical robot acceptance tests.

---

[更新记录 · Changelog](CHANGELOG.md) · [操作安全 · Safety](SAFETY.md) · [安全问题 · Security](SECURITY.md) · [许可证 · License](LICENSE)
