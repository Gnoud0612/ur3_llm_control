from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='ur3_llm_control',
            executable='executor',
            name='ur3_llm_executor',
            output='screen'
        )
    ])
