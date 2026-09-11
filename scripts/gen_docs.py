"""Generate API reference from interfaces actually exported by CMake; no ROS required."""
from pathlib import Path
import re
import textwrap

import mkdocs_gen_files

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / 'crb_ros_msg'
SOURCE_URL = 'https://github.com/CasbotRobotics/casbot2-ros2-sdk/blob/main/'


def write_page(destination, content, source):
    with mkdocs_gen_files.open(destination, 'w') as page:
        page.write(content)
    mkdocs_gen_files.set_edit_path(destination, '../' + source)


def tab(label, language, code):
    return f'=== "{label}"\n\n' + textwrap.indent(f'```{language}\n{code.rstrip()}\n```\n', '    ') + '\n'


def snake_case(name):
    return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()


def fields(section):
    """Read field and constant declarations, retaining inline/predecessor comments."""
    comments = []
    for line in section.splitlines():
        declaration, _, comment = line.partition('#')
        if not declaration.strip():
            if comment.strip():
                comments.append(comment.strip())
            continue
        parts = declaration.strip().split(None, 1)
        if len(parts) != 2:
            raise ValueError(f'Invalid interface field: {line!r}')
        yield parts[0], parts[1], comment.strip() or ' / '.join(comments)
        comments = []


cmake = re.sub(r'#[^\n]*', '', (PACKAGE / 'CMakeLists.txt').read_text(encoding='utf-8'))
exports = {}
for kind in ('msg', 'srv', 'action'):
    block = re.search(rf'set\(\s*{kind}_files\s+(.*?)\)', cmake, re.DOTALL)
    if block is None:
        raise ValueError(f'CMakeLists.txt missing {kind}_files')
    paths = re.findall(rf'"({kind}/[^"\n]+\.{kind})"', block.group(1))
    if not paths or len(paths) != len(set(paths)):
        raise ValueError(f'Empty or duplicate exports in {kind}_files')
    exports[kind] = paths

for kind, title, destination in (
    ('msg', 'Topic 与消息类型', 'api/messages.md'),
    ('srv', 'Service 服务类型', 'api/services.md'),
    ('action', 'Action 动作类型', 'api/actions.md'),
):
    content = [f'# {title}\n\n',
        '本页在构建时读取 `crb_ros_msg/` 中由 CMake 注册的接口，字段不维护手写副本。'
        '接口类型名与运行时端点名不同；端点和前置模式见[接口总览](../about/overview.md)与'
        '[运控参考](../dev-guide/motion-control.md)。\n\n',
        '双语言示例展示类型构造；发送前必须按当前字段定义填充消息／请求／目标。'
        '完整客户端示例见[开发指南](../dev-guide/python.md)。\n\n']
    if kind == 'msg':
        content.append('## 自定义消息依赖图\n\n```mermaid\ngraph LR\n')
        names = {Path(p).stem for p in exports['msg']}
        edges = set()
        connected = set()
        for relative in sorted(exports['msg']):
            name = Path(relative).stem
            for field_type, _, _ in fields((PACKAGE / relative).read_text(encoding='utf-8')):
                dependency = re.sub(r'\[.*\]', '', field_type)
                if dependency in names or '/' in dependency:
                    node_id = dependency.replace('/', '_')
                    edges.add(f'    {name} --> {node_id}["{dependency}"]\n')
                    connected.update((name, dependency))
        content.extend(sorted(edges))
        content.append('```\n\n')
        independent = ', '.join(f'`{name}`' for name in sorted(names - connected))
        content.append(f'其余消息仅含基础字段，无嵌套消息依赖：{independent}。\n\n')
    elif kind == 'action':
        content.append('!!! warning "可选音频 Action"\n'
            '    本仓库未提供 `VoicePlay.action`。音频 Action 需配套软件中的兼容定义，'
            '详见[兼容性](../about/compatibility.md)。\n\n')
    content.append('本次 main 核对范围及历史扩展见[兼容性](../about/compatibility.md)。存在类型不代表运行端提供对应服务。\n\n')
    for relative in sorted(exports[kind]):
        source = PACKAGE / relative
        name = source.stem
        type_name = f'crb_ros_msg/{kind}/{name}'
        raw = source.read_text(encoding='utf-8')
        content.append(f'## {name}\n\n| 属性 | 值 |\n| --- | --- |\n'
            f'| 接口类型 | `{type_name}` |\n'
            f'| 源文件 | [{relative}]({SOURCE_URL}crb_ros_msg/{relative}) |\n\n')
        labels = {'msg': ['消息'], 'srv': ['Request', 'Response'], 'action': ['Goal', 'Result', 'Feedback']}[kind]
        sections = re.split(r'^---\s*$', raw, flags=re.MULTILINE)
        if len(sections) != len(labels):
            raise ValueError(f'Wrong section count in {relative}')
        for label, section in zip(labels, sections):
            declarations = list(fields(section))
            content.append(f'### {label}\n\n')
            if declarations:
                content.append('| 属性 | 值 |\n| --- | --- |\n')
                for field_type, field_name, comment in declarations:
                    description = ('；' + comment.replace('|', '\\|')) if comment else ''
                    content.append(f'| `{field_name}` | `{field_type}`{description} |\n')
                content.append('\n')
            else:
                content.append('无字段。\n\n')
        content.append(f'??? note "完整源定义"\n\n'+textwrap.indent(f'```text\n{raw.rstrip()}\n```\n','    ')+'\n')
        suffix = {'msg': '', 'srv': '.Request', 'action': '.Goal'}[kind]
        cpp_suffix = suffix.replace('.', '::')
        var = {'msg': 'message', 'srv': 'request', 'action': 'goal'}[kind]
        content.append(tab('Python', 'python', f'from crb_ros_msg.{kind} import {name}\n\n{var} = {name}{suffix}()\n# 按上表填写 {var} 字段；完整调用流程见开发指南。'))
        content.append(tab('C++', 'cpp', f'#include "crb_ros_msg/{kind}/{snake_case(name)}.hpp"\n\ncrb_ros_msg::{kind}::{name}{cpp_suffix} {var};\n// 按上表填写 {var} 字段；完整调用流程见开发指南。'))
        content.append(f'### CLI 核查\n\n```bash\nros2 interface show {type_name}\n')
        if kind == 'srv': content.append(f'ros2 service find {type_name}\n')
        elif kind == 'action': content.append('ros2 action list -t\n')
        else: content.append('ros2 topic list -t\n')
        content.append('```\n\n')
    content.append('## 端点调用示例\n\n')
    if kind == 'msg':
        content.append('以下命令只读取状态：\n\n```bash\nros2 topic echo /joint_states --once\nros2 topic echo /imu --once\n```\n')
    elif kind == 'srv':
        content.append('```bash\nros2 service call get_robot_mode crb_ros_msg/srv/GetRobotMode "{}"\nros2 service call get_robot_state_srv_hl crb_ros_msg/srv/GetRobotState "{start: true}"\n```\n')
    else:
        content.append('!!! danger "动作会驱动机器人"\n    先完成模式和场地检查，确认动作资源存在。\n\n'
            '```bash\nros2 action send_goal /basic_action_play crb_ros_msg/action/BasicActionPlay "{type: wave_hand}" --feedback\n```\n')
    content.append('\n更多可直接调用的命令见[接口全覆盖](interfaces.md)。\n')
    write_page(destination, ''.join(content), 'crb_ros_msg/CMakeLists.txt')

write_page('changelog.md', (ROOT / 'CHANGELOG.md').read_text(encoding='utf-8'), 'CHANGELOG.md')
