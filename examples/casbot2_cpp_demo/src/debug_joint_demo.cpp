#include <algorithm>
#include <chrono>
#include <memory>
#include <stdexcept>
#include <string>
#include "rclcpp/rclcpp.hpp"
#include "std_srvs/srv/set_bool.hpp"
#include "sensor_msgs/msg/joint_state.hpp"
#include "crb_ros_msg/msg/joint_state_data.hpp"
#include "crb_ros_msg/msg/upper_joint_data.hpp"
using namespace std::chrono_literals;

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  auto node = rclcpp::Node::make_shared("debug_joint_demo");
  sensor_msgs::msg::JointState::SharedPtr measured;
  auto sub = node->create_subscription<sensor_msgs::msg::JointState>(
    "/joint_states", 10, [&](sensor_msgs::msg::JointState::SharedPtr msg) { measured = msg; });
  auto switch_mode = [&](const std::string & service, bool enabled) {
    auto cli = node->create_client<std_srvs::srv::SetBool>(service);
    if (!cli->wait_for_service(3s)) { throw std::runtime_error(service + " unavailable"); }
    auto req = std::make_shared<std_srvs::srv::SetBool::Request>();
    req->data = enabled;
    auto future = cli->async_send_request(req);
    if (rclcpp::spin_until_future_complete(node, future, 3s) != rclcpp::FutureReturnCode::SUCCESS) {
      throw std::runtime_error(service + " timed out; transition state unknown");
    }
    auto response = future.get();
    if (!response->success) { throw std::runtime_error(response->message); }
  };
  std::string active_service;
  int result = 0;
  try {
    auto deadline = std::chrono::steady_clock::now() + 5s;
    while (rclcpp::ok() && !measured && std::chrono::steady_clock::now() < deadline) {
      rclcpp::spin_some(node);
      rclcpp::sleep_for(20ms);
    }
    if (!measured || measured->name.empty() || measured->name.size() != measured->position.size()) {
      throw std::runtime_error("No valid /joint_states snapshot");
    }
    const auto names = measured->name;
    const auto positions = measured->position;
    const auto found = std::find(names.begin(), names.end(), "left_shoulder_pitch_joint");
    if (found == names.end()) { throw std::runtime_error("Missing shoulder joint"); }
    const auto index = static_cast<size_t>(found - names.begin());
    auto upper_pub = node->create_publisher<crb_ros_msg::msg::UpperJointData>("/upper_body_debug/joint_cmd", 10);
    auto whole_pub = node->create_publisher<crb_ros_msg::msg::JointStateData>("/motion/debug/joint_cmd", 10);
    switch_mode("/motion/upper_body_debug", true);
    active_service = "/motion/upper_body_debug";
    crb_ros_msg::msg::UpperJointData upper;
    upper.vel_scale = 0.05f;
    upper.name = {names[index]};
    upper.position = {positions[index]};
    upper.velocity = {0.0}; upper.effort = {0.0};
    // Hold the measured pose. Empty PD requires use_default_kp_kd=true.
    for (int i = 0; i < 20 && rclcpp::ok(); ++i) {
      upper.header.stamp = node->now();
      upper_pub->publish(upper);
      rclcpp::spin_some(node); rclcpp::sleep_for(100ms);
    }
    switch_mode(active_service, false); active_service.clear();
    switch_mode("/motion/whole_body_debug", true);
    active_service = "/motion/whole_body_debug";
    crb_ros_msg::msg::JointStateData whole;
    whole.name = names; whole.position = positions;
    whole.velocity.assign(names.size(), 0.0); whole.effort.assign(names.size(), 0.0);
    for (int i = 0; i < 20 && rclcpp::ok(); ++i) {
      whole.header.stamp = node->now();
      whole_pub->publish(whole);
      rclcpp::spin_some(node); rclcpp::sleep_for(100ms);
    }
    switch_mode(active_service, false); active_service.clear();
  } catch (const std::exception & error) {
    RCLCPP_ERROR(node->get_logger(), "%s", error.what());
    result = 1;
  }
  if (!active_service.empty() && rclcpp::ok()) {
    try { switch_mode(active_service, false); }
    catch (const std::exception & error) { RCLCPP_ERROR(node->get_logger(), "%s", error.what()); }
  }
  rclcpp::shutdown();
  return result;
}
