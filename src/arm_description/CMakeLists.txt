cmake_minimum_required(VERSION 3.8)
project(arm_description)

find_package(ament_cmake REQUIRED)

# This installs your folders so ROS 2 can find them at runtime
install(
  DIRECTORY urdf launch config
  DESTINATION share/${PROJECT_NAME}
)

ament_package()