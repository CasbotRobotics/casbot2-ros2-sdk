# ROS 2 运控接口参考



> **环境**：Ubuntu 22\.04 · ROS 2 Humble · 消息包 `crb_ros_msg`  
> 
> **接口来源**：基于 `hl_motion` 运控源码（`hl_orin/src/motion.cpp`、`hl_wbcfms/` 等）实测整理。
> 
> 



---



## 目录



1. 环境准备

2. 接口总览

3. 机器人模式说明

4. 使用流程与顺序

5. 接口详细说明

    - 5\.1 获取机器人模式

    - 5\.2 设置机器人模式

    - 5\.3 获取机器人状态

    - 5\.4 下肢行走控制（导航模式）

    - 5\.5 上身关节控制（上身调试模式）

    - 5\.6 全身关节控制（全身调试模式）

    - 5\.7 预设动作播放

    - 5\.8 传感器数据订阅

    - 5\.9 行走控制权切换（导航 / 遥控）

6. 关节名称速查表

---



## 1\. 环境准备



### 1\.1 ROS 2 环境初始化



在每个终端中按以下顺序 source（建议写入 `~/.bashrc`）：



```Bash
source /opt/ros/humble/setup.bash
source /workspace/prod_casbot02_basic/install/setup.bash 2>/dev/null || true
source /workspace/HLmotion/setup.bash 2>/dev/null || \
  source /workspace/hl_motion/setup.bash 2>/dev/null || true
```



### 1\.2 通信域隔离



```Bash
export ROS_DOMAIN_ID=72      # 多机同网，所有机器统一此值
export ROS_LOCALHOST_ONLY=1  # 单机调试，限制只通本机（二选一）
```



### 1\.3 验证环境



```Bash
ros2 doctor --report
ros2 topic list
ros2 service list | grep -E 'motion|robot_mode|robot_state'
```



---



## 2\. 接口总览



|类型|名称|消息/服务类型|方向|说明|
|---|---|---|---|---|
|Service|`get_robot_mode`|`crb_ros_msg/srv/GetRobotMode`|←|查询当前运动模式|
|Service|`/set_robot_mode`|`crb_ros_msg/srv/SetRobotMode`|→|切换运动模式|
|Service|`get_robot_state_srv_hl`|`crb_ros_msg/srv/GetRobotState`|←|获取运控状态|
|Service|`/motion/upper_body_debug`|`std_srvs/srv/SetBool`|→|进入/退出上身调试|
|Service|`/motion/whole_body_debug`|`std_srvs/srv/SetBool`|→|进入/退出全身调试|
|Service|`switch_teleoperation`|`std_srvs/srv/SetBool`|→|切换遥操作|
|Service|`switch_autonomous`|`std_srvs/srv/SetBool`|→|切换自主（动作播放）|
|Service|`/switch_drive_mode`|`std_srvs/srv/SetBool`|→|行走控制权切换（true=导航/false=遥控）|
|Topic|`/navigation/cmd_vel`|`geometry_msgs/msg/Twist`|→|行走速度指令|
|Topic|`/upper_body_debug/joint_cmd`|`crb_ros_msg/msg/UpperJointData`|→|上身关节指令|
|Topic|`/motion/joint_cmd`|`sensor_msgs/msg/JointState`|→|全身关节指令|
|Topic|`/joint_states`|`sensor_msgs/msg/JointState`|←|全身关节反馈|
|Topic|`/joint_control`|`sensor_msgs/msg/JointState`|←|运控输出镜像|
|Topic|`/imu`|`sensor_msgs/msg/Imu`|←|IMU 数据|
|Action|`basic_action_play`|`crb_ros_msg/action/BasicActionPlay`|→|预设动作（带反馈）|



---



## 3\. 机器人模式说明



|内部枚举|枚举值|`/set_robot_mode` 请求名|说明|
|---|---|---|---|
|`UNDEFINED`|0|—|上电初始|
|`DAMPING`|1|`"ZERO"`|阻尼/零力矩，关节软化|
|`READY`|2|`"STAND"`|站立模式|
|`ACTION_PLAY`|3|—|上身动作播放中|
|`TELEOPERATION`|4|—|遥操作|
|`IDLE_MODE`|5|`"WALK"`|行走/主模式|
|`NAVIGATION`|6|—|导航行走（`/navigation/cmd_vel` 生效）|
|`WHOLE_BODY_DEBUG`|7|—|全身调试（Service 进入）|
|`UPPER_BODY_DEBUG`|8|—|上身调试（Service 进入）|
|`WHOLE_BODY_ACTION_PLAY`|9|—|全身动作播放|



> **注意**：`get_robot_mode` 返回的整型 `mode` 不是枚举直接值。  
> 
> 规则：DAMPING/UNDEFINED → mode=2, name=`"ZERO"`；READY → mode=3, name=`"STAND"`；其余 → mode=4, name=`"WALK"`。
> 
> 



---



## 4\. 使用流程与顺序



### 各功能前提模式



|功能|需要的模式|进入方式|
|---|---|---|
|行走控制|`NAVIGATION`|手柄 RB\+A，或先 `WALK` 再由导航栈触发|
|上身关节控制|`UPPER_BODY_DEBUG`|Service `/motion/upper_body_debug true`|
|全身关节控制|`WHOLE_BODY_DEBUG`|Service `/motion/whole_body_debug true`|
|预设动作|`STAND` 或以上|直接调 Service/Action|



> ⚠️ **安全提示**：调试模式关节直接跟随指令，首次使用请在扶持/缓冲垫下操作，`vel_scale` 从 0\.05 开始。
> 
> 



---



## 5\. 接口详细说明



---



### 5\.1 获取机器人模式



|项|值|
|---|---|
|**类型**|Service|
|**名称**|`get_robot_mode`|
|**类型**|`crb_ros_msg/srv/GetRobotMode`|



**Request**：空（无需填写）



**Response**：



```Plain Text
int32  mode       # 2=ZERO, 3=STAND, 4=WALK（见第3节）
string mode_name  # "ZERO" / "STAND" / "WALK"
```



