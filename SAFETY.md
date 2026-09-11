# 机器人操作安全 / Robot Safety

本 SDK 的模式切换、速度发布、关节调试、动作播放和 workflow 程序会改变机器人状态或产生真实运动。

## 运行前

- 确认设备固定／支撑方式符合交付操作规程，运动区域内没有人员和障碍物。
- 确认急停装置可用，并安排熟悉设备的安全员在场。
- 核对 DDS 域、目标 IP、模式与软件版本，避免同时连接仿真和实机。
- 先运行状态查询或监听示例，再使用低速、小幅度指令逐步联调。
- 调试前核对关节名称、位置数组和增益；不将其他机器人或固件版本的参数直接用于当前设备。

## 运行中

- 严格遵守运控指南的模式切换顺序，不在前置服务失败或超时后继续发送运动指令。
- 监视关节状态、故障状态和实际动作，异常时按交付规程使用急停。
- 终止脚本或发送一次零速度不能替代硬件急停。不要假设断网后控制器一定自行停止。
- workflow 文件即使名称包含 `test`，也可能驱动机器人；不得自动对实机执行整套测试。

## 本仓库的离线检查

`scripts/test.sh` 只执行不创建 ROS 节点的回归检查，不启动仿真、不连接实机、不发送控制指令。
运动流程通过 `ros2 run casbot2_cpp_tests ...` 或 `ros2 run casbot2_py_tests ...` 显式运行。

## English

Motion examples and integration workflows can move a real robot. Confirm emergency stop,
physical support, a trained safety operator, and a clear workspace before execution.
Check the DDS target and software version, begin with state monitoring, and follow the documented
mode sequence using low speed and small motion ranges. Stopping a client process is not an emergency stop.
