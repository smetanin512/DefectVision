import cv2
import numpy as np
from PyQt5.QtCore import (QThread, pyqtSignal, QMutex, pyqtSlot, QTimer)


class OutStream(QThread):
    def __init__(self):
        super().__init__()
        self.output_frame = None
        self.out_stream = None
        self.exit_flag = False
        self.mutex = QMutex()
        self.fps_counter = 0
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.reset_fps)
        self.timer.start()

    def run(self):
        self.mutex.lock()
        while not self.exit_flag:
            self.mutex.lock()
            if self.exit_flag:
                break
            if self.output_frame is not None:
                if self.out_stream is None:
                    h, w, _ = self.output_frame.shape
                    self.out_stream = cv2.VideoWriter(
                        # "appsrc ! videoconvert ! jpegenc ! tcpserversink host=94.26.229.85 port=5001",
                        
                        "appsrc ! videoconvert ! x264enc  pass=17 tune=zerolatency byte-stream=true ! h264parse ! mpegtsmux ! tcpserversink host=94.26.229.85 port=5001",
                        cv2.CAP_GSTREAMER,
                        0, 19, (w, h), True)
                self.out_stream.write(self.output_frame)
                self.fps_counter += 1

    def reset_fps(self):
        print('fps =', self.fps_counter)
        self.fps_counter = 0

    @pyqtSlot(np.ndarray)
    def set_output_frame(self, frame: np.ndarray):
        self.output_frame = frame.copy()
        self.mutex.unlock()

    def stop_output_stream(self):
        self.exit_flag = True
        self.mutex.unlock()