import rosbag2_py
import cv2
from cv_bridge import CvBridge
from rclpy.serialization import deserialize_message
from sensor_msgs.msg import Image
import os

def get_reader(bag_path):
    reader = rosbag2_py.SequentialReader()
    storage_options = rosbag2_py.StorageOptions(uri=bag_path, storage_id='sqlite3')
    converter_options = rosbag2_py.ConverterOptions(
        input_serialization_format='cdr',
        output_serialization_format='cdr'
    )
    reader.open(storage_options, converter_options)

    return reader

def run_extraction(bag_path, output_dir):
    full_bag_path = os.path.expanduser(bag_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    reader = get_reader(full_bag_path)
    bridge = CvBridge()
    image_count = 0
    saved_count = 0

    while reader.has_next():
        (topic, data, timestamp) = reader.read_next()
        if '/my_robot/camera/image_raw' in topic:
            image_count += 1
            if image_count % 10 == 0:
                try:
                    msg = deserialize_message(data, Image)
                    cv_img = bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
                    file_name = os.path.join(output_dir, f'{saved_count:06d}.jpg')
                    cv2.imwrite(file_name, cv_img)
                    saved_count += 1
                    if saved_count % 50 == 0:
                        print(f"Saved {saved_count} images")
                except Exception as e:
                    print(f"error: {e}")
    print(f"Finished Total Image: {saved_count} images saved in {output_dir}")


if __name__ == '__main__':
    bag_path = '~/my_ws/dataset/dataset_0.db3'
    output_path = 'extracted_images'

    run_extraction(bag_path, output_path)