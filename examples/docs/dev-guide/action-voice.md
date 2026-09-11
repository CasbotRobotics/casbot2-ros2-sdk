# 动作与语音

!!! danger "示例会改变机器人状态或产生动作"
    先完成模式、场地和急停检查。服务失败时停止后续步骤。

ActionEvent 用于技能事件，Voice 用于语音服务，BasicActionPlay 用于预设动作（当前运控实现不发布 Feedback）。

`ActionEvent.Response` 使用 `error_code`（0 为成功）和 `msg`；`Voice.Response` 使用 `success` 和 `msg`。`VoicePlay` 为[可选配套接口](../about/compatibility.md)。

## 双语言示例

源码直接在文档构建时引入，修改对应源文件后重新构建文档。

=== "C++"

    ```cpp
    --8<-- "examples/casbot2_cpp_demo/src/action_voice_demo.cpp"
    ```

=== "Python"

    ```python
    --8<-- "examples/casbot2_py_demo/casbot2_py_demo/action_voice_demo.py"
    ```

## CLI

```bash
ros2 run casbot2_tools interface_cli basic_action_play --type wave_hand
ros2 run casbot2_tools interface_cli voice_service --type question --content "你好"
```

每次仅选择一种操作，避免技能事件与直接 Action 重复触发：

```bash
# 调用前由操作者进入 ACTION_PLAY
ros2 run casbot2_py_demo action_voice_demo --operation basic --action wave_hand
ros2 run casbot2_cpp_demo action_voice_demo --ros-args -p operation:=basic -p action:=wave_hand
# 外部语音组件存在时
ros2 run casbot2_py_demo action_voice_demo --operation voice --content 你好
ros2 run casbot2_cpp_demo action_voice_demo --ros-args -p operation:=voice -p content:=你好
```

最终成功需同时检查 ROS Action 状态与 `if_success`。完整模式和资源条件见[运动控制](motion-control.md)。
