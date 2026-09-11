# 常见问题

## 找不到 crb_ros_msg

在 SDK 根目录构建接口包，并在使用它的每个终端加载环境：

```bash
source /opt/ros/humble/setup.bash
colcon build --packages-select crb_ros_msg
source install/setup.bash
ros2 interface show crb_ros_msg/msg/JointStateData
```

如已加载其他工作区，使用 `ros2 pkg prefix crb_ros_msg` 确认当前命中的包，核对是否与机器人使用的版本一致。

## VoicePlay 导入失败

本仓库不包含该 Action 定义。音频播放依赖配套软件提供的兼容接口包；详细说明见[版本兼容性](../about/compatibility.md)。
不要用不完整的定义替代机器人侧协议。

## 服务或话题不可见

SDK 是客户端与接口定义，不会启动目标服务。先确认仿真或机器人主程序正在运行，
再核对两端的网络、`ROS_DOMAIN_ID` 和 `ROS_LOCALHOST_ONLY`。跨设备通信不能设置 `ROS_LOCALHOST_ONLY=1`。

```bash
ros2 topic list -t
ros2 service list -t
ros2 action list -t
```

类型或名称与手册不一致时，以当前目标程序和匹配的接口包为准。

## 字段 joint 不存在或消息类型不匹配

当前 `UpperJointData` 使用扁平数组字段；`/motion/debug/joint_cmd` 使用 `JointStateData`。
旧版嵌套字段或 `sensor_msgs/msg/JointState` 控制指令不能直接套用。
请对照[消息定义](../api/messages.md)和[运控参考](../dev-guide/motion-control.md)修正。

## 文档构建失败

使用独立 Python 环境安装 `requirements.txt`，从仓库根目录执行 `python -m mkdocs build --strict`。
缺失页面、图片和锚点会使构建失败；根据日志修正源文件，不要通过忽略错误跳过检查。
详细流程见[文档维护](../deployment.md)。

## colcon build 失败或仍出现旧包

目录迁移后旧构建目录会记录过时的源路径。请使用新的干净工作区重新构建，或先备份再移走旧 `build/`、`install/`、`log/`。
`colcon list` 应只列出根目录的六个包。不要从同时包含旧版源码副本的上级目录构建。
缺少依赖时按安装指南执行 `rosdep install`，不要把文档用的 Python 环境混入 ROS 2 构建终端。

## Python 找不到入口

先 `source install/setup.bash`，再用 `ros2 pkg executables casbot2_py_demo` 或 `ros2 pkg executables casbot2_py_tests` 检查。
Python 基础控制已更名为 `basic_control_demo`；流程文件名与 `ros2 run` 入口见[版本说明](../changelog.md)。

## 话题没有数据／服务无响应

确认目标程序实际启动了发布者或服务端，使用 `ros2 topic info <话题> --verbose` 检查类型、发布者和 QoS。
服务可发现但无响应时，检查服务端日志、当前模式和参数；不要在超时后继续发送控制指令。

## 仿真无法连接或 DDS 混连

核对宿主机与容器的域号、网络配置和 `ROS_LOCALHOST_ONLY`；重新检查 CLI daemon 的发现结果。
若能看到两套同名服务，停止客户端并隔离仿真与实机域后重试。
仿真启动本身失败时，需要使用该版本仿真包的日志和启动说明，SDK 无法补齐未安装的 Binary／模型资源。
