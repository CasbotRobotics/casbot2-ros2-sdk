# 实机快速开始

!!! danger "实机会产生运动"
    确认急停可用、安全员在场、设备支撑与场地符合交付规程。首次接入只做查询与订阅，不直接运行完整运动流程。

## 上电与网络

按设备交付规程完成上电和基础进程启动。SDK 本身不会启动机器人服务。
核对客户端与机器人网络、DDS 域、软件版本；跨设备使用 `ROS_LOCALHOST_ONLY=0`。

```bash
export ROS_DOMAIN_ID=72  # 必须替换为目标机器人的实际域号
export ROS_LOCALHOST_ONLY=0
source examples/scripts/setup_env.sh
```

## 查询与观测

```bash
ros2 service list -t
ros2 run casbot2_tools interface_cli get_robot_mode
ros2 run casbot2_tools interface_cli get_robot_state
ros2 run casbot2_py_demo monitor_topics_demo
```

也可运行 `ros2 run casbot2_cpp_demo monitor_topics_demo`，用同一接口观察数据。
查询失败、数据异常或控制域不确定时，不进入运动测试。

接下来执行[开机自检](../testing/boot-check.md)，再按[实机联调](../testing/real-robot.md)的顺序验证。
