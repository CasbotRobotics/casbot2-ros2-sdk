# 环境准备

## 依赖与统一环境

SDK 运行环境为 Ubuntu 22.04、ROS 2 Humble 及配套 Python / C++ 工具链；在线文档使用独立的 Python 3.11+ 环境。
安装 ROS 2、colcon、rosdep 后，在 SDK 根目录加载环境：

```bash
source examples/scripts/setup_env.sh
```

仿真和实机使用同一脚本。默认加载 `/opt/ros/humble/setup.bash`，并在存在时加载本 SDK 的 `install/setup.bash`。
可用 `CASBOT_RUNTIME_SETUP` 显式指定交付软件的环境脚本；路径必须真实存在，不会自动猜选其他工作区。
`CASBOT_ROS_SETUP` 和 `CASBOT_SDK_SETUP` 可用于指定自定义安装位置。

## DDS 通信隔离

| 属性 | 值 |
| --- | --- |
| `ROS_DOMAIN_ID` | 客户端和目标服务必须一致；72 仅为示例，按部署配置设置 |
| `ROS_LOCALHOST_ONLY=1` | 限制同机通信；不适用于跨设备接入 |
| `ROS_LOCALHOST_ONLY=0` | 允许跨设备发现，仍需网络和 DDS 配置正确 |

```bash
export ROS_DOMAIN_ID=72
export ROS_LOCALHOST_ONLY=0
source examples/scripts/setup_env.sh
```

仿真与实机同时开启时应使用不同通信域，并让客户端明确加入目标域。
容器需要显式传入环境变量并配置 DDS 所需网络；仅在宿主机 export 不会修改运行中容器。
修改 DDS 配置后，必要时重新启动 ROS 2 CLI daemon，再检查发现结果：

```bash
ros2 daemon stop
ros2 doctor --report
ros2 topic list -t
ros2 service list -t
```

## 验证接口包

```bash
ros2 pkg prefix crb_ros_msg
ros2 interface show crb_ros_msg/msg/UpperJointData
ros2 interface show crb_ros_msg/srv/GetRobotMode
```

找不到接口时按[安装编译](quickstart.md)操作；目标服务不可见时查[故障排查](../troubleshooting/common-errors.md)。