#### 命令行



```Bash
ros2 service call get_robot_mode crb_ros_msg/srv/GetRobotMode "{}"
```



#### C\+\+



```C++
#include <rclcpp/rclcpp.hpp>
#include <crb_ros_msg/srv/get_robot_mode.hpp>

auto node = rclcpp::Node::make_shared("get_mode_example");
auto client = node->create_client<crb_ros_msg::srv::GetRobotMode>("get_robot_mode");

// 等待 Service 可用
client->wait_for_service(std::chrono::seconds(5));

auto request = std::make_shared<crb_ros_msg::srv::GetRobotMode::Request>();
auto future = client->async_send_request(request);

if (rclcpp::spin_until_future_complete(node, future) ==
    rclcpp::FutureReturnCode::SUCCESS)
{
    auto resp = future.get();
    RCLCPP_INFO(node->get_logger(),
        "Mode: %d  Name: %s", resp->mode, resp->mode_name.c_str());
}
```



#### Python



```Python
import rclpy
from rclpy.node import Node
from crb_ros_msg.srv import GetRobotMode

rclpy.init()
node = Node('get_mode_example')
cli = node.create_client(GetRobotMode, 'get_robot_mode')
cli.wait_for_service(timeout_sec=5.0)

future = cli.call_async(GetRobotMode.Request())
rclpy.spin_until_future_complete(node, future)

resp = future.result()
print(f"Mode: {resp.mode}  Name: {resp.mode_name}")

node.destroy_node()
rclpy.shutdown()
```



---



### 5\.2 设置机器人模式



|项|值|
|---|---|
|**类型**|Service|
|**名称**|`/set_robot_mode`|
|**类型**|`crb_ros_msg/srv/SetRobotMode`|



**Request**：



```Plain Text
string mode_name  # "ZERO" / "STAND" / "WALK"
```



**Response**：



```Plain Text
bool success
```



**模式切换说明**：



|`mode_name`|切换目标|前提|
|---|---|---|
|`"ZERO"`|阻尼，关节软化|任意|
|`"STAND"`|站立，从 ZERO 切|当前为 ZERO|
|`"WALK"`|行走主模式|当前为 STAND|



#### 命令行



```Bash
# 站立
ros2 service call /set_robot_mode crb_ros_msg/srv/SetRobotMode "{mode_name: 'STAND'}"

# 切行走模式（导航/遥控准备）
ros2 service call /set_robot_mode crb_ros_msg/srv/SetRobotMode "{mode_name: 'WALK'}"

# 回零力矩（断电前安全退出）
ros2 service call /set_robot_mode crb_ros_msg/srv/SetRobotMode "{mode_name: 'ZERO'}"
```



#### C\+\+



```C++
#include <rclcpp/rclcpp.hpp>
#include <crb_ros_msg/srv/set_robot_mode.hpp>

// 封装为函数，node 已在外部创建
bool setRobotMode(rclcpp::Node::SharedPtr node, const std::string &mode_name)
{
    auto client = node->create_client<crb_ros_msg::srv::SetRobotMode>("/set_robot_mode");
    client->wait_for_service(std::chrono::seconds(5));

    auto req = std::make_shared<crb_ros_msg::srv::SetRobotMode::Request>();
    req->mode_name = mode_name;

    auto future = client->async_send_request(req);
    if (rclcpp::spin_until_future_complete(node, future) ==
        rclcpp::FutureReturnCode::SUCCESS)
    {
        bool ok = future.get()->success;
        RCLCPP_INFO(node->get_logger(),
            "SetRobotMode '%s' -> %s", mode_name.c_str(), ok ? "OK" : "FAILED");
        return ok;
    }
    return false;
}

// 使用示例：上电后站立
int main(int argc, char *argv[])
{
    rclcpp::init(argc, argv);
    auto node = rclcpp::Node::make_shared("set_mode_example");

    setRobotMode(node, "STAND");  // 站立
    rclcpp::sleep_for(std::chrono::seconds(3));
    setRobotMode(node, "WALK");   // 切行走

    rclcpp::shutdown();
    return 0;
}
```



#### Python



```Python
import rclpy
from rclpy.node import Node
from crb_ros_msg.srv import SetRobotMode
import time

rclpy.init()
node = Node('set_mode_example')
cli = node.create_client(SetRobotMode, '/set_robot_mode')
cli.wait_for_service(timeout_sec=5.0)

def set_mode(mode_name: str) -> bool:
    req = SetRobotMode.Request()
    req.mode_name = mode_name
    future = cli.call_async(req)
    rclpy.spin_until_future_complete(node, future, timeout_sec=5.0)
    ok = future.result().success if future.result() else False
    print(f"SetRobotMode '{mode_name}' -> {'OK' if ok else 'FAILED'}")
    return ok

# 上电后站立，再切行走
set_mode('STAND')
time.sleep(3.0)
set_mode('WALK')

node.destroy_node()
rclpy.shutdown()
```



---



### 5\.3 获取机器人状态



|项|值|
|---|---|
|**类型**|Service|
|**名称**|`get_robot_state_srv_hl`|
|**类型**|`crb_ros_msg/srv/GetRobotState`|



**Request**：



```Plain Text
bool start  # true: 请求获取
```



**Response**：



```Plain Text
uint8 state
# WholeBodyState: 0=IDLE, 1=INITIALIZE, 2=TASK_EXECUTION, 3=FAULT, 4=EMERGENCY_STOP
```



#### 命令行



```Bash
ros2 service call get_robot_state_srv_hl crb_ros_msg/srv/GetRobotState "{start: true}"
```



#### C\+\+



