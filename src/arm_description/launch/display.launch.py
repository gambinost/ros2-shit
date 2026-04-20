import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

def generate_launch_description():

    # Get the path to our package's share directory
    pkg_path = get_package_share_directory('arm_description')

    # Build the full path to the URDF file
    urdf_file = os.path.join(pkg_path, 'urdf', 'arm.urdf')

    # Read the URDF file contents into a string
    with open(urdf_file, 'r') as f:
        robot_description = f.read()

    # Node 1: robot_state_publisher
    # Reads the URDF and publishes all the TF transforms
    # (TF = coordinate frames for each link — RViz2 needs this to draw the robot)
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        parameters=[{'robot_description': robot_description}], 
        output='screen'
    )

    # Node 2: joint_state_publisher_gui
    # Opens a window with sliders — one per joint
    # Lets you manually move joints to test the URDF visually
    joint_state_publisher_gui_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui'
    )

    # Node 3: rviz2
    # The 3D visualizer — shows your robot
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen'
    )

    return LaunchDescription([
        robot_state_publisher_node,
        joint_state_publisher_gui_node,
        rviz_node,
    ])