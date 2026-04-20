#!/usr/bin/env python3
import rclpy
from rclpy.node import Node

from example_interfaces.msg import String
 
 
class RobotNewsStationNode(Node): 
    def __init__(self):
        super().__init__("robot_news_station")  #  Node name
        self.publisher_ = self.create_publisher(String, "robot_news", 10)  # Publisher for topic "news", the 10 is the queue size
        self.timer_ = self.create_timer(0.5, self.publish_news)  # Timer to call publish_news every 5 seconds
        self.get_logger().info("Robot News Station Node has been started.")
    
    def publish_news(self):
        msg = String()
        msg.data = "Breaking news: ROS 2 is awesome!"
        self.publisher_.publish(msg)
        self.get_logger().info(f"Published news: {msg.data}")
 
def main(args=None):
    rclpy.init(args=args)
    node = RobotNewsStationNode() 
    node.publish_news() # publish the message to the topic
    rclpy.spin(node) 
    rclpy.shutdown()
 
 
if __name__ == "__main__":
    main()