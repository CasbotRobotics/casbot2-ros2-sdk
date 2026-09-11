cmake_minimum_required(VERSION 3.16)
project(casbot2_cpp_tests)

set(CMAKE_CXX_STANDARD 17)

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclcpp_action REQUIRED)
find_package(std_srvs REQUIRED)
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(crb_ros_msg REQUIRED)

set(DEPS
  rclcpp
  rclcpp_action
  std_srvs
  std_msgs
  geometry_msgs
  sensor_msgs
  crb_ros_msg
)

# T01: 查询机器人状态
add_executable(get_state_test src/get_state_test.cpp)
ament_target_dependencies(get_state_test ${DEPS})

# T02: 切换遥操作/自主模式
add_executable(switch_mode_test src/switch_mode_test.cpp)
ament_target_dependencies(switch_mode_test ${DEPS})

# T03: 订阅关节状态
add_executable(joint_states_test src/joint_states_test.cpp)
ament_target_dependencies(joint_states_test ${DEPS})

# T04: 发布行走速度
add_executable(cmd_vel_test src/cmd_vel_test.cpp)
ament_target_dependencies(cmd_vel_test ${DEPS})

# T05: 进入/退出上身调试
add_executable(upper_body_debug_test src/upper_body_debug_test.cpp)
ament_target_dependencies(upper_body_debug_test ${DEPS})

install(TARGETS
  get_state_test
  switch_mode_test
  joint_states_test
  cmd_vel_test
  upper_body_debug_test
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
