import cv2
import pytesseract
import json
import time
import numpy as np
from pytesseract import Output
from PyQt5.QtCore import (QThread, pyqtSignal, QMutex, pyqtSlot, QTimer)

# cv2.namedWindow("Capture", cv2.WINDOW_NORMAL)
# cv2.resizeWindow("Capture", 1280, 720)
# last_detection_time = 0.0  # Время, когда в последний раз задетектился номер вагона
# yes_new_data = False  # Флаг о наличии задетекченных номеров
# url = "http://10.29.34.176:8080/video"
# history = []    # Сюда заносятся номера вагонов одного состава


class TextRecognition(QThread):
    get_text_frame = pyqtSignal(np.ndarray)

    def __init__(self):
        super().__init__()
        self.last_detection_time = 0.0  # Время, когда в последний раз задетектился номер вагона
        self.yes_new_data = False  # Флаг о наличии задетекченных номеров
        self.history = []  # Сюда заносятся номера вагонов одного состава
        self.current_image = None
        self.busy = False
        self.exit_flag = False
        self.mutex = QMutex()

    @pyqtSlot(np.ndarray)
    def set_frame(self, image):
        if not self.busy:
            self.current_image = image.copy()
            self.mutex.unlock()

    def stop_ocr(self):
        self.exit_flag = True
        self.mutex.unlock()

    def MakeJSON(self):
        dump = json.dumps(self.history)
        self.history.clear()
        # print(dump)
        self.yes_new_data = False

    def run(self):
        self.mutex.lock()
        while not self.exit_flag:
            self.mutex.lock()
            if self.exit_flag:
                break
            self.busy = True
            self.OCR(self.current_image)
            self.busy = False

    def OCR(self, image):
        # gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image = cv2.resize(image, (1920, 1080))
        image = image[450:-100,:]
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        threshold_img = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

        custom_config = r'-c tessedit_char_whitelist=0123456789 --oem 3 --psm 6'

        details = pytesseract.image_to_data(threshold_img, output_type=Output.DICT, config=custom_config, lang='eng')

        numbers = []
        total_boxes = len(details['text'])

        for nm in range(total_boxes):
            if len(details['text'][nm]) == 8:
                if details['text'][nm] not in numbers:
                    numbers.append(details['text'][nm])
                self.last_detection_time = time.time()
                self.yes_new_data = True

        for nm in numbers:
            if nm not in self.history:
                print(nm)
                self.history.append(nm)

        if len(numbers) == 0:
            if (time.time() - self.last_detection_time) > 30.0 and self.yes_new_data is True:
                MakeJSON()

        for sequence_number in range(total_boxes):
            if int(details['conf'][sequence_number]) > 30:
                (x, y, w, h) = (
                    details['left'][sequence_number], details['top'][sequence_number], details['width'][sequence_number],
                    details['height'][sequence_number])
                # threshold_img = cv2.rectangle(threshold_img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                image = cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        self.get_text_frame.emit(image)
        # cv2.imshow('Capture', image)

