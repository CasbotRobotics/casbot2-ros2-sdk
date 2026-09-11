# Python 示例

从 SDK 根目录构建依赖和示例：

```bash
source /opt/ros/humble/setup.bash
colcon build --packages-up-to casbot2_py_demo
source install/setup.bash
ros2 run casbot2_py_demo monitor_topics_demo
```

源码位于 [`casbot2_py_demo/casbot2_py_demo/`](https://github.com/CasbotRobotics/casbot2-ros2-sdk/tree/main/casbot2_py_demo/casbot2_py_demo)。

| 入口 | 用途 |
| --- | --- |
| `monitor_topics_demo` | 订阅关节、IMU 等状态 |
| `service_mode_demo` | 查询与切换模式 |
| `basic_control_demo` | 导航速度发布与停止 |
| `debug_joint_demo` | 进入上身调试并发送关节指令 |
| `action_voice_demo` | 触发技能、语音服务和动作 |

除监听示例外，其他入口会改变机器人状态或发送指令。前置条件见[运控接口参考](motion-control.md)。
音频 Action 的额外依赖见[版本兼容性](../about/compatibility.md)。

## 接口调用模式

Service 客户端通常依次执行 `create_client`、`wait_for_service`、`call_async`、`spin_until_future_complete`。
应检查等待结果、超时及服务响应，再执行后续步骤。

Topic 使用 `create_publisher` 和 `create_subscription`，消息字段需与[当前消息定义](../api/messages.md)一致。
Action 使用 `rclpy.action.ActionClient`，区分目标是否被接受、执行反馈和最终结果。

更多单项调用可在仓库根目录执行：

```bash
ros2 run casbot2_tools interface_cli --help
ros2 run casbot2_tools interface_cli get_robot_mode
ros2 run casbot2_tools interface_cli sub_motion_joint_state --seconds 5
```

## 代码解读：基础控制

`BasicControlDemo` 创建导航切换 Service 客户端、速度发布者。
服务调用等待响应后再决定是否继续；消息通过扁平字段赋值。完整源码如下。

!!! danger "该示例发送控制指令"
    先确认机器人模式及操作安全条件。首次接入优先使用监听入口。

```python
--8<-- "casbot2_py_demo/casbot2_py_demo/basic_control_demo.py"
```
