from ctypes import *
import random
import os
import cv2
import time
from libs.streamcapture import StreamCapture
from libs.detector import DefectDetector
from ui import MainForm
import argparse
from PyQt5.QtCore import QWaitCondition, Qt
from PyQt5.QtWidgets import QApplication
import sys


def parser():
    parser = argparse.ArgumentParser(description="YOLO Object Detection")
    parser.add_argument("--input", type=str, default=0,
                        help="video source. If empty, uses webcam 0 stream")
    parser.add_argument("--thresh", type=float, default=.25,
                        help="remove detections with confidence below this value")
    return parser.parse_args()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    weights = os.path.join(os.getcwd(), 'data', 'yolov4-custom_last.weights')
    config_path = os.path.join(os.getcwd(), 'data', 'yolov4-custom.cfg')
    data_path = os.path.join(os.getcwd(), 'data', 'obj.data')
    args = parser()
    form = MainForm()
    defect_detector = DefectDetector(config_path, data_path, weights)
    defect_detector.get_output_frame.connect(form.mat2qimage)
    stream = StreamCapture('ipaddres')
    stream.getframe.connect(defect_detector.get_frame_for_detection)
    stream.start()
    form.showMaximized()
    ret = app.exec_()
    stream.stop()
    sys.exit(ret)