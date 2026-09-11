# 关节调试

!!! danger "示例会改变机器人状态或产生动作"
    先完成模式、场地和急停检查。服务失败时停止后续步骤。

上身与全身调试分别使用 UpperJointData 和 JointStateData；当前接口使用扁平数组。

!!! warning "模式和增益"
    上身／全身调试先申请对应模式；退出时关闭调试开关。`kp` / `kd` 可否留空取决于运控默认增益配置，灵巧手不填写这组增益。

全身控制的双语言实现见[运动控制](motion-control.md)中全身调试一节。

## 双语言示例

源码直接在文档构建时引入，修改对应源文件后重新构建文档。

=== "C++"

    ```cpp
    --8<-- "examples/casbot2_cpp_demo/src/debug_joint_demo.cpp"
    ```

=== "Python"

    ```python
    --8<-- "examples/casbot2_py_demo/casbot2_py_demo/debug_joint_demo.py"
    ```

## CLI

```bash
ros2 interface show crb_ros_msg/msg/UpperJointData
ros2 interface show crb_ros_msg/msg/JointStateData
ros2 run casbot2_tools interface_cli sub_motion_debug_joint_state --seconds 5
```
