# CASBOT2 ROS 2 SDK

CASBOT2 人形机器人的 ROS 2 二次开发 SDK，提供自定义消息、服务和动作定义，以及 Python、C++ 示例和联调文档。

[安装与编译](getting-started/quickstart.md){ .md-button .md-button--primary }
[运控接口参考](dev-guide/motion-control.md){ .md-button }

## 从这里开始

| 目标 | 阅读入口 |
| --- | --- |
| 第一次接入机器人 | [安装与编译](getting-started/quickstart.md) → [开机自检](testing/boot-check.md) |
| 查询状态、切换模式、控制关节 | [运控接口与调用时序](dev-guide/motion-control.md) |
| 查找消息字段 | [消息](api/messages.md) · [服务](api/services.md) · [动作](api/actions.md) |
| 编写应用 | [Python 示例](dev-guide/python.md) · [C++ 示例](dev-guide/cpp.md) |
| 使用语音、技能、传感器与头显 | [二次开发手册](dev-guide/secondary-development.md) |
| 验证完整调用流程 | [Workflow 测试](testing/workflow.md) |

## SDK 组成

| 路径 | 内容 |
| --- | --- |
| `crb_ros_msg/` | ROS 2 自定义 msg / srv / action |
| `examples/casbot2_py_demo/` | Python 示例包 |
| `examples/casbot2_cpp_demo/` | C++ 示例包 |
| `examples/casbot2_tools/` | 接口命令行调用工具 |
| `examples/casbot2_cpp_tests/`、`examples/casbot2_py_tests/` | 需要仿真或实机服务的流程验证程序 |
| `docs/` | 开发文档与在线站点内容 |

SDK 面向 **Ubuntu 22.04 + ROS 2 Humble**。机器人主程序、MuJoCo 仿真程序和模型资源需由配套软件提供；编译本仓库不会启动机器人服务。

首次接入建议先执行状态查询与数据订阅。运动类示例会发送控制指令，请先阅读运控参考中的前置模式和操作顺序。

## 文档来源与维护

原有四份手册已迁入分主题目录，图片统一保留在 `docs/images/`。在线文档沿用
[个人 demo](https://github.com/ElvinChan777/casbot02-docs) 的 MkDocs Material 阅读方式，
示例与接口字段从本 SDK 仓库取源。构建、预览和 Read the Docs 接入见[文档维护](deployment.md)。
