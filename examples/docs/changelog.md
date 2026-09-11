# 版本变更记录

## Unreleased

### SDK 目录与命令迁移

根目录现在直接包含 `crb_ros_msg`、`casbot2_cpp_demo`、`casbot2_py_demo`、`casbot2_tools`、`casbot2_cpp_tests`、`casbot2_py_tests` 六个 ROS 2 包。
删除旧 `examples/` 和 `packages/` 层级。升级后应使用新的干净构建目录，避免旧 CMake 缓存和旧包入口残留。

| 旧入口 | 新入口 |
| --- | --- |
| Python `control_demo` | `ros2 run casbot2_py_demo basic_control_demo` |
| `all_interfaces_demo.py` | `ros2 run casbot2_tools interface_cli` |
| C++ `casbot_cpp_test` 包 | `casbot2_cpp_tests` 包 |
| Python 独立 workflow 脚本 | `casbot2_py_tests` 包的同名 console script |
| `t01_get_state` | `get_state_test` |
| `t02_switch_mode` | `switch_mode_test` |
| `t03_joint_states` | `joint_states_test` |
| `t04_cmd_vel` | `cmd_vel_test` |
| `t05_upper_debug` | `upper_body_debug_test` |
| `test_flow1_walk` | `test_walk_flow` |
| `test_flow2_upper_debug` | `test_upper_body_flow` |
| `test_flow3_whole_body` | `test_whole_body_flow` |
| `test_flow4_sensors_and_actions` | `test_sensors_and_actions_flow` |
| `test_flow_debug_kp_kd` | `test_kp_kd_debug` |
| `test_joint_states_kp_kd` | `test_kp_kd_joint_states` |
| `test_wbd_action_play` | `test_action_play_flow` |

### 接口与清理

- 已注册的 25 个 msg / srv / action 定义原样迁移，字段不变。
- 删除误复制的 `FaultRecord copy.msg` 与无人引用的 `common_function.cpp/.hpp`。
- `HlArmState` 与 `ArmState` 内容相同，但都已在 CMake 中导出，保留两个类型名以保持兼容。
- `RunBehaviorTree.msg` 没有 CMake 注册或仓库内引用，原文件还含无效类型声明；保留供维护者确认，不新增导出，也不把它列为可用接口。仓库外使用情况尚未确认。
- 修复 C++ 服务客户端模板参数推导错误。
- `VoicePlay` 缺失时不再阻止基础示例编译和 CLI 帮助；使用可选音频 Action 时明确说明依赖。
- `ActionEvent` 和 `Voice` 示例按实际 `error_code` / `msg` 字段读取响应。

### 文档与工程

- 按概述、快速开始、接口参考、开发指南、联调测试、故障排查重组文档。
- 增加 MkDocs Material、Mermaid、中文分词搜索、接口源文件生成、RTD 配置和文档 CI。
- 增加统一环境、构建、离线测试及仿真命令启动入口。
- 新增安全操作说明及安全问题处理说明。

### 待外部环境接入

仿真 Binary／镜像的下载地址和专用启动命令需交付团队提供；RTD 项目导入、Webhook 和正式域名需在托管平台完成。
上述外部资源尚未包含在本仓库，本版本不宣称完成真机或仿真验证。

## 对照 hl_motion main 的修正（2026-09-11）

- 锁定运控 `c3b2902` 与消息子模块 `3228d83`，23 个公共定义逐字节一致；保留 2 个 SDK 历史扩展。
- 分离标准 `/motion/joint_*` 和自定义增益 `/motion/debug/joint_*`，修正错误的 `/joint_states` 类型订阅。
- 导航使用 `/motion/switch_nav_mode`，退出到 IDLE_MODE；补齐并行导航上身调试与上身速度入口。
- 修正状态映射、完整关节名、紧凑增益回读；反馈需在正确模式下检查。
- 控制前检查服务结果，完整流程不再自动 ZERO 复位；基础导航示例补发停止，调试示例使用实测姿态。
- CLI 增加 doctor、输入检查、DDS 发现等待、错误退出码、Action 结果及取消请求处理。
- Action 示例每次执行单一操作，避免事件入口与直接 Action 重复触发；增益测试改为只读回读。
- 记录底层导航超时、缓存优先级和 Action 反馈限制；新增可复现的源码契约核查脚本。

- 修正 Python 包的构建依赖：`ament_python` 仅为构建类型，依赖声明改为可解析的 `python3-setuptools`，支持干净环境 `rosdep install`。

## 仓库层级整理 / Repository layout

- 根目录保留 `crb_ros_msg/`；五个配套包统一迁入 `examples/`，与接口包并列展示。
- 新增 `examples/README.md` 导航，根 README 改为逐节中英对照，保留现有使用说明。
- 同步文档源码引用、依赖安装路径、测试源码定位与 CI 路径；ROS 包名、入口和接口定义保持不变。

The interface package stays at the root, while examples, tools and test packages move under `examples/`.
Package names, executables and interface definitions remain unchanged. README sections are presented in Chinese and English.

## 精简仓库首页与语言切换

- 根目录仅保留 `examples/`、`crb_ros_msg/`、`README.md` 和 `LICENSE`。
- 文档归入 `examples/docs/`，YAML、JSON 与文档依赖归入 `examples/config/`，脚本归入 `examples/scripts/`。
- 不再跟踪隐藏配置文件；工作流以普通模板保存，不自动运行 GitHub Actions。
- README 按中文版、英文版分为完整的两个区块，顶部提供互相跳转的语言链接。
- 同步文档构建配置、脚本路径与契约文件位置，接口定义及客户端实现不变。
