# from ctypes import *
import darknet
from PyQt5.QtCore import (QThread, pyqtSignal, QMutex, pyqtSlot)
import cv2
import numpy as np


class DefectDetector(QThread):
    get_output_frame = pyqtSignal(np.ndarray)

    def __init__(self, config_path, data_path, weights):
        super().__init__()
        self.network, self.class_names, self.class_colors = darknet.load_network(
            config_path, data_path, weights, batch_size=1
        )
        self.darknet_width = darknet.network_width(self.network)
        self.darknet_height = darknet.network_height(self.network)
        self.current_frame = None
        self.busy = False
        self.exit_flag = False
        self.mutex = QMutex()
        self.thresh = 0.95

    def run(self):
        self.mutex.lock()
        while not self.exit_flag:
            self.mutex.lock()
            if self.exit_flag:
                break
            self.busy = True
            frame_rgb = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2RGB)
            frame_resized = cv2.resize(frame_rgb, (self.darknet_width, self.darknet_height),
                                       interpolation=cv2.INTER_LINEAR)
            img_for_detect = darknet.make_image(self.darknet_width, self.darknet_height, 3)
            darknet.copy_image_from_bytes(img_for_detect, frame_resized.tobytes())
            detections = darknet.detect_image(self.network, self.class_names, img_for_detect, thresh=self.thresh)
            darknet.free_image(img_for_detect)
            detections_adjusted = []
            if self.current_frame is not None:
                for label, confidence, bbox in detections:
                    bbox_adjusted = self.convert2original(self.current_frame, bbox)
                    detections_adjusted.append((str(label), confidence, bbox_adjusted))
                self.current_frame = darknet.draw_boxes(detections_adjusted, self.current_frame, self.class_colors)
                self.get_output_frame.emit(self.current_frame.copy())
            self.busy = False

    @pyqtSlot(np.ndarray)
    def get_frame_for_detection(self, frame: np.ndarray):
        if not self.busy:
            self.current_frame = frame.copy()
            self.mutex.unlock()

    def stop_detection(self):
        self.exit_flag = True
        self.mutex.unlock()

    def convert2relative(self, bbox):
        """
        YOLO format use relative coordinates for annotation
        """
        x, y, w, h = bbox
        _height = self.darknet_height
        _width = self.darknet_width
        return x / _width, y / _height, w / _width, h / _height

    def convert2original(self, image, bbox):
        x, y, w, h = self.convert2relative(bbox)

        image_h, image_w, __ = image.shape

        orig_x = int(x * image_w)
        orig_y = int(y * image_h)
        orig_width = int(w * image_w)
        orig_height = int(h * image_h)

        bbox_converted = (orig_x, orig_y, orig_width, orig_height)

        return bbox_converted