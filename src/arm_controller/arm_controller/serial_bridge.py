import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory
import serial
import math

class SerialBridge(Node):
    def __init__(self):
        super().__init__('serial_bridge')

        # Open USB connection to Arduino
        # Change '/dev/ttyUSB0' to '/dev/ttyACM0' if it doesn't connect
        self.ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
        self.get_logger().info('Serial port opened!')

        self.subscription = self.create_subscription(
            JointTrajectory,
            '/arm_controller/joint_trajectory',
            self.callback,
            10
        )

    def callback(self, msg):
        if not msg.points:
            return

        # Grab the first trajectory point's positions
        positions = msg.points[0].positions

        # Convert each joint from radians to degrees, clamp to 0-180
        degrees = []
        for rad in positions:
            deg = math.degrees(rad)
            deg = max(0, min(180, deg))
            degrees.append(int(deg))

        # If less than 5 joints published, pad with 90 (neutral)
        while len(degrees) < 5:
            degrees.append(90)

        # Format: "90,45,120,60,90\n"
        serial_msg = ','.join(str(d) for d in degrees) + '\n'
        self.ser.write(serial_msg.encode())
        self.get_logger().info(f'Sent to Arduino: {serial_msg.strip()}')

def main(args=None):
    rclpy.init(args=args)
    node = SerialBridge()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()