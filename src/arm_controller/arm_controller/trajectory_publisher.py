import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration

class TrajectoryPublisher(Node):
    def __init__(self):
        super().__init__('trajectory_publisher')

        # Create publisher on the exact topic name from the PDF
        self.publisher = self.create_publisher(
            JointTrajectory,
            '/arm_controller/joint_trajectory',
            10
        )

        # Publish every 2 seconds
        self.timer = self.create_timer(2.0, self.publish_trajectory)
        self.get_logger().info('Trajectory publisher started!')

    def publish_trajectory(self):
        msg = JointTrajectory()

        # Must match URDF joint names exactly
        msg.joint_names = ['joint1', 'joint2', 'joint3', 'joint4']

        # One trajectory point — target angles in radians
        point = JointTrajectoryPoint()
        point.positions = [0.0, 0.5, -0.5, 0.3]  # radians
        point.time_from_start = Duration(sec=2, nanosec=0)

        msg.points = [point]
        self.publisher.publish(msg)
        self.get_logger().info(f'Published: {point.positions}')

def main(args=None):
    rclpy.init(args=args)
    node = TrajectoryPublisher()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()