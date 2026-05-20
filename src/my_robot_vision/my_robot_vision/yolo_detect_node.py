import rclpy
from rclpy.node import Node
from rclpy.executors import ExternalShutdownException
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from std_msgs.msg import Float32
from ultralytics import YOLO
from ament_index_python import get_package_share_directory
import os

class Yolo_detect_node(Node):
    def __init__(self):
        super().__init__("detect_node")

        package_share_dir = get_package_share_directory('my_robot_vision')

        self.declare_parameter('target_frame_id', 'my_robot/camera_link')
        self.target_frame = self.get_parameter('target_frame_id').get_parameter_value().string_value

        self.model = YOLO(os.path.join(package_share_dir, 'models', 'best.pt'))
        self.bridge = CvBridge()

        self.img_sub_ = self.create_subscription(Image, '/my_robot/camera/image_raw', self.image_callback, 10)
        self.error_pub_ = self.create_publisher(Float32, '/my_robot/yolo_error', 10)

    def image_callback(self, msg):
        if msg.header.frame_id != self.target_frame:
            return

        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

            res = self.model.predict(cv_image, conf=0.5, device='0')

            img_h, img_w, _ = cv_image.shape

            if res and len(res[0].boxes) > 0:
                box = res[0].boxes[0]
                x1, _, x2, _ = box.xyxy[0].tolist()
                center_x = (x1 + x2) / 2.0

                error = center_x - (img_w / 2.0)

                self.error_pub_.publish(Float32(data=error))
        except Exception as e:
            self.get_logger().info(f"Error: {e}")



def main():
    rclpy.init()
    node = Yolo_detect_node()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()