```C++
#include <rclcpp/rclcpp.hpp>
#include <crb_ros_msg/srv/get_robot_state.hpp>

auto node = rclcpp::Node::make_shared("get_state_example");
auto client = node->create_client<crb_ros_msg::srv::GetRobotState>(
    "get_robot_state_srv_hl");
client->wait_for_service(std::chrono::seconds(5));

auto req = std::make_shared<crb_ros_msg::srv::GetRobotState::Request>();
req->start = true;
auto future = client->async_send_request(req);

if (rclcpp::spin_until_future_complete(node, future) ==
    rclcpp::FutureReturnCode::SUCCESS)
{
    uint8_t state = future.get()->state;
    // 0=IDLE, 1=INITIALIZE, 2=TASK_EXECUTION, 3=FAULT, 4=EMERGENCY_STOP
    RCLCPP_INFO(node->get_logger(), "Robot state: %d", state);
}
```



#### Python



```Python
import rclpy
from rclpy.node import Node
from crb_ros_msg.srv import GetRobotState

rclpy.init()
node = Node('get_state_example')
cli = node.create_client(GetRobotState, 'get_robot_state_srv_hl')
cli.wait_for_service(timeout_sec=5.0)

req = GetRobotState.Request()
req.start = True
future = cli.call_async(req)
rclpy.spin_until_future_complete(node, future)

state_map = {0: 'IDLE', 1: 'INITIALIZE', 2: 'TASK_EXECUTION',
             3: 'FAULT', 4: 'EMERGENCY_STOP'}
state = future.result().state
print(f"Robot state: {state} ({state_map.get(state, 'UNKNOWN')})")

node.destroy_node()
rclpy.shutdown()
```



---



### 5\.4 下肢行走控制（导航模式）



|项|值|
|---|---|
|**类型**|Topic（发布）|
|**名称**|`/navigation/cmd_vel`|
|**类型**|`geometry_msgs/msg/Twist`|
|**前提**|机器人处于 `NAVIGATION` 模式（手柄 RB\+A 或导航栈触发）|



**字段说明**：



|字段|含义|单位|备注|
|---|---|---|---|
|`linear.x`|前进（\+）/ 后退（−）|m/s|内部分段映射，非 1:1|
|`linear.y`|**未接入，不生效**|—|当前代码无侧向行走|
|`angular.z`|左转（\+）/ 右转（−）|rad/s|仅 `｜linear.x｜ ≥ 0.2` 时生效|



> **速度映射**：输入值经内部分段线性映射后再送入 RL，实际运动速度与输入不是 1:1，需联调标定。
> 
> 



#### 命令行



```Bash
# 前进 0.3 m/s（持续发布）
ros2 topic pub /navigation/cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.3, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}"

# 前进同时左转
ros2 topic pub /navigation/cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.3, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.3}}"

# 发一帧后停止（--once）
ros2 topic pub --once /navigation/cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}"
```



#### C\+\+



```C++
#include <rclcpp/rclcpp.hpp>
#include <geometry_msgs/msg/twist.hpp>

class WalkController : public rclcpp::Node
{
public:
    WalkController() : Node("walk_controller")
    {
        pub_ = create_publisher<geometry_msgs::msg::Twist>(
            "/navigation/cmd_vel", 10);
    }

    void sendVelocity(double vx, double wz)
    {
        geometry_msgs::msg::Twist msg;
        msg.linear.x  = vx;   // 前进速度 m/s
        msg.angular.z = wz;   // 旋转速度 rad/s
        pub_->publish(msg);
    }

    void stop() { sendVelocity(0.0, 0.0); }

private:
    rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr pub_;
};

int main(int argc, char *argv[])
{
    rclcpp::init(argc, argv);
    auto node = std::make_shared<WalkController>();

    // 以 10 Hz 前进 3 秒后停止
    rclcpp::Rate rate(10);
    for (int i = 0; i < 30 && rclcpp::ok(); ++i) {
        node->sendVelocity(0.3, 0.0);
        rclcpp::spin_some(node);
        rate.sleep();
    }
    node->stop();

    rclcpp::shutdown();
    return 0;
}
```



#### Python



```Python
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import time

class WalkController(Node):
    def __init__(self):
        super().__init__('walk_controller')
        self.pub = self.create_publisher(Twist, '/navigation/cmd_vel', 10)

    def send_velocity(self, vx: float, wz: float):
        msg = Twist()
        msg.linear.x  = float(vx)
        msg.angular.z = float(wz)
        self.pub.publish(msg)

    def stop(self):
        self.send_velocity(0.0, 0.0)

rclpy.init()
node = WalkController()
rate = node.create_rate(10)

# 前进 3 秒后停止（机器人须先在 NAVIGATION 模式）
for _ in range(30):
    if not rclpy.ok():
        break
    node.send_velocity(0.3, 0.0)
    rclpy.spin_once(node, timeout_sec=0.1)
    rate.sleep()

node.stop()
node.destroy_node()
rclpy.shutdown()
```



---



### 5\.5 上身关节控制（上身调试模式）



上身调试分两步：先通过 Service 进入模式，再持续发布关节指令。



#### Step A：进入 / 退出上身调试



|项|值|
|---|---|
|**类型**|Service|
|**名称**|`/motion/upper_body_debug`|
|**类型**|`std_srvs/srv/SetBool`|



**命令行**



```Bash
# 进入上身调试
ros2 service call /motion/upper_body_debug std_srvs/srv/SetBool "{data: true}"
# 退出
ros2 service call /motion/upper_body_debug std_srvs/srv/SetBool "{data: false}"
```



#### Step B：发送关节指令



|项|值|
|---|---|
|**类型**|Topic（发布）|
|**名称**|`/upper_body_debug/joint_cmd`|
|**类型**|`crb_ros_msg/msg/UpperJointData`|



**消息结构**：



```Plain Text
std_msgs/Header header
float32 time_ref    # 参考时间(s)，单帧置 0；多帧插值时填帧间隔
float32 vel_scale   # 速度缩放 0.0~1.0，首次建议 0.05~0.1
sensor_msgs/JointState joint
  string[]  name      # 关节名（仅填需要控制的关节即可）
  float64[] position  # 目标角度，单位 rad
  float64[] velocity  # 可不填
  float64[] effort    # 可不填
```



**命令行**



> ⚠️ `crb_ros_msg/msg/UpperJointData` 包含嵌套消息，`ros2 topic pub` 直接构造较繁琐，**推荐用 C\+\+ 或 Python 代码发布**。如需命令行快速验证，可用如下方式（仅控制头部关节示例）：
> 
> 



