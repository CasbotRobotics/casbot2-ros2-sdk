# C++ 示例

从 SDK 根目录构建依赖和示例：

```bash
source /opt/ros/humble/setup.bash
colcon build --packages-up-to casbot2_cpp_demo
source install/setup.bash
ros2 run casbot2_cpp_demo monitor_topics_demo
```

源码位于 [`examples/casbot2_cpp_demo/src/`](https://github.com/CasbotRobotics/casbot2-ros2-sdk/tree/main/examples/casbot2_cpp_demo/src)。

| 入口 | 用途 |
| --- | --- |
| `monitor_topics_demo` | 订阅关节、IMU 等状态 |
| `service_mode_demo` | 查询与切换模式 |
| `basic_control_demo` | 导航速度发布与停止 |
| `debug_joint_demo` | 进入上身调试并发送关节指令 |
| `action_voice_demo` | 触发技能、语音服务和动作 |

除监听示例外，其他入口会改变机器人状态或发送指令。请先阅读[运控接口参考](motion-control.md)。

## 在自己的包中引用

`package.xml` 声明实际使用的依赖，例如：

```xml
<depend>rclcpp</depend>
<depend>crb_ros_msg</depend>
```

`CMakeLists.txt` 中查找并链接依赖：

```cmake
find_package(rclcpp REQUIRED)
find_package(crb_ros_msg REQUIRED)
ament_target_dependencies(your_target rclcpp crb_ros_msg)
```

更完整的包配置见[自定义消息包使用指南](../api/custom-messages.md)。
消息字段见[接口类型参考](../api/messages.md)，分步调用验证见[Workflow 测试](../testing/workflow.md)。

## C++ / Python 调用对照

| 属性 | 值 |
| --- | --- |
| 创建客户端 | C++ `create_client<ServiceT>`；Python `create_client(ServiceT, name)` |
| 等待服务 | C++ `wait_for_service`；Python `wait_for_service` |
| 异步请求 | C++ `async_send_request`；Python `call_async` |
| 等待响应 | 两者均使用 `spin_until_future_complete`，然后检查结果 |
| 发布消息 | C++ `publisher->publish`；Python `publisher.publish` |
| Action | C++ `rclcpp_action`；Python `rclpy.action` |

## 代码解读：基础控制

节点在构造时创建客户端和发布者，导航模式切换检查服务响应，速度和关节控制分别构造对应消息。

!!! danger "该示例发送控制指令"
    先确认前置模式、安全员和急停条件。

```cpp
--8<-- "examples/casbot2_cpp_demo/src/basic_control_demo.cpp"
```
