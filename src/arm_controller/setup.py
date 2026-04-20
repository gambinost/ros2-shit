from setuptools import find_packages, setup

package_name = 'arm_controller'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Moamen',
    maintainer_email='you@email.com',
    description='Arm trajectory publisher',
    license='MIT',
    entry_points={
        'console_scripts': [
            'trajectory_publisher = arm_controller.trajectory_publisher:main',
            'serial_bridge = arm_controller.serial_bridge:main', 
            'arm_gui = arm_controller.arm_gui:main',
        ],
    },
)