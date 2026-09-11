# 安装与编译

## 1. 准备环境

使用 Ubuntu 22.04 和 ROS 2 Humble，安装 ROS 2 开发工具后，在终端加载环境：

```bash
source /opt/ros/humble/setup.bash
```

需要 `colcon`、`rosdep`、C++ 编译工具和 Python。`rosdep` 应已完成初始化及更新。
机器人运行环境的初始化命令见[环境速查](environment.md)。

## 2. 获取 SDK 并安装依赖

```bash
git clone https://github.com/CasbotRobotics/casbot2-ros2-sdk.git
cd casbot2-ros2-sdk
rosdep install --from-paths crb_ros_msg examples --ignore-src --rosdistro humble -r -y
```

后续命令均在 **SDK 仓库根目录**执行。接口包位于 `crb_ros_msg/`，其余 5 个包位于 `examples/`；`colcon` 递归发现全部 6 个包。

## 3. 构建

```bash
colcon build
source install/setup.bash
```

如果只需要接口定义：

```bash
colcon build --packages-select crb_ros_msg
source install/setup.bash
```

验证生成结果：

```bash
ros2 interface show crb_ros_msg/msg/JointStateData
ros2 interface show crb_ros_msg/srv/GetRobotMode
ros2 pkg executables casbot2_py_demo
ros2 pkg executables casbot2_cpp_demo
```

## 4. 连接目标并查询状态

先启动配套仿真或机器人服务，并确保通信域与目标一致。跨设备连接时不能使用 `ROS_LOCALHOST_ONLY=1`。

```bash
ros2 service list
ros2 service call get_robot_mode crb_ros_msg/srv/GetRobotMode '{}'
ros2 topic echo /joint_states --once
```

首个 Python / C++ 示例可以选择只订阅数据的节点：

=== "Python"

    ```bash
    ros2 run casbot2_py_demo monitor_topics_demo
    ```

=== "C++"

    ```bash
    ros2 run casbot2_cpp_demo monitor_topics_demo
    ```

## 5. 接口命令行工具

```bash
ros2 run casbot2_tools interface_cli --help
ros2 run casbot2_tools interface_cli get_robot_mode
```

完整命令见[接口调用工具](../api/interfaces.md)。运动控制前先完成[开机自检](../testing/boot-check.md)，再按[运控参考](../dev-guide/motion-control.md)的模式顺序操作。
