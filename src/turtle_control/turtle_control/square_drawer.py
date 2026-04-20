import rclpy
from rclpy.node import Node
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor

from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from std_srvs.srv import Empty
from turtle_interfaces.srv import DrawSquare

import math
import time

class SquareDrawer(Node):
    def __init__(self):
        super().__init__('square_drawer')
        
        self.cb_group = ReentrantCallbackGroup()

        # 1. Service Server for /draw_square
        self.srv = self.create_service(
            DrawSquare, '/draw_square', self.draw_square_callback, callback_group=self.cb_group)

        # 2. Publisher for velocity commands
        self.cmd_pub = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)

        # 3. Subscriber for pose feedback
        self.pose_sub = self.create_subscription(
            Pose, '/turtle1/pose', self.pose_callback, 10, callback_group=self.cb_group)
        self.current_pose = None

        # 4. Service Clients for /reset and /clear
        self.reset_client = self.create_client(Empty, '/reset', callback_group=self.cb_group)
        self.clear_client = self.create_client(Empty, '/clear', callback_group=self.cb_group)

        self.get_logger().info("Square Drawer Node is ready! Waiting for /draw_square requests...")

    def pose_callback(self, msg):
        """Continually updates the turtle's current pose."""
        self.current_pose = msg

    def draw_square_callback(self, request, response):
        """Triggered when a request to /draw_square is received."""
        self.get_logger().info(f"Received request: Draw a square of length {request.length}")

        # Wait for reset and clear services to be available
        while not self.reset_client.wait_for_service(timeout_sec=1.0) or not self.clear_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for /reset and /clear services...')

        # Step 4.1 & 4.2: Reset and clear the simulator
        req_empty = Empty.Request()
        self.reset_client.call(req_empty)
        self.clear_client.call(req_empty)

        # Force a fresh pose read after reset
        self.current_pose = None
        while self.current_pose is None:
            time.sleep(0.1)
        time.sleep(1.0)   

        for _ in range(4):
            self.move_forward(request.length)
            self.turn_90_degrees()

        # Step 5: Turtle is officially stopped and square is complete
        self.get_logger().info("Square complete!")
        return response

    def move_forward(self, distance):
        start_x = self.current_pose.x
        start_y = self.current_pose.y
        msg = Twist()

        while True:
            curr_x = self.current_pose.x
            curr_y = self.current_pose.y
            dist_moved = math.sqrt((curr_x - start_x)**2 + (curr_y - start_y)**2)
            
            
            error = distance - dist_moved

           
            if abs(error) <= 0.005:
                break

          
            msg.linear.x = 1.5 * error
            self.cmd_pub.publish(msg)
            time.sleep(0.01)

         
        msg.linear.x = 0.0
        self.cmd_pub.publish(msg)
        time.sleep(0.5)

    def turn_90_degrees(self):
         
        target_theta = self.current_pose.theta + (math.pi / 2.0)
        msg = Twist()

        while True:
            curr_theta = self.current_pose.theta
            
             
            error = math.atan2(math.sin(target_theta - curr_theta), math.cos(target_theta - curr_theta))

            if abs(error) <= 0.001:   
                break

            msg.angular.z = 3.0 * error   
            self.cmd_pub.publish(msg)
            time.sleep(0.01)

        msg.angular.z = 0.0
        self.cmd_pub.publish(msg)
        time.sleep(0.5)

def main(args=None):
    rclpy.init(args=args)
    node = SquareDrawer()
    
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()