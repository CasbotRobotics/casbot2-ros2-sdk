# 状态获取

查询状态并订阅关节与 IMU，是首次接入时的检查入口。

## 双语言示例

源码直接在文档构建时引入，修改对应源文件后重新构建文档。

=== "C++"

    ```cpp
    --8<-- "examples/casbot2_cpp_tests/src/get_state_test.cpp"
    ```

=== "Python"

    ```python
    --8<-- "examples/casbot2_py_tests/casbot2_py_tests/get_state_test.py"
    ```

## CLI

```bash
ros2 service call get_robot_state_srv_hl crb_ros_msg/srv/GetRobotState "{start: true}"
ros2 topic echo /joint_states --once
ros2 topic echo /imu --once
```
