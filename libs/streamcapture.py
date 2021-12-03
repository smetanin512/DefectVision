from PyQt5.QtCore import (QThread, pyqtSignal, QMutex, pyqtSlot, QElapsedTimer)
import cv2
import numpy as np
from sys import platform


class StreamCapture(QThread):
    getframe = pyqtSignal(np.ndarray)

    def __init__(self, cam):
        super().__init__()
        self.camip = cam
        self.frame = None
        self.cap = None
        self.exit_flag = False
        self.timer = QElapsedTimer()

    def run(self):
        if platform == "linux" or platform == "linux2":
            self.cap = cv2.VideoCapture(self.camip)
        else:
            self.cap = cv2.VideoCapture(self.camip)
        self.sleeptime = 1000 // self.cap.get(cv2.CAP_PROP_FPS)
        self.timer.start()
        while not self.exit_flag:
            self.timer.restart()
            ret, self.frame = self.cap.read()
            if self.cap.get(cv2.CAP_PROP_POS_FRAMES) == self.cap.get(cv2.CAP_PROP_FRAME_COUNT):
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            if not ret:
                self.frame = self.show_empty_frame()
                self.msleep(40)
            else:
                if self.timer.elapsed() < self.sleeptime:
                    self.msleep(int(self.sleeptime - self.timer.elapsed()))
            self.getframe.emit(self.frame.copy())
        self.cap.release()

    def show_empty_frame(self):
        empty_frame = np.zeros([1080, 1920, 3], dtype=np.uint8)
        text = "Ошибка захвата с камеры!"
        FONT_SCALE = 1
        FONT_THICKNESS = 2
        (label_width, label_height), baseline = cv2.getTextSize(text, cv2.FONT_HERSHEY_COMPLEX, FONT_SCALE, FONT_THICKNESS)
        point = ((empty_frame.shape[1] - label_width) // 2 , (empty_frame.shape[0] - label_height) // 2 )
        cv2.putText(empty_frame, text, point, cv2.FONT_HERSHEY_COMPLEX, FONT_SCALE, (255, 255, 255), FONT_THICKNESS)
        return empty_frame

    def stop(self):
        self.exit_flag = True

    def get_current_frame(self, resize=False, size=(1280, 720)):
        self.mutex.lock()
        frame = self.frame.copy()
        if resize and self.frame.shape[0] > size[1]:
            frame = self.frame.copy()
            frame = cv2.resize(frame, size)
            self.mutex.unlock()
            return frame
        self.mutex.unlock()
        return frame.copy()

    def reopenStream(self, cam):
        if platform == "linux" or platform == "linux2":
            self.camip = "/dev/video" + str(cam)
            self.cap = cv2.VideoCapture(self.camip, cv2.CAP_V4L2)
        else:
            self.camip = 0
            self.cap = cv2.VideoCapture(self.camip)