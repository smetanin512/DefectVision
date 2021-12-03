import numpy as np
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QDockWidget, QVBoxLayout, QPushButton, QGridLayout,
                             QComboBox, QLineEdit, QMessageBox, QInputDialog, QHBoxLayout, QCheckBox)
from PyQt5.QtGui import (QPixmap, QImage, QFont, QPainter, QPainterPath, QPen, QBrush, QPalette, QKeyEvent)
from PyQt5.QtCore import Qt, QSize, QRectF, pyqtSlot, pyqtSignal, QWaitCondition
from PIL import Image
import cv2
import os


class MainForm(QWidget):

    def __init__(self):
        super().__init__()
        self.current_frame: np.ndarray = None
        self.initUI()

    # инициализируем UI
    def initUI(self):
        self.screen_resolution = QApplication.desktop().availableGeometry()

        # label для отображения изображения с микроскопа
        self.frame_label = QLabel(self)
        self.frame_label.move(0, 0)
        self.frame_label.resize(self.screen_resolution.width(),self.screen_resolution.height())

    @pyqtSlot(np.ndarray)
    def mat2qimage(self, image: np.ndarray):
        self.current_frame = image.copy()
        rgbImage = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        rgbImage = cv2.resize(rgbImage, (self.frame_label.size().width(),
                                         self.frame_label.size().height()))
        h, w, ch = rgbImage.shape
        bytesPerLine = ch * w
        result_image = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
        self.frame_label.setPixmap(QPixmap.fromImage(result_image))
