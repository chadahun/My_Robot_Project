import os
from ament_index_python import get_package_share_directory, get_package_prefix
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.actions import IncludeLaunchDescription
from launch.actions import TimerAction
import xacro

from launch.actions import RegisterEventHandler
from launch.event_handlers import OnProcessExit, OnProcessStart

from launch.actions import GroupAction
from launch_ros.actions import PushRosNamespace

def generate_launch_description():
    package_name = 'my_robot_description'
    urdf_file = os.path.join(get_package_share_directory(package_name), 'urdf', 'my_robot_description.urdf.xacro')
    world_file = os.path.join(get_package_share_directory(package_name), 'worlds', 'turtlebot3_autorace_2020.world')
    install_dir = get_package_prefix(package_name)
    config_file = os.path.join(get_package_share_directory(package_name), 'config', 'my_controllers.yaml')

    robot_name_arg = DeclareLaunchArgument('robot_name', default_value='my_robot')
    robot_name = LaunchConfiguration('robot_name')

    rsp_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        namespace=robot_name,
        parameters=[{
                'robot_description': Command(['xacro ', urdf_file, ' robot_name:=', robot_name]),
                'use_sim_tile': True,
                'frame_prefix': [robot_name, '/']
            }],
        output='screen'
    )

#     gazebo_model_path = os.path.join(get_package_share_directory(package_name), 'models')
#     if 'GAZEBO_MODEL_PATH' in os.environ:
#         os.environ['GAZEBO_MODEL_PATH'] += ':' + gazebo_model_path
#     else:
#         os.environ['GAZEBO_MODEL_PATH'] = gazebo_model_path

#     if 'GAZEBO_PLUGIN_PATH' in os.environ:
#         os.environ['GAZEBO_PLUGIN_PATH'] = os.environ['GAZEBO_PLUGIN_PATH'] + \
#             ':' + install_dir + '/lib'
#     else:
#         os.environ['GAZEBO_PLUGIN_PATH'] = install_dir + '/lib'

#     print("GAZEBO MODELS PATH=="+str(os.environ["GAZEBO_MODEL_PATH"]))
#     print("GAZEBO PLUGINS PATH=="+str(os.environ["GAZEBO_PLUGIN_PATH"]))

#     robot_1 = 'my_robot'
#     robot_2 = 'dest_robot'

#     robot_1_group = GroupAction(
#     actions=[
#         PushRosNamespace(robot_1),
#         Node(
#             package='controller_manager',
#             executable='spawner',
#             name='diff_drive_controller',
#             arguments=[
#                 'diff_drive_controller', '-c', f'/{robot_1}/controller_manager'
#             ],
#             output='screen'
#         ),
#         Node(
#             package='controller_manager',
#             executable='spawner',
#             name='joint_state_broadcaster',
#             arguments=[
#                 'joint_state_broadcaster', '-c', f'/{robot_1}/controller_manager'
#             ],
#             output='screen'
#         ),
#     ]
# )

#     robot_2_group = GroupAction(
#     actions=[
#         PushRosNamespace(robot_2),
#         Node(
#             package='controller_manager',
#             executable='spawner',
#             name='diff_drive_controller',
#             arguments=[
#                 'diff_drive_controller', '-c', f'/{robot_2}/controller_manager'
#             ],
#             output='screen'
#         ),
#         Node(
#             package='controller_manager',
#             executable='spawner',
#             name='joint_state_broadcaster',
#             arguments=[
#                 'joint_state_broadcaster', '-c', f'/{robot_2}/controller_manager'
#             ],
#             output='screen'
#         )
#     ]
# )

#     robot_1_rsp = Node(
#             package='robot_state_publisher',
#             executable='robot_state_publisher',
#             name='robot_state_publisher',
#             namespace=robot_1,
#             parameters=[{
#                 'robot_description': Command(['xacro ', urdf_file, ' robot_name:=', robot_1]),
#                 'use_sim_time': True,
#                 'frame_prefix': robot_1+ '/'
#             }],
#             output='screen'
#         )

#     robot_2_rsp = Node(
#             package='robot_state_publisher',
#             executable='robot_state_publisher',
#             name='robot_state_publisher',
#             namespace=robot_2,
#             parameters=[{
#                 'robot_description': Command(['xacro ', urdf_file, ' robot_name:=', robot_2]),
#                 'use_sim_time': True,
#                 'frame_prefix': robot_2 + '/'
#             }],
#             output='screen'
#         )

#     robot_1_spawn = Node(
#         package='gazebo_ros',
#         executable='spawn_entity.py',
#         arguments=[
#             '-entity', robot_1,
#             '-topic', f'/{robot_1}/robot_description',
#             '-x', '0.181752', '-y', '-1.757106', '-z', '0.3'
#         ],
#         output='screen'
#     )

#     robot_1_spawn_delay = TimerAction(
#         period=3.0,
#         actions=[robot_1_spawn]
#     )

#     robot_2_spawn = Node(
#         package='gazebo_ros',
#         executable='spawn_entity.py',
#         arguments=[
#             '-entity', robot_2,
#             '-topic',  f'/{robot_2}/robot_description',
#             '-x', '0.715248', '-y', '-1.757106', '-z', '0.3'
#         ],
#         output='screen'
#     )

#     robot_1_group_handler = RegisterEventHandler(
#         OnProcessExit(
#             target_action=robot_1_spawn,
#             on_exit=[robot_1_group, robot_2_spawn]
#         )
#     )

#     robot_2_group_handler = RegisterEventHandler(
#         OnProcessExit(
#             target_action=robot_2_spawn,
#             on_exit=[robot_2_group]
#         )
#     )

#     gazebo = IncludeLaunchDescription(
#         PythonLaunchDescriptionSource(
#             [os.path.join(get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py')]
#             ),
#         launch_arguments={'world': world_file}.items()
#     )

    return LaunchDescription([
        # gazebo,
        # robot_1_rsp,
        # robot_2_rsp,
        # robot_1_spawn_delay,
        # robot_1_group_handler,
        # robot_2_group_handler
        robot_name_arg,
        rsp_node
    ])