```Bash
ros2 topic pub --once /upper_body_debug/joint_cmd crb_ros_msg/msg/UpperJointData \
  "{header: {stamp: {sec: 0, nanosec: 0}, frame_id: ''},
    time_ref: 0.0, vel_scale: 0.05,
    joint: {name: ['head_yaw_joint', 'head_pitch_joint'],
            position: [0.1, -0.1],
            velocity: [], effort: []}}"
```



#### C\+\+（完整流程：进入→控制→退出）



```C++
#include <rclcpp/rclcpp.hpp>
#include <std_srvs/srv/set_bool.hpp>
#include <crb_ros_msg/msg/upper_joint_data.hpp>
#include <sensor_msgs/msg/joint_state.hpp>

class UpperBodyController : public rclcpp::Node
{
public:
    UpperBodyController() : Node("upper_body_ctrl")
    {
        debug_cli_ = create_client<std_srvs::srv::SetBool>(
            "/motion/upper_body_debug");
        joint_pub_ = create_publisher<crb_ros_msg::msg::UpperJointData>(
            "/upper_body_debug/joint_cmd", 10);
    }

    bool setDebugMode(bool enable)
    {
        debug_cli_->wait_for_service(std::chrono::seconds(5));
        auto req = std::make_shared<std_srvs::srv::SetBool::Request>();
        req->data = enable;
        auto future = debug_cli_->async_send_request(req);
        if (rclcpp::spin_until_future_complete(shared_from_this(), future) ==
            rclcpp::FutureReturnCode::SUCCESS)
        {
            return future.get()->success;
        }
        return false;
    }

    void sendJointCmd(const std::vector<std::string> &names,
                      const std::vector<double> &positions,
                      float vel_scale = 0.1f)
    {
        crb_ros_msg::msg::UpperJointData msg;
        msg.header.stamp = now();
        msg.time_ref  = 0.0f;
        msg.vel_scale = vel_scale;
        msg.joint.name     = names;
        msg.joint.position = positions;
        joint_pub_->publish(msg);
    }

private:
    rclcpp::Client<std_srvs::srv::SetBool>::SharedPtr debug_cli_;
    rclcpp::Publisher<crb_ros_msg::msg::UpperJointData>::SharedPtr joint_pub_;
};

int main(int argc, char *argv[])
{
    rclcpp::init(argc, argv);
    auto node = std::make_shared<UpperBodyController>();

    // Step 1：进入上身调试
    node->setDebugMode(true);
    rclcpp::sleep_for(std::chrono::milliseconds(300));

    // Step 2：以 20 Hz 发送关节指令，持续 3 秒
    // 仅控制双臂，其余关节不填
    std::vector<std::string> names = {
        "left_shoulder_pitch_joint",  "left_shoulder_roll_joint",
        "left_elbow_pitch_joint",
        "right_shoulder_pitch_joint", "right_shoulder_roll_joint",
        "right_elbow_pitch_joint"
    };
    std::vector<double> positions = {0.3, 0.2, 0.5, 0.3, -0.2, 0.5};

    rclcpp::Rate rate(20);
    for (int i = 0; i < 60 && rclcpp::ok(); ++i) {
        node->sendJointCmd(names, positions, 0.1f);
        rclcpp::spin_some(node);
        rate.sleep();
    }

    // Step 3：退出调试
    node->setDebugMode(false);

    rclcpp::shutdown();
    return 0;
}
```



#### Python（完整流程：进入→控制→退出）



```Python
import rclpy
from rclpy.node import Node
from std_srvs.srv import SetBool
from crb_ros_msg.msg import UpperJointData
from std_msgs.msg import Header
import time

class UpperBodyController(Node):
    def __init__(self):
        super().__init__('upper_body_ctrl')
        self.debug_cli = self.create_client(SetBool, '/motion/upper_body_debug')
        self.joint_pub = self.create_publisher(
            UpperJointData, '/upper_body_debug/joint_cmd', 10)

    def set_debug_mode(self, enable: bool) -> bool:
        self.debug_cli.wait_for_service(timeout_sec=5.0)
        req = SetBool.Request()
        req.data = enable
        future = self.debug_cli.call_async(req)
        rclpy.spin_until_future_complete(self, future, timeout_sec=5.0)
        return future.result().success if future.result() else False

    def send_joint_cmd(self, names: list, positions: list,
                        vel_scale: float = 0.1):
        msg = UpperJointData()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.time_ref  = 0.0
        msg.vel_scale = float(vel_scale)
        msg.joint.name     = names
        msg.joint.position = [float(p) for p in positions]
        self.joint_pub.publish(msg)

rclpy.init()
node = UpperBodyController()

# Step 1：进入上身调试
node.set_debug_mode(True)
time.sleep(0.3)

# Step 2：以 20 Hz 发送关节指令，持续 3 秒
names = [
    'left_shoulder_pitch_joint', 'left_shoulder_roll_joint',
    'left_elbow_pitch_joint',
    'right_shoulder_pitch_joint', 'right_shoulder_roll_joint',
    'right_elbow_pitch_joint',
]
positions = [0.3, 0.2, 0.5, 0.3, -0.2, 0.5]

rate = node.create_rate(20)
for _ in range(60):
    if not rclpy.ok():
        break
    node.send_joint_cmd(names, positions, vel_scale=0.1)
    rclpy.spin_once(node, timeout_sec=0.05)
    rate.sleep()

# Step 3：退出调试
node.set_debug_mode(False)

node.destroy_node()
rclpy.shutdown()
```



---



### 5\.6 全身关节控制（全身调试模式）



全身调试与上身调试类似，Service 名不同，关节指令使用标准 `JointState`。



#### Step A：进入 / 退出全身调试



|项|值|
|---|---|
|**类型**|Service|
|**名称**|`/motion/whole_body_debug`|
|**类型**|`std_srvs/srv/SetBool`|



**命令行**



