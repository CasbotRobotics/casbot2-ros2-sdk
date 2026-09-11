#include <chrono>
#include <memory>
#include <stdexcept>
#include <string>
#include "rclcpp/rclcpp.hpp"
#include "rclcpp_action/rclcpp_action.hpp"
#include "crb_ros_msg/action/basic_action_play.hpp"
#include "crb_ros_msg/srv/voice.hpp"
using namespace std::chrono_literals;
using BasicActionPlay = crb_ros_msg::action::BasicActionPlay;

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  auto node = rclcpp::Node::make_shared("action_voice_demo");
  const auto operation = node->declare_parameter<std::string>("operation", "basic");
  int result = 0;
  try {
    if (operation == "voice") {
      auto cli = node->create_client<crb_ros_msg::srv::Voice>("/voice_svr");
      if (!cli->wait_for_service(3s)) { throw std::runtime_error("voice_svr unavailable (external service)"); }
      auto req = std::make_shared<crb_ros_msg::srv::Voice::Request>();
      req->type = "question"; req->content_type = "text";
      req->content = node->declare_parameter<std::string>("content", "你好");
      auto future = cli->async_send_request(req);
      if (rclcpp::spin_until_future_complete(node, future, 5s) != rclcpp::FutureReturnCode::SUCCESS) {
        throw std::runtime_error("voice_svr response timeout");
      }
      auto response = future.get();
      if (!response->success) { throw std::runtime_error(response->msg); }
      RCLCPP_INFO(node->get_logger(), "%s", response->msg.c_str());
    } else if (operation == "basic") {
      auto cli = rclcpp_action::create_client<BasicActionPlay>(node, "/basic_action_play");
      if (!cli->wait_for_action_server(3s)) { throw std::runtime_error("basic_action_play unavailable"); }
      BasicActionPlay::Goal goal;
      goal.type = node->declare_parameter<std::string>("action", "wave_hand");
      auto future = cli->async_send_goal(goal);
      if (rclcpp::spin_until_future_complete(node, future, 5s) != rclcpp::FutureReturnCode::SUCCESS) {
        throw std::runtime_error("Goal response timeout; acceptance unknown");
      }
      auto handle = future.get();
      if (!handle) { throw std::runtime_error("Goal rejected"); }
      auto done = cli->async_get_result(handle);
      if (rclcpp::spin_until_future_complete(node, done, 30s) != rclcpp::FutureReturnCode::SUCCESS) {
        if (rclcpp::ok()) {
          auto cancel = cli->async_cancel_goal(handle);
          rclcpp::spin_until_future_complete(node, cancel, 3s);
        }
        throw std::runtime_error("Action result timeout/interruption; check robot status");
      }
      const auto response = done.get();
      if (response.code != rclcpp_action::ResultCode::SUCCEEDED || !response.result->if_success) {
        throw std::runtime_error("Action failed: check ACTION_PLAY mode, resource and initial pose");
      }
      RCLCPP_INFO(node->get_logger(), "Action succeeded (if_success=true)");
    } else { throw std::runtime_error("operation must be basic or voice; use interface_cli for event/optional audio"); }
  } catch (const std::exception & error) {
    RCLCPP_ERROR(node->get_logger(), "%s", error.what());
    result = 1;
  }
  rclcpp::shutdown();
  return result;
}
