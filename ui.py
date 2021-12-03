import numpy as np
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QDockWidget, QVBoxLayout, QPushButton, QGridLayout,
                             QComboBox, QLineEdit, QMessageBox, QInputDialog, QHBoxLayout, QCheckBox)
from PyQt5.QtGui import (QPixmap, QImage, QFont, QPainter, QPainterPath, QPen, QBrush, QPalette, QKeyEvent)
from PyQt5.QtCore import Qt, QSize, QRectF, pyqtSlot, pyqtSignal, QWaitCondition
import cv2
import imutils


class MainForm(QWidget):

    def __init__(self):
        super().__init__()
        self.current_frame = None
        self.counter = 0
        self.initUI()

    # инициализируем UI
    def initUI(self):
        self.screen_resolution = QApplication.desktop().availableGeometry()
        self.move(self.screen_resolution.width() // 2, 0)
        self.resize(self.screen_resolution.width() // 2, self.screen_resolution.height())

        # label для отображения изображения с микроскопа
        self.frame_label = QLabel(self)
        self.frame_label.move(0, 0)
        self.frame_label.resize(self.screen_resolution.width() // 2,self.screen_resolution.height() // 2)

        self.text_frame_label = QLabel(self)
        self.text_frame_label.move(0, self.screen_resolution.height() // 2)
        self.text_frame_label.resize(self.screen_resolution.width() // 2, self.screen_resolution.height() // 2)


    @pyqtSlot(np.ndarray)
    def mat2qimage(self, image: np.ndarray):
        image = image[750:1400,200:-200]
        self.current_frame = image.copy()
        # image= cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
        rgbImage = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        # rgbImage = cv2.resize(rgbImage, (self.frame_label.size().width(),
        #                                  self.frame_label.size().height()))
        rgbImage = imutils.resize(rgbImage, height=self.frame_label.height())
        h, w, ch = rgbImage.shape
        bytesPerLine = ch * w
        result_image = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
        self.frame_label.setPixmap(QPixmap.fromImage(result_image))

    @pyqtSlot(np.ndarray)
    def set_text_frame(self, image: np.ndarray):
        rgbImage = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        # rgbImage = cv2.resize(rgbImage, (self.frame_label.size().width(),
        #                                  self.frame_label.size().height()))
        rgbImage = imutils.resize(rgbImage, height=self.text_frame_label.height())
        h, w, ch = rgbImage.shape
        bytesPerLine = ch * w
        result_image = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
        self.text_frame_label.setPixmap(QPixmap.fromImage(result_image))

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            filename = str(self.counter) + ('1' if self.counter % 2 == 0 else '2')
            cv2.imwrite(filename + '.jpg', self.current_frame)
            self.counter += 1