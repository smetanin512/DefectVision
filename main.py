from ctypes import *
import random
import os
import cv2
import time
from libs.streamcapture import StreamCapture
from libs.detector import DefectDetector
from libs.out_stream import OutStream
from ui import MainForm
import argparse
from PyQt5.QtCore import QWaitCondition, Qt
from PyQt5.QtWidgets import QApplication
import sys

if __name__ == '__main__':
    app = QApplication(sys.argv)
    weights = os.path.join(os.getcwd(), 'data', 'yolov4-custom_last.weights')
    config_path = os.path.join(os.getcwd(), 'data', 'yolov4-custom.cfg')
    data_path = os.path.join(os.getcwd(), 'data', 'obj.data')
    form = MainForm()
    defect_detector = DefectDetector(config_path, data_path, weights)
    out_stream = OutStream()
    # defect_detector.get_output_frame.connect(form.mat2qimage)
    defect_detector.get_output_frame.connect(out_stream.set_output_frame)
    stream = StreamCapture(sys.argv[1])
    stream.getframe.connect(defect_detector.get_frame_for_detection)
    stream.start()
    out_stream.start()
    defect_detector.start()
    # form.showMaximized()
    ret = app.exec_()
    stream.stop()
    sys.exit(ret)