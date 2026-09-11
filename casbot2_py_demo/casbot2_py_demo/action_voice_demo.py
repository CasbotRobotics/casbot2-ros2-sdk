"""Run one action/voice operation; select with --operation to avoid duplicate skills."""
import argparse
import rclpy
from casbot2_tools.interface_cli import InterfaceDemo, VoicePlay


class ActionVoiceDemo(InterfaceDemo):
    def run(self, operation='basic', action='wave_hand', content='你好'):
        if operation == 'basic':
            # Caller must enter ACTION_PLAY and supply matching motion resources first.
            return self.cmd_basic_action_play(action)
        if operation == 'voice':
            return self.cmd_voice_service('question', 'text', content)
        if operation == 'event':
            return self.cmd_event_skill(action, True)
        return self.cmd_voice_play(content)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--operation', choices=['basic', 'voice', 'event', 'voice-play'], default='basic')
    parser.add_argument('--action', default='wave_hand')
    parser.add_argument('--content', default='你好', help='voice text or voice-play WAV path on server')
    args = parser.parse_args()
    if args.operation == 'voice-play' and VoicePlay is None:
        parser.error('当前 crb_ros_msg 未提供 VoicePlay')
    rclpy.init()
    node = ActionVoiceDemo()
    try:
        node.run(args.operation, args.action, args.content)
        return 0
    except (RuntimeError, TimeoutError, ValueError) as exc:
        node.get_logger().error(str(exc))
        return 1
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    raise SystemExit(main())
