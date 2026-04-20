import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration
import tkinter as tk
import math
import threading

class ArmGUI(Node):
    def __init__(self):
        super().__init__('arm_gui')
        self.publisher = self.create_publisher(
            JointTrajectory,
            '/arm_controller/joint_trajectory',
            10
        )

    def publish_angles(self, degrees_list):
        msg = JointTrajectory()
        msg.joint_names = ['joint1', 'joint2', 'joint3', 'joint4', 'joint5']

        point = JointTrajectoryPoint()
        # GUI gives degrees, topic expects radians
        point.positions = [math.radians(d) for d in degrees_list]
        point.time_from_start = Duration(sec=1, nanosec=0)

        msg.points = [point]
        self.publisher.publish(msg)
        self.get_logger().info(f'Published degrees: {degrees_list}')

def main(args=None):
    rclpy.init(args=args)
    node = ArmGUI()

    # Run ROS2 spin in background thread so GUI doesn't freeze
    ros_thread = threading.Thread(target=rclpy.spin, args=(node,), daemon=True)
    ros_thread.start()

    # Build the tkinter window
    root = tk.Tk()
    root.title('Arm Controller')
    root.geometry('400x350')

    sliders = []
    joint_names = ['Joint 1 (Base)', 'Joint 2 (L1-L2)', 'Joint 3 (L2-L3)', 'Joint 4 (L3-Gripper)', 'Joint 5 (Gripper)']

    for name in joint_names:
        tk.Label(root, text=name, font=('Arial', 10)).pack(pady=2)
        slider = tk.Scale(root, from_=0, to=180, orient=tk.HORIZONTAL, length=300)
        slider.set(90)  # start at neutral position
        slider.pack()
        sliders.append(slider)

    def on_send():
        degrees = [s.get() for s in sliders]
        node.publish_angles(degrees)

    tk.Button(root, text='Send to Arm', command=on_send,
              bg='green', fg='white', font=('Arial', 12)).pack(pady=15)

    root.mainloop()
    rclpy.shutdown()

if __name__ == '__main__':
    main()