```Bash
# 进入全身调试
ros2 service call /motion/whole_body_debug std_srvs/srv/SetBool "{data: true}"
# 退出
ros2 service call /motion/whole_body_debug std_srvs/srv/SetBool "{data: false}"
```



#### Step B：发送关节指令



|项|值|
|---|---|
|**类型**|Topic（发布）|
|**名称**|`/motion/joint_cmd`|
|**类型**|`sensor_msgs/msg/JointState`|



**消息字段**：



```Plain Text
std_msgs/Header header
string[]  name      # 关节名（见第6节）
float64[] position  # 目标角度，单位 rad
float64[] velocity  # 可不填
float64[] effort    # 可不填
```



**命令行**



```Bash
# 控制头部（命令行方式验证）
ros2 topic pub --once /motion/joint_cmd sensor_msgs/msg/JointState \
  "{header: {stamp: {sec: 0, nanosec: 0}, frame_id: ''},
    name: ['head_yaw_joint', 'head_pitch_joint'],
    position: [0.1, -0.05],
    velocity: [], effort: []}"
```



#### C\+\+



```C++
#include <rclcpp/rclcpp.hpp>
#include <std_srvs/srv/set_bool.hpp>
#include <sensor_msgs/msg/joint_state.hpp>

class WholeBodyController : public rclcpp::Node
{
public:
    WholeBodyController() : Node("whole_body_ctrl")
    {
        debug_cli_ = create_client<std_srvs/srv/SetBool>(
            "/motion/whole_body_debug");
        joint_pub_ = create_publisher<sensor_msgs::msg::JointState>(
            "/motion/joint_cmd", 10);
    }

    bool setDebugMode(bool enable)
    {
        debug_cli_->wait_for_service(std::chrono::seconds(5));
        auto req = std::make_shared<std_srvs::srv::SetBool::Request>();
        req->data = enable;
        auto future = debug_cli_->async_send_request(req);
        if (rclcpp::spin_until_future_complete(shared_from_this(), future) ==
            rclcpp::FutureReturnCode::SUCCESS)
        {
            return future.get()->success;
        }
        return false;
    }

    void sendJointCmd(const std::vector<std::string> &names,
                      const std::vector<double> &positions)
    {
        sensor_msgs::msg::JointState msg;
        msg.header.stamp = now();
        msg.name     = names;
        msg.position = positions;
        joint_pub_->publish(msg);
    }

private:
    rclcpp::Client<std_srvs/srv/SetBool>::SharedPtr debug_cli_;
    rclcpp::Publisher<sensor_msgs::msg::JointState>::SharedPtr joint_pub_;
};

int main(int argc, char *argv[])
{
    rclcpp::init(argc, argv);
    auto node = std::make_shared<WholeBodyController>();

    // Step 1：进入全身调试
    node->setDebugMode(true);
    rclcpp::sleep_for(std::chrono::milliseconds(300));

    // Step 2：同时控制头部和腰部
    std::vector<std::string> names = {
        "head_yaw_joint", "head_pitch_joint", "waist_yaw_joint"
    };
    std::vector<double> positions = {0.1, -0.05, 0.0};

    rclcpp::Rate rate(20);
    for (int i = 0; i < 60 && rclcpp::ok(); ++i) {
        node->sendJointCmd(names, positions);
        rclcpp::spin_some(node);
        rate.sleep();
    }

    // Step 3：退出
    node->setDebugMode(false);

    rclcpp::shutdown();
    return 0;
}
```



#### Python



```Python
import rclpy
from rclpy.node import Node
from std_srvs.srv import SetBool
from sensor_msgs.msg import JointState
import time

class WholeBodyController(Node):
    def __init__(self):
        super().__init__('whole_body_ctrl')
        self.debug_cli = self.create_client(SetBool, '/motion/whole_body_debug')
        self.joint_pub = self.create_publisher(
            JointState, '/motion/joint_cmd', 10)

    def set_debug_mode(self, enable: bool) -> bool:
        self.debug_cli.wait_for_service(timeout_sec=5.0)
        req = SetBool.Request()
        req.data = enable
        future = self.debug_cli.call_async(req)
        rclpy.spin_until_future_complete(self, future, timeout_sec=5.0)
        return future.result().success if future.result() else False

    def send_joint_cmd(self, names: list, positions: list):
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name     = names
        msg.position = [float(p) for p in positions]
        self.joint_pub.publish(msg)

rclpy.init()
node = WholeBodyController()

# Step 1：进入全身调试
node.set_debug_mode(True)
time.sleep(0.3)

# Step 2：控制头部 + 腰部，以 20 Hz 持续 3 秒
names     = ['head_yaw_joint', 'head_pitch_joint', 'waist_yaw_joint']
positions = [0.1, -0.05, 0.0]

rate = node.create_rate(20)
for _ in range(60):
    if not rclpy.ok():
        break
    node.send_joint_cmd(names, positions)
    rclpy.spin_once(node, timeout_sec=0.05)
    rate.sleep()

# Step 3：退出调试
node.set_debug_mode(False)

node.destroy_node()
rclpy.shutdown()
```



---



### 5\.7 预设动作播放



提供两种调用方式：**Service**（无反馈，简单）和 **Action**（带状态反馈）。



#### 方式一：Service 调用（推荐快速触发）



|项|值|
|---|---|
|**类型**|Service|
|**名称**|`/casbot/event_service`|
|**类型**|`crb_ros_msg/srv/ActionEvent`|



**预设动作清单**：



|动作名|`target_tree`|`action_type`|
|---|---|---|
|点赞|`basic_action_play`|`thumb_up`|
|挥手|`basic_action_play`|`wave_hand`|
|比心|`basic_action_play`|`heart_gesture`|
|恭喜|`basic_action_play`|`congratulation_gesture`|
|剪刀手|`basic_action_play`|`v_gesture`|
|握手|`hand_shake`|`{}`|
|自我介绍|`self_introduction`|`{}`|



**命令行**



