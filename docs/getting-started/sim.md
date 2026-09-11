# 仿真快速开始

## 获取仿真环境

本 SDK 不包含 MuJoCo Binary、Docker 镜像、URDF 或运控主进程。请从对应机器人交付／仿真团队获取相互匹配的程序与模型资源。
目前没有经确认可公开的镜像名、下载地址和专用 launch 命令，不能把 demo 中的注释当作可用启动命令。

需要交付团队提供：Binary／镜像版本与获取地址、MuJoCo 和 `hlorin` 的启动命令、所需模型路径，以及容器的 DDS 网络配置。

## 启动与连接

1. 完成[安装编译](quickstart.md)，按仿真包说明配置模型与依赖。
2. 按[环境准备](environment.md)设置仿真服务与客户端相同的 DDS 域。
3. 使用交付团队提供的实际命令启动仿真与 `hlorin`。

仓库提供统一环境启动入口：

```bash
bash scripts/start_sim.sh --help
```

其调用形式是 `bash scripts/start_sim.sh <真实程序路径> [参数...]`，仅加载 SDK 环境并执行传入命令。
它不提供或下载仿真程序。若启动 Docker，环境变量和网络参数仍需按镜像说明显式传入容器。

## 通信验证与首个示例

```bash
source scripts/setup_env.sh
ros2 service list -t
ros2 run casbot2_tools interface_cli get_robot_mode
ros2 run casbot2_py_demo monitor_topics_demo
```

确认数据和模式正常后，按[仿真联调](../testing/simulation.md)逐项执行流程。
部分仿真动作可能因腿部锁定或资源缺失而失败，接口是否可用以当前发布版本为准。
RL 的 sim2sim 和实机过渡见[仿真到实机](../dev-guide/sim-to-real.md)。
