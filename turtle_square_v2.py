import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
import math
import time


class TurtleSquare(Node):

    def __init__(self):
        super().__init__('turtle_square')

        self.publisher_ = self.create_publisher(
            Twist,
            '/turtle1/cmd_vel',
            10
        )

        self.subscription = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.pose_callback,
            10
        )

        self.pose = None

        self.state = 'MOVE'
        self.side_count = 0

        self.side_length = 2.0
        self.linear_speed = 1.0

        self.angular_speed = 0.5
        self.turn_time = (math.pi / 2) / self.angular_speed

        self.start_x = None
        self.start_y = None

        self.start_time = None

        self.get_logger().info(
            'Turtle Square Node Started. Waiting for pose...'
        )

    def pose_callback(self, msg):
        self.pose = msg

    def stop(self):
        msg = Twist()
        self.publisher_.publish(msg)

    def move_square(self):

        if self.pose is None:
            return

        msg = Twist()

        # Move forward
        if self.state == 'MOVE':

            if self.start_x is None:

                self.start_x = self.pose.x
                self.start_y = self.pose.y

                self.get_logger().info(
                    f'Starting side {self.side_count + 1}'
                )

            distance = math.sqrt(
                (self.pose.x - self.start_x) ** 2 +
                (self.pose.y - self.start_y) ** 2
            )

            if distance >= self.side_length:

                self.stop()

                self.start_time = time.time()
                self.state = 'TURN'

                self.get_logger().info(
                    f'Side {self.side_count + 1} completed.'
                )

                return

            msg.linear.x = self.linear_speed
            msg.angular.z = 0.0

        # Turn 90 degrees
        elif self.state == 'TURN':

            elapsed = time.time() - self.start_time

            if elapsed >= self.turn_time:

                self.stop()

                self.side_count += 1

                if self.side_count >= 4:

                    self.state = 'DONE'

                    self.get_logger().info(
                        'Square Completed!'
                    )

                    return

                self.start_x = None
                self.start_y = None

                self.state = 'MOVE'

                return

            msg.linear.x = 0.0
            msg.angular.z = self.angular_speed

        # Stop after completing the square
        elif self.state == 'DONE':

            self.stop()
            return

        self.publisher_.publish(msg)


def main(args=None):

    rclpy.init(args=args)

    node = TurtleSquare()

    try:

        while rclpy.ok():

            rclpy.spin_once(node, timeout_sec=0.01)

            node.move_square()

    except KeyboardInterrupt:
        pass

    finally:

        node.stop()
        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()