```Bash
# 挥手
ros2 service call /casbot/event_service crb_ros_msg/srv/ActionEvent \
  '{"event_id":"","event_type":"ExecSkill","blocking":false,
    "param_json":"{\"payload\":\"{\\\"action_type\\\":\\\"wave_hand\\\"}\",\"target_tree\":\"basic_action_play\"}"}'

# 点赞
ros2 service call /casbot/event_service crb_ros_msg/srv/ActionEvent \
  '{"event_id":"","event_type":"ExecSkill","blocking":false,
    "param_json":"{\"payload\":\"{\\\"action_type\\\":\\\"thumb_up\\\"}\",\"target_tree\":\"basic_action_play\"}"}'
```



**C\+\+**



```C++
#include <rclcpp/rclcpp.hpp>
#include <crb_ros_msg/srv/action_event.hpp>
#include <nlohmann/json.hpp>  // 或手工拼字符串

class SkillCaller : public rclcpp::Node
{
public:
    SkillCaller() : Node("skill_caller")
    {
        cli_ = create_client<crb_ros_msg::srv::ActionEvent>(
            "/casbot/event_service");
    }

    bool callSkill(const std::string &action_type,
                   const std::string &target_tree = "basic_action_play",
                   bool blocking = false)
    {
        cli_->wait_for_service(std::chrono::seconds(5));

        // 手工拼 JSON（避免额外依赖）
        std::string payload     = "{\\\"action_type\\\":\\\"" + action_type + "\\\"}";
        std::string param_json  = "{\"payload\":\"" + payload +
                                  "\",\"target_tree\":\"" + target_tree + "\"}";

        auto req = std::make_shared<crb_ros_msg::srv::ActionEvent::Request>();
        req->event_id   = "";
        req->event_type = "ExecSkill";
        req->blocking   = blocking;
        req->param_json = param_json;

        auto future = cli_->async_send_request(req);
        rclcpp::spin_until_future_complete(shared_from_this(), future,
                                           std::chrono::seconds(5));
        RCLCPP_INFO(get_logger(), "Skill '%s' triggered.", action_type.c_str());
        return true;
    }

private:
    rclcpp::Client<crb_ros_msg::srv::ActionEvent>::SharedPtr cli_;
};

int main(int argc, char *argv[])
{
    rclcpp::init(argc, argv);
    auto node = std::make_shared<SkillCaller>();
    node->callSkill("wave_hand");   // 挥手
    node->callSkill("thumb_up");    // 点赞
    rclcpp::shutdown();
    return 0;
}
```



**Python**



```Python
import rclpy
from rclpy.node import Node
from crb_ros_msg.srv import ActionEvent
import json

class SkillCaller(Node):
    def __init__(self):
        super().__init__('skill_caller')
        self.cli = self.create_client(ActionEvent, '/casbot/event_service')

    def call_skill(self, action_type: str,
                   target_tree: str = 'basic_action_play',
                   blocking: bool = False):
        self.cli.wait_for_service(timeout_sec=5.0)
        req = ActionEvent.Request()
        req.event_id   = ''
        req.event_type = 'ExecSkill'
        req.blocking   = blocking
        req.param_json = json.dumps({
            'payload': json.dumps({'action_type': action_type}),
            'target_tree': target_tree
        })
        future = self.cli.call_async(req)
        rclpy.spin_until_future_complete(self, future, timeout_sec=5.0)
        self.get_logger().info(f"Skill '{action_type}' triggered.")

rclpy.init()
node = SkillCaller()
node.call_skill('wave_hand')   # 挥手
node.call_skill('heart_gesture')  # 比心
node.destroy_node()
rclpy.shutdown()
```



---



#### 方式二：Action 调用（带状态反馈）



|项|值|
|---|---|
|**类型**|Action|
|**名称**|`basic_action_play`|
|**类型**|`crb_ros_msg/action/BasicActionPlay`|



**Feedback ****`state`**** 枚举**：`0`=未播放，`1`=加载中，`2`=播放中，`3`=结束



**命令行**



```Bash
ros2 action send_goal basic_action_play crb_ros_msg/action/BasicActionPlay \
  "{type: 'wave_hand'}"
```



**C\+\+**



```C++
#include <rclcpp/rclcpp.hpp>
#include <rclcpp_action/rclcpp_action.hpp>
#include <crb_ros_msg/action/basic_action_play.hpp>

using BasicActionPlay = crb_ros_msg::action::BasicActionPlay;
using GoalHandle = rclcpp_action::ClientGoalHandle<BasicActionPlay>;

class ActionPlayClient : public rclcpp::Node
{
public:
    ActionPlayClient() : Node("action_play_client")
    {
        client_ = rclcpp_action::create_client<BasicActionPlay>(
            this, "basic_action_play");
    }

    void sendGoal(const std::string &action_type)
    {
        if (!client_->wait_for_action_server(std::chrono::seconds(5))) {
            RCLCPP_ERROR(get_logger(), "Action server not available!");
            return;
        }

        BasicActionPlay::Goal goal;
        goal.type = action_type;

        rclcpp_action::Client<BasicActionPlay>::SendGoalOptions opts;

        opts.feedback_callback =
            [this](GoalHandle::SharedPtr,
                   const std::shared_ptr<const BasicActionPlay::Feedback> fb) {
                // state: 0=未播放 1=加载 2=播放中 3=结束
                RCLCPP_INFO(get_logger(), "Feedback state: %d", fb->state);
            };

        opts.result_callback =
            [this](const GoalHandle::WrappedResult &result) {
                RCLCPP_INFO(get_logger(), "Action finished: %s",
                            result.result->if_success ? "SUCCESS" : "FAILED");
            };

        client_->async_send_goal(goal, opts);
    }

private:
    rclcpp_action::Client<BasicActionPlay>::SharedPtr client_;
};

int main(int argc, char *argv[])
{
    rclcpp::init(argc, argv);
    auto node = std::make_shared<ActionPlayClient>();
    node->sendGoal("wave_hand");
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}
```



**Python**



