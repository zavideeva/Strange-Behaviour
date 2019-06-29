# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.Qt import QWidget, QLabel, QPixmap, QThread, QImage, pyqtSignal, pyqtSlot, QApplication, QPushButton, QVBoxLayout, QListWidgetItem, QFileDialog
from PyQt5.QtCore import Qt
import sys
import os
import cv2
import numpy as np
import yolo_detect
import detect_object
import tf_video

YOLO_PATH = 'yolo-coco'
MIN_PROB = 0.1
MIN_THRESHHOLD = 0.2

objects_to_track = []
trackable_objects_list = []
first_img_read = True
first_img = None
k = True
frame_detect_delay = 50
current_frame = 0
window = None


class RecordVideo(QtCore.QObject):
    image_data = QtCore.pyqtSignal(np.ndarray)

    def __init__(self, camera_port=0, parent=None):
        super().__init__(parent)
        self.camera = cv2.VideoCapture(camera_port)
        global first_img, objects_to_track, trackable_objects_list
        read, img = self.camera.read()
        first_img = img
        trackable_objects_list = self.find_trackable_objects(first_img)
        self.timer = QtCore.QBasicTimer()
        self.tracking = True
        self.last_frame = 255 * np.ones((1000, 1000, 3), np.uint8)

    def start_recording(self):
        self.timer.start(0, self)

    def timerEvent(self, event):
        if event.timerId() != self.timer.timerId():
            return

        if not self.tracking:
            self.image_data.emit(self.last_frame)
            return

        read, img = self.camera.read()
        if read:
            global current_frame, frame_detect_delay, trackable_objects_list, objects_to_track
            current_frame += 1
            if current_frame == frame_detect_delay:
                trackable_objects_list = self.find_trackable_objects(img)
                current_frame = 0
                window.item_list.clear()
                for obj in trackable_objects_list:
                    window.item_list.addItem(obj.name)
            self.last_frame = img
            self.image_data.emit(img)

    @staticmethod
    def find_trackable_objects(image):
        return detect_object.init_obj_detection(
            yolo_detect.find_electric_objects(YOLO_PATH, MIN_PROB, MIN_THRESHHOLD, image),#tf_video.find_coco_objects(image),
            image)


class FaceDetectionWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.image = QtGui.QImage()
        self._red = (0, 0, 255)
        self._width = 2
        self._min_size = (30, 30)

    def image_data_slot(self, img):
        global trackable_objectss_list, window
        dict = {}
        for i in range(len(trackable_objects_list)):
            # change listWidget
            obj_name = trackable_objects_list[i].name
            if dict.get(obj_name, -1) == -1:
                dict[obj_name] = 1
            else:
                dict[obj_name] += 1
            # draw rectangles
            upd, obj = trackable_objects_list[i].tracker.update(img)
            if upd:
                x1 = (int(obj[0]), int(obj[1]))
                x2 = (int(obj[0] + obj[2]), int(obj[1] + obj[3]))
                trackable_objects_list[i].coords = x1 + x2
                if trackable_objects_list[i].borders and not trackable_objects_list[i].is_object_inside():
                    print("WARNING: OBJECT IS OUTSIDE OF BORDERS")
                    print("Borders: ", trackable_objects_list[i].borders)
                    print("Coord: ", trackable_objects_list[i].coords)
                cv2.rectangle(img, x1, x2, (255, 0, 0), 2)
                cv2.putText(img, trackable_objects_list[i].name, detect_object.get_first_point(trackable_objects_list[i].coords),
                            cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 255, 255))
                if trackable_objects_list[i].borders:
                    cv2.rectangle(img, detect_object.get_first_point(trackable_objects_list[i].borders),
                                  detect_object.get_second_point(trackable_objects_list[i].borders), (0, 255, 0), 2, 1)
            else:
                trackable_objects_list[i].detect_obj(False)

        self.image = self.get_qimage(img)
        if self.image.size() != self.size():
            self.setFixedSize(self.image.size())

        self.update()

    def get_qimage(self, image: np.ndarray):
        height, width, colors = image.shape
        bytesPerLine = 3 * width
        QImage = QtGui.QImage

        image = QImage(image.data,
                       width,
                       height,
                       bytesPerLine,
                       QImage.Format_RGB888)

        image = image.rgbSwapped()
        return image

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.drawImage(0, 0, self.image)
        self.image = QtGui.QImage()


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(733, 585)

        self.centralwidget = QtWidgets.QWidget(MainWindow)

        #layouts
        self.layout_main = QtWidgets.QVBoxLayout()
        self.layout_cam = QtWidgets.QHBoxLayout()
        self.layout_up = QtWidgets.QHBoxLayout()
        self.layout_buttons = QtWidgets.QVBoxLayout()
        self.layout_play = QtWidgets.QHBoxLayout()
        self.layout_add = QtWidgets.QHBoxLayout()

        # Push buttons
        self.play_button = QtWidgets.QPushButton('Play')

        self.layout_main = QtWidgets.QVBoxLayout(self.centralwidget)


        self.face_det_widget = FaceDetectionWidget()

        # pass
        self.qle = QtWidgets.QLineEdit(self)
        self.item_list = QtWidgets.QListWidget()
        self.logs = QtWidgets.QListWidget()
        self.label = QtWidgets.QLabel()

        self.layout_cam.addWidget(self.face_det_widget)
        self.layout_up.addLayout(self.layout_cam, stretch=4)  # TODO: try stretch =5
        self.layout_buttons.addLayout(self.layout_play)

        self.layout_play.addWidget(self.play_button)
        self.layout_add.addWidget(self.qle)
        self.layout_buttons.addLayout(self.layout_add)
        self.layout_buttons.addWidget(self.item_list, 0, QtCore.Qt.AlignLeft)


        self.layout_up.addLayout(self.layout_buttons, stretch=1)
        self.layout_main.addLayout(self.layout_up, stretch=3)

        self.layout_main.addWidget(self.logs, stretch=1)


        self.centralwidget.setLayout(self.layout_main)
        MainWindow.setCentralWidget(self.centralwidget)

#########
        self.record_video = RecordVideo('videos/1.mpg')
        image_data_slot = self.face_det_widget.image_data_slot
        self.record_video.image_data.connect(image_data_slot)
        self.record_video.start_recording()

        self.image = QImage()
        self.trainOpenImg = QLabel()
##########

        #connections
        #TODO write connect functions for buttons
        self.play_button.clicked.connect(self.play)


        self.retranslateUi(MainWindow)

        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))

    def play(self):
        self.record_video.tracking = not self.record_video.tracking


class ExampleApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)


def main():
    global window
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = ExampleApp()  # Создаём объект класса ExampleApp
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение


if __name__ == '__main__':
    main()
