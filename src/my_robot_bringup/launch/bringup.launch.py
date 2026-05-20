from ament_index_python import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, TimerAction, GroupAction, RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node, PushRosNamespace
import os

def generate_launch_description():
    # vision_pkg = get_package_share_directory("my_robot_vision")
    # control_pkg = get_package_share_directory("my_robot_control")
    desc_pkg = get_package_share_directory("my_robot_description")
    config_file = os.path.join(desc_pkg, 'config', 'my_controllers.yaml')

    robot_1 = 'my_robot'
    robot_2 = 'dest_robot'

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [os.path.join(desc_pkg, 'launch', 'gazebo_sim.launch.py')]
        )
    )

    robot_1_rsp = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [os.path.join(desc_pkg, 'launch', 'rsp.launch.py')]
        ),
        launch_arguments={'robot_name': robot_1}.items()
    )
    robot_2_rsp = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [os.path.join(desc_pkg, 'launch', 'rsp.launch.py')]
        ),
        launch_arguments={'robot_name': robot_2}.items()
    )
    robot_1_group = GroupAction(
    actions=[
        PushRosNamespace(robot_1),
        Node(
            package='controller_manager',
            executable='spawner',
            name='diff_drive_controller',
            arguments=[
                'diff_drive_controller', '-c', f'/{robot_1}/controller_manager',
                '--param-file', config_file
            ],
            output='screen'
        ),
        Node(
            package='controller_manager',
            executable='spawner',
            name='joint_state_broadcaster',
            arguments=[
                'joint_state_broadcaster', '-c', f'/{robot_1}/controller_manager',
                '--param-file', config_file
            ],
            output='screen'
        ),
    ]
)

    robot_2_group = GroupAction(
    actions=[
        PushRosNamespace(robot_2),
        Node(
            package='controller_manager',
            executable='spawner',
            name='diff_drive_controller',
            arguments=[
                'diff_drive_controller', '-c', f'/{robot_2}/controller_manager'
            ],
            output='screen'
        ),
        Node(
            package='controller_manager',
            executable='spawner',
            name='joint_state_broadcaster',
            arguments=[
                'joint_state_broadcaster', '-c', f'/{robot_2}/controller_manager'
            ],
            output='screen'
        )
    ]
)

    robot_1_spawn = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-entity', robot_1,
            '-topic', f'/{robot_1}/robot_description',
            '-x', '0.181752', '-y', '-1.757106', '-z', '0.3'
        ],
        output='screen'
    )
    robot_2_spawn = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-entity', robot_2,
            '-topic',  f'/{robot_2}/robot_description',
            '-x', '0.715248', '-y', '-1.757106', '-z', '0.3'
        ],
        output='screen'
    )

    robot_1_group_handler = RegisterEventHandler(
        OnProcessExit(
            target_action=robot_1_spawn,
            on_exit=[robot_1_group, robot_2_spawn]
        )
    )

    robot_2_group_handler = RegisterEventHandler(
        OnProcessExit(
            target_action=robot_2_spawn,
            on_exit=[robot_2_group]
        )
    )

    delay_sim = TimerAction(
        period=5.0,
        actions=[
            robot_1_spawn,
            robot_1_group_handler,
            robot_2_group_handler
        ]
    )

    vision_node = Node(
        package='my_robot_vision',
        executable='vision_node',
        namespace=robot_1,
        parameters=[{'use_sim_time': True}],
        output='screen'
    )

    yolo_node = Node(
        package='my_robot_vision',
        executable='detect_node',
        namespace=robot_1,
        parameters=[{'use_sim_time': True}],
        output='screen'
    )

    follower_node = Node(
        package='my_robot_control',
        executable='follower_node',
        # namespace=robot_1,
        parameters=[{'use_sim_time': True}],
        output='screen'
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', os.path.join(desc_pkg, 'rviz', 'my_robot.rviz')],
        output='screen'
    )

    return LaunchDescription([
        gazebo,
        robot_1_rsp,
        robot_2_rsp,
        delay_sim,
        vision_node,
        yolo_node,
        follower_node,
        rviz_node
    ])