from setuptools import find_packages, setup

package_name = 'casbot2_tools'

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
    description='CASBOT2 ROS 2 command-line interface tools',
    license='MIT',
    entry_points={'console_scripts': [
        'interface_cli = casbot2_tools.interface_cli:main',
    ]},
)
