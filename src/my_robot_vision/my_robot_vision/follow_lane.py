import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from std_msgs.msg import Float32
from cv_bridge import CvBridge
import cv2
from rclpy.qos import qos_profile_sensor_data
import numpy as np

class VisionNode(Node):
    def __init__(self):
        super().__init__('vision_node')
        self.sub_ = self.create_subscription(Image, '/my_robot/camera/image_raw', self.image_callback, qos_profile_sensor_data)
        self.pub_ = self.create_publisher(Float32, '/my_robot/lane_error', 10)
        self.bridge = CvBridge()
        self.last_error = 0.0

    def image_callback(self, msg):
        if(msg.header.frame_id != 'my_robot/camera_link'):
            return
        image = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        height, width, _ = image.shape

        x1, x2 = 0, width
        y1, y2 = int(height*0.8), height

        box_bgr = image[y1:y2, x1:x2]
        box_hsv = cv2.cvtColor(box_bgr, cv2.COLOR_BGR2HSV)

        dark_yellow = np.array([20, 100, 100])
        bright_yellow = np.array([40, 255, 255])
        mask = cv2.inRange(box_hsv, dark_yellow, bright_yellow)

        lane_pixel = np.where(mask > 0)
        lane_msg = Float32()


        if lane_pixel[1].size > 50:
            lane_center_x = int(np.mean(lane_pixel[1]))

            box_width = x2 - x1
            center_x = box_width / 2

            error = center_x - lane_center_x

            lane_msg.data = float(error)
        else:
            lane_msg.data = -999.0

        self.pub_.publish(lane_msg)

        cv2.imshow('ROI Image', image)
        cv2.imshow('Mask', mask)
        cv2.waitKey(1)


def main():
    rclpy.init()

    node = VisionNode()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()