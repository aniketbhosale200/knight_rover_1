import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import Command, LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    # Get the path to your robot package
    my_robot_dir = get_package_share_directory("knight_rover_new")

    # Declare the argument for the robot model file (XACRO/URDF)
    model_arg = DeclareLaunchArgument(
        name="model",
        default_value=os.path.join(my_robot_dir, "urdf", "knight_rover_new.urdf.xacro"),
        description="Absolute path to the robot URDF file"
    )

    # Declare the argument for the RViz config file
    rviz_config_arg = DeclareLaunchArgument(
        name="rviz_config",
        default_value=os.path.join(my_robot_dir, "rviz", "urdf_config.rviz"),
        description="Absolute path to RViz configuration file"
    )

    # Generate the robot_description by processing the XACRO file
    robot_description = ParameterValue(
        Command(["xacro ", LaunchConfiguration("model")]),
        value_type=str
    )

    # Launch the robot_state_publisher node
    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[{"robot_description": robot_description}]
    )

    # Launch the joint_state_publisher node
    joint_state_publisher_node = Node(
        package="joint_state_publisher",
        executable="joint_state_publisher",
        name="joint_state_publisher",
        output="screen"
    )

    # Include the classic Gazebo (Gazebo 11) launch file from the gazebo_ros package.
    # Here we set the world to an empty world.
    gazebo_launch_path = os.path.join(
        get_package_share_directory("gazebo_ros"),
        "launch",
        "gazebo.launch.py"
    )
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(gazebo_launch_path),
        launch_arguments={
            "world": os.path.join(get_package_share_directory("gazebo_ros"), "worlds", "empty.world")
        }.items()
    )

    # Spawn the robot into Gazebo using the spawn_entity.py node.
    spawn_entity = Node(
        package="gazebo_ros",
        executable="spawn_entity.py",
        arguments=["-topic", "robot_description", "-entity", "knight_rover_new"],
        output="screen"
    )

    # Launch RViz2 with the given configuration.
    #rviz_node = Node(
        #package="rviz2",
        #executable="rviz2",
        #output="screen",
        #arguments=["-d", LaunchConfiguration("rviz_config")]
    #)

    # Return the launch description with all declared nodes and actions.
    return LaunchDescription([
        model_arg,
        rviz_config_arg,
        robot_state_publisher_node,
        joint_state_publisher_node,
        gazebo,
        spawn_entity,
        #rviz_node
    ])