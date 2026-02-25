#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, CompressedImage
from ultralytics import YOLO
import cv2
import numpy as np
import os
from ament_index_python.packages import get_package_share_directory

class YoloDetector(Node):
    def __init__(self):
        super().__init__('yolo_detector')

        # Find model path
        package_share_directory = get_package_share_directory('eesob_yolo')
        model_path = os.path.join(package_share_directory, 'models', 'eesob.onnx')
        self.get_logger().info(f"Loading YOLO ONNX model from: {model_path}")

        # Initialize YOLO model
        self.model = YOLO(model_path, task='detect')
        self.get_logger().info(f"Model loaded")


        # Subscriber to the compressed camera image
        self.compressed_image_sub = self.create_subscription(
            CompressedImage, 
            'camera/image_raw/compressed',
            self.compressed_image_callback,
            10
        )

        # Publisher for the detected electronic image
        self.detected_image_pub = self.create_publisher(
            CompressedImage, 
            'yolo/annotated_image/compressed', 
            10
        )

        self.get_logger().info('YOLO Detector node is ready!')

    def compressed_image_callback(self, msg):
        try: 
            # Decode the compressed image
            np_arr = np.frombuffer(msg.data, np.uint8)
            img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            # Run YOLO model on the image
            results = self.model.predict(source=img, conf=0.5, verbose=False)
            annotated_image = results[0].plot()

            # Compress the image
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 80]
            result, encimg = cv2.imencode('.jpg', annotated_image, encode_param)

            if result:
                # 4. Create and populate the CompressedImage message
                out_msg = CompressedImage()
                out_msg.header= msg.header
                out_msg.format = "jpeg"
                out_msg.data = np.array(encimg).tobytes()

            

                # Publish the annotated image
                self.detected_image_pub.publish(out_msg)
                self.get_logger().info('Publisher annotated image')

        except Exception as e:
            self.get_logger().error(f"Error processing image: {e}")

        





def main(args=None):
    rclpy.init(args=args)
    node = YoloDetector()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()