# SDK 简介

CASBOT2 ROS 2 SDK 为二次开发者提供接口类型、客户端示例、命令行工具和联调程序。
六个包可从仓库根目录一起构建，消息定义、示例、工具和测试分别维护。

| 包 | 构建类型与职责 |
| --- | --- |
| `crb_ros_msg` | ament_cmake，25 个已注册消息／服务／动作接口 |
| `casbot2_cpp_demo` | ament_cmake，C++ 示例 |
| `casbot2_py_demo` | ament_python，Python 示例 |
| `casbot2_tools` | ament_python，`interface_cli` 命令行工具 |
| `casbot2_cpp_tests` | ament_cmake，5 个分步联调入口 |
| `casbot2_py_tests` | ament_python，12 个联调入口及离线回归检查 |

新用户从[安装编译](../getting-started/quickstart.md)开始，应用开发者查阅[接口总览](overview.md)，
运控开发者重点阅读[运动控制](../dev-guide/motion-control.md)。机器人主程序和仿真软件需要单独获取。
