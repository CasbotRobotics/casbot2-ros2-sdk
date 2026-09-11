# 开发示例与工具 · Examples and Tools

本目录集中收纳 CASBOT2 SDK 的示例、命令行工具及联调程序。ROS 2 接口定义独立维护在上一级的 [`crb_ros_msg/`](../crb_ros_msg/)。

This directory contains the SDK's examples, CLI tools and integration workflows. ROS 2 interface definitions are maintained separately in [`crb_ros_msg/`](../crb_ros_msg/).

## 目录导航 · Package Guide

| 目录 · Directory | 说明 · Description | 入门命令 · First command |
| --- | --- | --- |
| [casbot2_cpp_demo](casbot2_cpp_demo/) | C++ 客户端示例 · C++ client examples | `ros2 run casbot2_cpp_demo monitor_topics_demo` |
| [casbot2_py_demo](casbot2_py_demo/) | Python 客户端示例 · Python client examples | `ros2 run casbot2_py_demo monitor_topics_demo` |
| [casbot2_tools](casbot2_tools/) | 接口 CLI 与只读检查 · CLI and read-only checks | `ros2 run casbot2_tools interface_cli --help` |
| [casbot2_cpp_tests](casbot2_cpp_tests/) | C++ 分步联调 · C++ integration workflows | `ros2 run casbot2_cpp_tests get_state_test` |
| [casbot2_py_tests](casbot2_py_tests/) | Python 联调与离线回归 · Python workflows and offline regression | `ros2 run casbot2_py_tests get_state_test` |

## 编译与运行 · Build and Run

在**仓库根目录**运行以下命令，`colcon` 会同时发现接口包和本目录内的配套包。

Run these commands from the **repository root**. `colcon` discovers both the interface package and the packages in this directory.

```bash
source /opt/ros/humble/setup.bash
rosdep install --from-paths crb_ros_msg examples --ignore-src --rosdistro humble -y
colcon build
source install/setup.bash
```

只构建所需示例及其依赖 · Build a selected example and its dependencies:

```bash
colcon build --packages-up-to casbot2_py_demo
source install/setup.bash
ros2 run casbot2_py_demo monitor_topics_demo
```

## 示例分类 · Example Categories

| 入口 · Executable | 用途 · Purpose | 语言 · Language |
| --- | --- | --- |
| `monitor_topics_demo` | 只读监听关节与传感器 · Read-only joint and sensor monitoring | C++ / Python |
| `service_mode_demo` | 查询与切换模式 · Query and switch modes | C++ / Python |
| `basic_control_demo` | 导航速度发布与停止 · Navigation velocity and stopping | C++ / Python |
| `debug_joint_demo` | 上身／全身关节调试 · Upper-body / whole-body joint debugging | C++ / Python |
| `action_voice_demo` | 动作与语音调用 · Action and voice calls | C++ / Python |

首次连接建议先运行状态监听。运动类示例与联调程序会发送控制指令，前置条件见[运动控制](../docs/dev-guide/motion-control.md)和[操作安全](../SAFETY.md)。

Start with state monitoring. Motion examples and integration workflows send control commands; read the [motion control guide](../docs/dev-guide/motion-control.md) and [safety instructions](../SAFETY.md) first.

## 离线回归 · Offline Regression

```bash
bash scripts/test.sh
```

以上命令仍在仓库根目录运行，仅执行 `examples/casbot2_py_tests/test/` 中的离线检查，不自动执行机器人工作流。

Run this command from the repository root. It executes only the offline checks in `examples/casbot2_py_tests/test/`, without automatically running robot workflows.

[返回 SDK 首页 · Back to SDK](../README.md) · [Workflow 测试 · Workflow Tests](../docs/testing/workflow.md) · [接口工具 · Interface CLI](../docs/api/interfaces.md)
