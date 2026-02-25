#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import CompressedImage
from picamera2 import Picamera2
import cv2
import numpy as np

class CameraPublisher(Node):
    def __init__(self):
        super().__init__('camera_publisher')
        
        # Notice we are publishing to a /compressed topic now
        self.publisher_ = self.create_publisher(CompressedImage, 'camera/image_raw/compressed', 10)
        
        self.picam2 = Picamera2()
        self.picam2.configure(self.picam2.create_video_configuration(
            main={"size": (640, 480), "format": "RGB888"}
        ))
        self.picam2.start()
        
        # 0.1 seconds = 10 FPS
        self.timer = self.create_timer(0.2, self.timer_callback)
        self.get_logger().info('Publishing COMPRESSED video...')

    def timer_callback(self):
        try:
            # 1. Grab the frame
            frame = self.picam2.capture_array()
            
            # 2. Convert RGB to BGR (OpenCV expects BGR for JPEG compression)
            # frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
            # 3. Compress the image to JPEG format (Quality: 80%)
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 100]
            result, encimg = cv2.imencode('.jpg', frame, encode_param)
            
            if result:
                # 4. Create and populate the CompressedImage message
                msg = CompressedImage()
                msg.header.stamp = self.get_clock().now().to_msg()
                msg.header.frame_id = "camera_frame"
                msg.format = "jpeg"
                msg.data = np.array(encimg).tobytes()
                
                self.publisher_.publish(msg)
                
        except Exception as e:
            self.get_logger().warning(f'Failed to capture/compress frame: {e}')

    def __del__(self):
        if hasattr(self, 'picam2'):
            self.picam2.stop()

def main(args=None):
    rclpy.init(args=args)
    camera_publisher = CameraPublisher()
    try:
        rclpy.spin(camera_publisher)
    except KeyboardInterrupt:
        pass
    finally:
        camera_publisher.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()