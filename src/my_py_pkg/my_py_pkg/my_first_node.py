#!/usr/bin/env python3
# We write our code here.

import rclpy
from rclpy.node import Node


class MyNode(Node):
    def __init__(self):
        super().__init__('py_test') 
        self.counter_=0
        self.get_logger().info('MyNode initialized') # initialize the node with a name
        self.create_timer(1.0, self.timer_callback) # create a timer that calls the timer_callback function every 1 second

    def timer_callback(self):
        self.counter_ += 1
        self.get_logger().info(f'Hello ROS2! {self.counter_}') 


def main(args=None):
    rclpy.init(args=args) # initialize the ROS2 client library
    node = MyNode() # create a node
    rclpy.spin(node) # keep the node running until it is killed
    
    rclpy.shutdown() # shutdown the ROS2 client library
    
if __name__ == '__main__':
    main()