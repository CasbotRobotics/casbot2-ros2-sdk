# CASBOT2 ROS 2 SDK

中文 | [English](#english)

CASBOT2 人形机器人官方 ROS 2 二次开发 SDK，面向 **Ubuntu 22.04 + ROS 2 Humble**。
提供消息接口、C++ / Python 示例、接口工具和仿真／实机联调流程。

## 安装与编译

```bash
git clone https://github.com/CasbotRobotics/casbot2-ros2-sdk.git
cd casbot2-ros2-sdk
source /opt/ros/humble/setup.bash
rosdep install --from-paths crb_ros_msg casbot2_cpp_demo casbot2_py_demo casbot2_tools casbot2_cpp_tests casbot2_py_tests --ignore-src --rosdistro humble -r -y
colcon build
source install/setup.bash
```

`rosdep` 应已完成初始化及更新。仓库根目录包含 6 个标准 ROS 2 包，直接 `colcon build` 即可发现并构建全部包。

## 包与入口

| 包 | 职责 | 示例入口 |
| --- | --- | --- |
| `crb_ros_msg` | msg / srv / action 接口定义 | `ros2 interface show crb_ros_msg/msg/JointStateData` |
| `casbot2_cpp_demo` | C++ 基础示例 | `ros2 run casbot2_cpp_demo monitor_topics_demo` |
| `casbot2_py_demo` | Python 基础示例 | `ros2 run casbot2_py_demo monitor_topics_demo` |
| `casbot2_tools` | 全接口命令行工具 | `ros2 run casbot2_tools interface_cli --help` |
| `casbot2_cpp_tests` | C++ 分步联调程序 | `ros2 run casbot2_cpp_tests get_state_test` |
| `casbot2_py_tests` | Python 分步／流程联调与离线回归 | `ros2 run casbot2_py_tests get_state_test` |

`docs/` 放文档，`scripts/` 放环境加载、构建和测试入口。文件迁移与命令更名见 [CHANGELOG](CHANGELOG.md)。

## 首次连接

SDK 不包含机器人主程序、MuJoCo Binary、Docker 镜像或模型资源。
请向对应机器人交付／仿真团队获取匹配版本的仿真包及其启动命令。
当前仓库尚无经确认的下载地址与专用 launch 文件，详见[仿真快速开始](docs/getting-started/sim.md)。

仿真与实机使用同一套 SDK 和环境加载方式；通信目标由运行中的服务、网络与 DDS 域决定。

```bash
# 示例域号；必须与目标服务配置一致
export ROS_DOMAIN_ID=72
# 跨机器／跨容器网络通信使用 0；纯本机隔离可使用 1
export ROS_LOCALHOST_ONLY=0
source scripts/setup_env.sh
ros2 run casbot2_tools interface_cli get_robot_mode
```

仿真包给出启动命令后，可通过 `bash scripts/start_sim.sh <程序> [参数...]` 加载同一 SDK 环境并启动该程序。
Docker 启动时还需按交付说明将 DDS 环境变量与网络配置传入容器；宿主机环境不会自动传入容器。

首次联调先读取状态，再按[运控指南](docs/dev-guide/motion-control.md)执行模式切换与控制。
运动类示例会驱动机器人，请先阅读 [SAFETY.md](SAFETY.md)。
`VoicePlay.action` 是配套软件的可选接口，本仓库未包含；缺少时不影响其他示例，音频命令会明确报错。

## 辅助脚本

```bash
source scripts/setup_env.sh
bash scripts/build.sh
bash scripts/test.sh
```

`test.sh` 只执行不创建 ROS 节点的离线回归。联调／运动流程通过 `ros2 run` 手动运行。
更多步骤见[Workflow 测试](docs/testing/workflow.md)。安全问题处理方式见 [SECURITY.md](SECURITY.md)。

## 在线文档

[文档首页](docs/index.md) · [环境准备](docs/getting-started/environment.md) · [接口工具](docs/api/interfaces.md)

```bash
python3.11 -m venv .venv-docs
source .venv-docs/bin/activate
python -m pip install -r requirements.txt
python -m mkdocs serve
```

文档构建独立于 ROS 2，Python 3.11+；默认预览地址为 `http://127.0.0.1:8000/`。
`python -m mkdocs build --strict` 执行构建检查。
RTD Community 接入、Webhook、PR 预览和版本说明见[部署指南](docs/deployment.md)。
正式站点 URL 以维护者完成 RTD 项目接入后的地址为准。

## English

CASBOT2 ROS 2 SDK targets Ubuntu 22.04 and ROS 2 Humble. Clone the repository,
source ROS 2, install dependencies with `rosdep`, then run `colcon build` from the root.
All six ROS packages are located directly at the repository root.

Use `ros2 run casbot2_tools interface_cli --help` for the CLI and
`ros2 run casbot2_py_demo monitor_topics_demo` for a read-only example.
Python's control entry is now `basic_control_demo`; integration executables use functional names
such as `get_state_test` in `casbot2_cpp_tests` and `casbot2_py_tests`.

Simulation binaries and robot runtime software are distributed separately by the delivery team.
Match `ROS_DOMAIN_ID` to the target and use `ROS_LOCALHOST_ONLY=0` across machines.
The same SDK environment loader serves both simulation and real robots.
Read [SAFETY.md](SAFETY.md) before running motion examples.

`bash scripts/test.sh` runs offline tests only. Documentation builds use Python 3.11+,
`requirements.txt`, and MkDocs; see the [documentation maintenance guide](docs/deployment.md).

## 当前运控核对基准 / Runtime baseline

已对照 `hl_motion/main` 的 `c3b2902`（2026-09-07）及其消息子模块 `3228d83` 核对接口。
23 个公共定义一致，另保留 `ActionPlay`、`SwitchMode` 两个历史扩展。
标准全身 Topic 使用 `sensor_msgs/JointState`；带增益的 Topic 使用 `/motion/debug/` 前缀。

```bash
python3 scripts/check_runtime_contract.py --motion /path/to/hl_motion
ros2 run casbot2_tools interface_cli doctor
```

验证范围和服务端限制见 [兼容性](docs/about/compatibility.md) 与 [运动控制](docs/dev-guide/motion-control.md)。
本地编译与离线检查不替代 MuJoCo / 实机运动验收。