```Python
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from crb_ros_msg.action import BasicActionPlay

class ActionPlayClient(Node):
    def __init__(self):
        super().__init__('action_play_client')
        self._client = ActionClient(self, BasicActionPlay, 'basic_action_play')

    def send_goal(self, action_type: str):
        self._client.wait_for_server(timeout_sec=5.0)
        goal = BasicActionPlay.Goal()
        goal.type = action_type

        future = self._client.send_goal_async(
            goal, feedback_callback=self._feedback_cb)
        future.add_done_callback(self._goal_response_cb)

    def _goal_response_cb(self, future):
        handle = future.result()
        if not handle.accepted:
            self.get_logger().warn('Goal rejected!')
            return
        handle.get_result_async().add_done_callback(self._result_cb)

    def _feedback_cb(self, feedback_msg):
        state_map = {0: '未播放', 1: '加载中', 2: '播放中', 3: '结束'}
        state = feedback_msg.feedback.state
        self.get_logger().info(f"Feedback: {state} ({state_map.get(state, '?')})")

    def _result_cb(self, future):
        result = future.result().result
        self.get_logger().info(
            f"Result: {'SUCCESS' if result.if_success else 'FAILED'}")

rclpy.init()
node = ActionPlayClient()
node.send_goal('wave_hand')
rclpy.spin(node)
node.destroy_node()
node.shutdown()
```



---



### 5\.8 传感器数据订阅



订阅类接口均可直接用命令行查看，也可在代码中订阅处理。



#### 传感器 Topic 一览



|数据|Topic|类型|
|---|---|---|
|全身关节反馈|`/joint_states`|`sensor_msgs/msg/JointState`|
|运控输出镜像|`/joint_control`|`sensor_msgs/msg/JointState`|
|IMU|`/imu`|`sensor_msgs/msg/Imu`|
|头部彩色图|`/camera_head/color/image_raw`|`sensor_msgs/msg/Image`|
|头部深度图|`/camera_head/depth/image_raw`|`sensor_msgs/msg/Image`|
|胸部相机|`/camera_chest/color/image_raw`|`sensor_msgs/msg/Image`|
|点云|`/rslidar_points`|`sensor_msgs/msg/PointCloud2`|



#### 命令行



```Bash
# 查看关节状态（位置/速度/力矩）
ros2 topic echo /joint_states

# 只看关节名列表
ros2 topic echo /joint_states --field name

# 查看 IMU
ros2 topic echo /imu

# 查看话题频率
ros2 topic hz /joint_states
ros2 topic hz /imu

# 查看消息定义
ros2 interface show sensor_msgs/msg/JointState
ros2 interface show crb_ros_msg/msg/RobotState
```



#### C\+\+（关节状态 \+ IMU 同时订阅）



```C++
#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/joint_state.hpp>
#include <sensor_msgs/msg/imu.hpp>

class SensorMonitor : public rclcpp::Node
{
public:
    SensorMonitor() : Node("sensor_monitor")
    {
        // 关节状态
        joint_sub_ = create_subscription<sensor_msgs::msg::JointState>(
            "/joint_states", 10,
            [this](const sensor_msgs::msg::JointState::SharedPtr msg) {
                // 打印前 6 个关节（双腿）
                for (size_t i = 0; i < std::min<size_t>(6, msg->name.size()); ++i) {
                    RCLCPP_INFO_THROTTLE(get_logger(), *get_clock(), 1000,
                        "Joint %-35s pos=%.4f rad  vel=%.4f",
                        msg->name[i].c_str(),
                        msg->position[i],
                        msg->velocity.size() > i ? msg->velocity[i] : 0.0);
                }
            });

        // IMU
        imu_sub_ = create_subscription<sensor_msgs::msg::Imu>(
            "/imu", 10,
            [this](const sensor_msgs::msg::Imu::SharedPtr msg) {
                RCLCPP_INFO_THROTTLE(get_logger(), *get_clock(), 500,
                    "IMU orient: w=%.3f x=%.3f y=%.3f z=%.3f",
                    msg->orientation.w, msg->orientation.x,
                    msg->orientation.y, msg->orientation.z);
            });
    }

private:
    rclcpp::Subscription<sensor_msgs::msg::JointState>::SharedPtr joint_sub_;
    rclcpp::Subscription<sensor_msgs::msg::Imu>::SharedPtr imu_sub_;
};

int main(int argc, char *argv[])
{
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<SensorMonitor>());
    rclcpp::shutdown();
    return 0;
}
```



#### Python（关节状态 \+ IMU 同时订阅）



```Python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState, Imu

class SensorMonitor(Node):
    def __init__(self):
        super().__init__('sensor_monitor')

        # 关节状态
        self.create_subscription(
            JointState, '/joint_states', self._joint_cb, 10)

        # IMU
        self.create_subscription(
            Imu, '/imu', self._imu_cb, 10)

        self._print_cnt = 0

    def _joint_cb(self, msg: JointState):
        # 每 50 帧打印一次（约 1 Hz 刷新）
        self._print_cnt += 1
        if self._print_cnt % 50 != 0:
            return
        self.get_logger().info('--- Joint States (first 6) ---')
        for name, pos in zip(msg.name[:6], msg.position[:6]):
            self.get_logger().info(f'  {name:<35s}: {pos:.4f} rad')

    def _imu_cb(self, msg: Imu):
        o = msg.orientation
        # 每次收到都打印（如需降频可仿上面加计数器）
        self.get_logger().info(
            f'IMU orient w={o.w:.3f} x={o.x:.3f} y={o.y:.3f} z={o.z:.3f}',
            throttle_duration_sec=1.0)

def main():
    rclpy.init()
    node = SensorMonitor()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name == '__main__':
    main()
```



---



### 5\.9 行走控制权切换（导航 / 遥控）



> **背景**：行走控制权原先只能通过手柄组合键切换（RB\+A → 导航模式，RB\+Y → 遥控模式）。  
> 
> 本接口以 Service 形式暴露相同能力，供上层程序在无手柄时自主切换。
> 
> 



