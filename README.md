# Electronic Components Detection with YOLO & ROS 2

Real-time detection of electronic components using a **YOLOv26** model running on a **Raspberry Pi** with **ROS 2**. The project is built as a modular two-node pipeline — one node captures frames from the Pi camera, and the other runs inference — communicating over compressed image topics.

> While this project targets electronic components, the pipeline is **fully generic** and can be adapted to any object detection task by simply swapping the YOLO model.

---

## Architecture

```
┌──────────────┐  CompressedImage  ┌──────────────┐  CompressedImage
│              │ ───────────────►  │              │ ───────────────►  Subscribers
│  Camera Node │   /camera/image   │ YOLO Detector│   /yolo/annotated  (rqt, web, etc.)
│              │   _raw/compressed │              │   _image/compressed
└──────────────┘                   └──────────────┘
     picamera2                        ultralytics
```

The two ROS 2 nodes run independently and communicate via standard `sensor_msgs/CompressedImage` topics, meaning you can replace either end without touching the other.

---

## Packages

### `eesob_camera`

Camera capture node for the Raspberry Pi.

| Detail | Value |
|---|---|
| **Node name** | `camera_publisher` |
| **Publishes** | `camera/image_raw/compressed` (`CompressedImage`) |
| **Resolution** | 640 x 480 |
| **Frame rate** | ~5 FPS |
| **Encoding** | JPEG |

Uses `picamera2` to grab frames and `cv2.imencode` to compress them before publishing.

### `eesob_yolo`

YOLO inference node that subscribes to the camera feed and publishes annotated detections.

| Detail | Value |
|---|---|
| **Node name** | `yolo_detector` |
| **Subscribes** | `camera/image_raw/compressed` (`CompressedImage`) |
| **Publishes** | `yolo/annotated_image/compressed` (`CompressedImage`) |
| **Model** | `eesob.onnx` (YOLOv26, shipped in `models/`) |
| **Confidence** | >= 0.50 |

The `.pt` weights are also included if you want to retrain or export to a different format.

## Tested Hardware

- Raspberry Pi 4
- Raspberry Pi Camera Module Rev 1.3

---

## Dependencies

- **Ubuntu 24** on Raspberry Pi
- **ROS 2** (tested on Jazzy)
- **Python 3**
- `picamera2` — Raspberry Pi camera interface
- `opencv-python` (`cv2`)
- `numpy`
- `ultralytics` — YOLO runtime

---

## Usage

Run the camera node on the Raspberry Pi:

```bash
ros2 run eesob_camera camera_node
```

In a second terminal, launch the detector:

```bash
ros2 run eesob_yolo yolo_detector
```

To view the annotated output you can use any image viewer that supports compressed topics, for example:

```bash
ros2 run rqt_image_view rqt_image_view
# then select /yolo/annotated_image/compressed
```

---

## Adapting to Other Objects

1. **Train** a YOLO model on your own dataset using the [Ultralytics docs](https://docs.ultralytics.com/).
2. **Export** to ONNX:
   ```python
   from ultralytics import YOLO
   model = YOLO("your_model.pt")
   model.export(format="onnx")
   ```
3. **Replace** the file at `eesob_yolo/models/eesob.onnx` with your exported model.
4. Run the pipeline — no code changes needed.

---

## Repository Structure

```
src/
├── eesob_camera/           # Camera capture package
│   └── eesob_camera/
│       └── camera_node.py  # Picamera2 -> CompressedImage publisher
│
└── eesob_yolo/             # YOLO detection package
    ├── eesob_yolo/
    │   └── yolo_detector.py  # YOLO inference subscriber/publisher
    └── models/
        ├── eesob.onnx        # ONNX model (used at runtime)
        └── eesob.pt          # PyTorch weights (for retraining/export)
```

---

## Related Projects

- [EESOB](https://github.com/yacin-hamdi/EESOB) — Dataset collection and model training pipeline used to produce the YOLOv26 weights shipped in this project.
- [android_eesob](https://github.com/yacin-hamdi/android_eesob) — An Android application for electronic component detection using the same YOLO model, offering a mobile alternative to the Raspberry Pi pipeline.

---

## License

This project is licensed under the [MIT License](LICENSE).
