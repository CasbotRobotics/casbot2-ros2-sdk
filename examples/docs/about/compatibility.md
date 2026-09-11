# 版本兼容性

## 运行环境

| 项目 | 要求 |
| --- | --- |
| 操作系统 | Ubuntu 22.04 |
| ROS 2 | Humble |
| Python 示例 | ROS 2 Humble 配套 Python 环境 |
| 接口包 | 与目标机器人软件匹配的 `crb_ros_msg` |
| 文档构建 | Python 3.11+，无需安装 ROS 2；CI 和 Read the Docs 使用 3.11 |

升级时记录 SDK 的 Git 提交号和机器人软件版本。当前仓库没有提供经过验证的 SDK／固件版本矩阵，不能仅根据分支名判断兼容性。

## 消息定义

`UpperJointData` 和 `JointStateData` 使用扁平的 `name`、`position`、`velocity`、`effort`、`kp`、`kd` 数组。
旧版嵌套 `joint` 字段的示例不适用于本仓库。接口的完整定义见[消息类型](../api/messages.md)。

ROS 2 通信双方需要匹配的接口定义。增加字段也会改变消息结构，不能默认与旧版二进制兼容。
更新接口后应重新编译依赖它的程序，并在仿真环境核对类型和服务响应。

## 可选音频 Action

仓库提供 `Voice.srv`，但没有 `VoicePlay.action`。`/action_voice_play` 依赖配套机器人软件中的兼容定义。
使用前先检查：

```bash
ros2 interface show crb_ros_msg/action/VoicePlay
ros2 action list -t
```

不要用推测的 Result 或 Feedback 字段创建同名动作。缺少该定义时，仍可使用仓库自带的 `Voice` 服务和 `BasicActionPlay` 动作。

## 仿真与实机

先确认两端 `ROS_DOMAIN_ID`、接口类型及服务名称，再运行相同的客户端代码。
仿真程序和实机固件可能存在接口差异，动作资源也可能不同；具体以目标程序提供的接口为准。
参见[仿真联调](../testing/simulation.md)与[实机联调](../testing/real-robot.md)。

## 2026-09-11 main 核对

| 项目 | 基准 |
| --- | --- |
| hl_motion main | `c3b2902ea53f0267ae3ef12b2fdc178c7162ea54`（2026-09-07） |
| 锁定 crb_ros_msg | `3228d83f5629727eb2a8440bf9fd46c9f9fcedbf` |
| 公共接口 | 23 个导出定义逐字节一致 |
| SDK 历史扩展 | 额外保留 `ActionPlay.action`、`SwitchMode.srv`，不属于该运控基准 |
| 本地验证 | 六包编译、离线契约测试、文档严格构建 |
| 未验证 | 未执行机器人运动或完整 MuJoCo 联调；外部语音/技能服务与资源不在该源仓库验证范围 |

可重复运行源码契约核查（本地需有对应源仓库和消息子模块）：

```bash
python3 examples/scripts/check_runtime_contract.py --motion /path/to/hl_motion
```

脚本读取 Git 对象中的 main 基准与锁定子模块，不以工作目录未提交的改动为准。
在线只读检查使用 `ros2 run casbot2_tools interface_cli doctor`；ROS 图匹配不等于运动验收通过。

当前运控的导航断流处理、debug 命令缓存优先级、紧凑增益消费以及 Action 反馈限制见
[运动控制](../dev-guide/motion-control.md)。这些限制涉及运控服务端，SDK 修正客户端并明确记录，不能据此宣称底层问题已修复。