|项|值|
|---|---|
|**类型**|Service|
|**名称**|`/switch_drive_mode`|
|**消息类型**|`std_srvs/srv/SetBool`|
|**前提**|当前模式为 `IDLE_MODE`、`NAVIGATION` 或 `TELEOPERATION` 之一|



**Request**：



```Plain Text
bool data   # true = 切到导航模式（NAVIGATION）
            # false = 切到遥控模式（TELEOPERATION）
```



**Response**：



```Plain Text
bool   success
string message   # 结果描述（已在目标模式时也返回 success=true）
```



**切换规则**：



|`data`|目标模式|等效手柄操作|
|---|---|---|
|`true`|`NAVIGATION`|RB \+ A|
|`false`|`TELEOPERATION`|RB \+ Y|



> **注意**：若当前不在行走相关模式（如 READY / DAMPING / DEBUG），Service 会拒绝切换并返回 `success=false`。
> 
> 



#### 命令行



```Bash
# 切到导航模式（等效 RB+A）
ros2 service call /switch_drive_mode std_srvs/srv/SetBool "{data: true}"

# 切到遥控模式（等效 RB+Y）
ros2 service call /switch_drive_mode std_srvs/srv/SetBool "{data: false}"
```



### C\+\+ 控制权切换

```C++
#include <rclcpp/rclcpp.hpp>
#include <std_srvs/srv/set_bool.hpp>

bool switchDriveMode(rclcpp::Node::SharedPtr node, bool nav_mode)
{
    auto cli = node->create_client<std_srvs::srv::SetBool>("/switch_drive_mode");
    cli->wait_for_service(std::chrono::seconds(3));
    auto req = std::make_shared<std_srvs::srv::SetBool::Request>();
    req->data = nav_mode;
    auto fut = cli->async_send_request(req);
    if(rclcpp::spin_until_future_complete(node, fut) == rclcpp::FutureReturnCode::SUCCESS)
    {
        auto res = fut.get();
        RCLCPP_INFO(node->get_logger(),"切换结果：%s",res->success?"成功":"失败");
        return res->success;
    }
    return false;
}
```



### Python 控制权切换

```Python
from std_srvs.srv import SetBool
def switch_drive_ctrl(node, is_nav:bool):
    cli = node.create_client(SetBool,"/switch_drive_mode")
    cli.wait_for_service(timeout_sec=3)
    req = SetBool.Request()
    req.data = is_nav
    res = cli.call(req)
    print("切换成功" if res.success else "切换失败")
```



### 5\.10 遥操作/自主模式总开关

1. 开启遥操作模式

```Bash
ros2 service call switch_teleoperation std_srvs/srv/SetBool "{data: true}"
```

2. 关闭遥操作

```Bash
ros2 service call switch_teleoperation std_srvs/srv/SetBool "{data: false}"
```

3. 开启自主动作模式

```Bash
ros2 service call switch_autonomous std_srvs/srv/SetBool "{data: true}"
```



---

## 6\. 关节名称速查表（全量原版）

### 6\.1 头部关节

- head\_yaw\_joint 头部偏航

- head\_pitch\_joint 头部俯仰

### 6\.2 腰部关节

- waist\_yaw\_joint 腰部旋转

### 6\.3 左臂关节

- left\_shoulder\_pitch\_joint

- left\_shoulder\_roll\_joint

- left\_shoulder\_yaw\_joint

- left\_elbow\_pitch\_joint

- left\_wrist\_joint

### 6\.4 右臂关节

- right\_shoulder\_pitch\_joint

- right\_shoulder\_roll\_joint

- right\_shoulder\_yaw\_joint

- right\_elbow\_pitch\_joint

- right\_wrist\_joint

### 6\.5 左腿下肢关节

- left\_hip\_pitch\_joint

- left\_hip\_roll\_joint

- left\_hip\_yaw\_joint

- left\_knee\_pitch\_joint

- left\_ankle\_pitch\_joint

- left\_ankle\_roll\_joint

### 6\.6 右腿下肢关节

- right\_hip\_pitch\_joint

- right\_hip\_roll\_joint

- right\_hip\_yaw\_joint

- right\_knee\_pitch\_joint

- right\_ankle\_pitch\_joint

- right\_ankle\_roll\_joint

---

## 7\. 故障状态码对照表（原版）





## 8\. 上电完整标准时序（原版固定流程）

```Plain Text
1. 机器人上电自检
2. 自动进入 READY（STAND）
3. 确认 get_robot_mode 返回 STAND 后继续
4. 延时2s完成姿态归位
5. 切换 WALK 行走主模式
6. 下发 cmd_vel 行走指令 
7. 关机前强制切 ZERO 卸力断电
```



## 9\. 常用一键调试指令合集（原版）

### 9\.1 快速复位全流程

```Bash
ros2 service call /set_robot_mode crb_ros_msg/srv/SetRobotMode "{mode_name: 'ZERO'}"
sleep 1
ros2 service call /set_robot_mode crb_ros_msg/srv/SetRobotMode "{mode_name: 'STAND'}"
```

### 9\.2 紧急停走清零速度

```Bash
ros2 topic pub --once /navigation/cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.0}, angular: {z:0.0}}"
```

### 9\.3 关闭所有调试模式

```Bash
ros2 service call /motion/upper_body_debug std_srvs/srv/SetBool "{data: false}"
ros2 service call /motion/whole_body_debug std_srvs/srv/SetBool "{data: false}"
```

### 9\.4 查看全部运动相关服务

```Bash
ros2 service list | grep -E "motion|robot|drive|debug"
```



## 10\. 接口限制与原版约束

1. 行走`linear.y`横向速度**硬件未适配**，下发无效

2. 动作技能播放须先切入 ACTION\_PLAY 模式

3. 速度缩放`vel_scale`最大值限制0\~1，超出自动截断

4. 关节角度存在软件安全限位，超限位指令自动被运控拦截

5. 导航行走指令在机器人处于 `NAVIGATION` 模式时生效；进入该模式的前提是先处于 `WALK` 模式 或者（`IDLE_MODE`）\+ `STAND` 状态。

6. 急停触发后所有运动接口全部冻结，只能切ZERO复位



