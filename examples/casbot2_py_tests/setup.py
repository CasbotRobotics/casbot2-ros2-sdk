from setuptools import find_packages, setup

package_name = 'casbot2_py_tests'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    tests_require=['pytest'],
    zip_safe=True,
    maintainer='casbot2-dev',
    maintainer_email='maintainer@example.com',
    description='CASBOT2 ROS 2 integration workflows and offline contract tests',
    license='MIT',
    entry_points={'console_scripts': [
        'cmd_vel_test = casbot2_py_tests.cmd_vel_test:main',
        'get_state_test = casbot2_py_tests.get_state_test:main',
        'joint_states_test = casbot2_py_tests.joint_states_test:main',
        'switch_mode_test = casbot2_py_tests.switch_mode_test:main',
        'test_action_play_flow = casbot2_py_tests.test_action_play_flow:main',
        'test_kp_kd_debug = casbot2_py_tests.test_kp_kd_debug:main',
        'test_kp_kd_joint_states = casbot2_py_tests.test_kp_kd_joint_states:main',
        'test_sensors_and_actions_flow = casbot2_py_tests.test_sensors_and_actions_flow:main',
        'test_upper_body_flow = casbot2_py_tests.test_upper_body_flow:main',
        'test_walk_flow = casbot2_py_tests.test_walk_flow:main',
        'test_whole_body_flow = casbot2_py_tests.test_whole_body_flow:main',
        'upper_body_debug_test = casbot2_py_tests.upper_body_debug_test:main',
    ]},
)
