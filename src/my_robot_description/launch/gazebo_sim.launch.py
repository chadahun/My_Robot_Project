import os
from ament_index_python import get_package_share_directory, get_package_prefix
from launch import LaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription

def generate_launch_description():
    package_name = 'my_robot_description'
    world_file = os.path.join(get_package_share_directory(package_name), 'worlds', 'turtlebot3_autorace_2020.world')
    install_dir = get_package_prefix(package_name)

    gazebo_model_path = os.path.join(get_package_share_directory(package_name), 'models')
    if 'GAZEBO_MODEL_PATH' in os.environ:
        os.environ['GAZEBO_MODEL_PATH'] += ':' + gazebo_model_path
    else:
        os.environ['GAZEBO_MODEL_PATH'] = gazebo_model_path

    if 'GAZEBO_PLUGIN_PATH' in os.environ:
        os.environ['GAZEBO_PLUGIN_PATH'] = os.environ['GAZEBO_PLUGIN_PATH'] + \
            ':' + install_dir + '/lib'
    else:
        os.environ['GAZEBO_PLUGIN_PATH'] = install_dir + '/lib'

    package_name = 'my_robot_control'

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [os.path.join(get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py')]
            ),
        launch_arguments={'world': world_file}.items()
    )

    return LaunchDescription([
        gazebo
    ])