import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from sensor_msgs.msg import JointState
from builtin_interfaces.msg import Duration
from arm_interfaces.action import PickAndPlace
from .kinematics import forward_kinematics, inverse_kinematics
import numpy as np
import time

TOLERANCE_MM = 20  

class PickAndPlaceServer(Node):
    def __init__(self):
        super().__init__('pick_and_place_server')

        self._action_server = ActionServer(
            self, PickAndPlace, '/pick_and_place', self.execute_callback)

        self._traj_pub = self.create_publisher(
            JointTrajectory, '/arm_controller/joint_trajectory', 10)

        self._servos = [90, 90, 90, 90, 90]

        self.create_subscription(
            JointState, '/joint_states', self._joint_cb, 10)

        self.get_logger().info('Pick and Place Server ready ✅')

    def _joint_cb(self, msg):
        """Convert incoming joint positions (radians) back to servo degrees."""
        self._servos = [
            int(np.degrees(p) + 90)
            for p in msg.position[:5]
        ]

    def _publish_servos(self, s1, s2, s3, s4, s5_gripper):
        """Publish servo positions as a JointTrajectory message."""
        msg = JointTrajectory()
        msg.joint_names = ['joint1', 'joint2', 'joint3', 'joint4', 'joint5']

        pt = JointTrajectoryPoint()
        # Convert servo degrees back to radians for the topic
        pt.positions = [np.radians(s - 90) for s in [s1, s2, s3, s4, s5_gripper]]
        pt.time_from_start = Duration(sec=2, nanosec=0)

        msg.points = [pt]
        self._traj_pub.publish(msg)
        self.get_logger().info(f'Servos: [{s1},{s2},{s3},{s4},{s5_gripper}]')

    def _current_xyz(self):
        """FK on current servo positions → end-effector (x,y,z)."""
        return forward_kinematics(*self._servos[:4])

    def _distance_mm(self, target_xyz):
        cx, cy, cz = self._current_xyz()
        dist = np.sqrt((cx - target_xyz[0])**2 +
                       (cy - target_xyz[1])**2 +
                       (cz - target_xyz[2])**2)
        return int(dist * 1000)

    def execute_callback(self, goal_handle):
        self.get_logger().info('Goal received!')
        feedback = PickAndPlace.Feedback()

        pick = goal_handle.request.pick_pose.position
        drop = goal_handle.request.drop_pose.position
        pick_xyz = (pick.x, pick.y, pick.z)
        drop_xyz  = (drop.x,  drop.y,  drop.z)

        # ── STATUS 0: Move to pick pose ──────────────────────────
        self.get_logger().info(f'Moving to pick pose {pick_xyz}')
        servos = inverse_kinematics(*pick_xyz)
        if servos is None:
            self.get_logger().error('Pick pose unreachable!')
            goal_handle.abort()
            return PickAndPlace.Result(success=False)

        self._publish_servos(*servos, 0)  # gripper open

        for _ in range(50):  # wait up to 5 seconds
            feedback.status   = 0
            feedback.distance = self._distance_mm(pick_xyz)
            goal_handle.publish_feedback(feedback)
            if feedback.distance < TOLERANCE_MM:
                break
            time.sleep(0.1)

        # ── STATUS 1: Close gripper ───────────────────────────────
        self.get_logger().info('Gripping...')
        self._publish_servos(*servos, 90)  # gripper close

        for _ in range(20):
            feedback.status   = 1
            feedback.distance = 0
            goal_handle.publish_feedback(feedback)
            time.sleep(0.1)

        # ── STATUS 2: Move to drop pose ───────────────────────────
        self.get_logger().info(f'Moving to drop pose {drop_xyz}')
        servos = inverse_kinematics(*drop_xyz)
        if servos is None:
            self.get_logger().error('Drop pose unreachable!')
            goal_handle.abort()
            return PickAndPlace.Result(success=False)

        self._publish_servos(*servos, 90)  # keep gripping

        for _ in range(50):
            feedback.status   = 2
            feedback.distance = self._distance_mm(drop_xyz)
            goal_handle.publish_feedback(feedback)
            if feedback.distance < TOLERANCE_MM:
                break
            time.sleep(0.1)

        # ── STATUS 3: Open gripper ────────────────────────────────
        self.get_logger().info('Dropping...')
        self._publish_servos(*servos, 0)  # gripper open

        for _ in range(20):
            feedback.status   = 3
            feedback.distance = 0
            goal_handle.publish_feedback(feedback)
            time.sleep(0.1)

        goal_handle.succeed()
        self.get_logger().info('Pick and place complete! ✅')
        return PickAndPlace.Result(success=True)


def main(args=None):
    rclpy.init(args=args)
    node = PickAndPlaceServer()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()