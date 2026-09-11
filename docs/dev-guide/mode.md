# 模式切换

!!! danger "示例会改变机器人状态或产生动作"
    先完成模式、场地和急停检查。服务失败时停止后续步骤。

设置 ZERO / STAND / WALK 与切换遥操作／自主模式前，先核对当前模式和目标服务。

具体状态机及允许顺序见[运动控制](motion-control.md)。示例会尝试切换到 WALK；不要将该程序用作只读查询。

## 双语言示例

源码直接在文档构建时引入，修改对应源文件后重新构建文档。

=== "C++"

    ```cpp
    --8<-- "examples/casbot2_cpp_demo/src/service_mode_demo.cpp"
    ```

=== "Python"

    ```python
    --8<-- "examples/casbot2_py_demo/casbot2_py_demo/service_mode_demo.py"
    ```

## CLI

```bash
ros2 run casbot2_tools interface_cli get_robot_mode
ros2 run casbot2_tools interface_cli set_robot_mode --mode STAND
```
