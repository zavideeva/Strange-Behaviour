from PyQt5 import QtWidgets, QtGui, QtCore
import cv2
import numpy as np


class RecordVideo(QtCore.QObject):
	image_data = QtCore.pyqtSignal(np.ndarray)

	def __init__(self, camera_port=0, parent=None):
		super().__init__(parent)
		self.camera = cv2.VideoCapture(camera_port)

		self.timer = QtCore.QBasicTimer()

	def start_recording(self):
		self.timer.start(0, self)

	def timerEvent(self, event):
		if event.timerId() != self.timer.timerId():
			return

		read, data = self.camera.read()
		if read:
			self.image_data.emit(data)


class ObjectDetectionWidget(QtWidgets.QWidget):
	class Point():
		def __init__(self):
			self.x = 0
			self.y = 0

		def setPoint(self, x, y):
			self.x = x
			self.y = y

	def __init__(self, parent=None):
		super().__init__(parent)
		self.setMouseTracking(True)
		self.image = QtGui.QImage()
		self.p1 = self.Point()
		self.p2 = self.Point()
		self.drawing = False
		self._red = (0, 0, 255)
		self._width = 2

		self.height_shearing = 1072 / 642
		self.width_shearing = 517 / 488

		print("{} {}".format(self.height_shearing, self.width_shearing))

	def image_data_slot(self, image_data):
		if self.drawing:
			# for (x, y, w, h) in faces: #TODO: add ability to draw many rectangles by storing coordinates in list
			# x1, y1 = self.frameGeometry().topLeft().x(), self.frameGeometry().topLeft().y()
			# x2, y2 = self.frameGeometry().bottomRight().x(), self.frameGeometry().bottomRight().y()
			x1, y1, x2, y2 = 0, 0, 642, 488
			if x1 <= self.p1.x and y1 <= self.p1.y and x2 >= self.p2.x and y2 >= self.p2.y:
				cv2.rectangle(image_data, (self.p1.x, self.p1.y), (self.p2.x, self.p2.y), self._red, self._width)

		self.image = self.get_qimage(image_data)
		self.update()

	def get_qimage(self, image: np.ndarray):
		height, width, colors = image.shape
		bytesPerLine = 3 * width
		QImage = QtGui.QImage

		image = QImage(image.data, width, height, bytesPerLine, QImage.Format_RGB888)

		image = image.rgbSwapped()
		return image

	def paintEvent(self, event):
		painter = QtGui.QPainter(self)
		painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform)
		painter.drawImage(self.rect(), self.image)
		self.image = QtGui.QImage()

		self.update()

	def mousePressEvent(self, event):
		self.p1.x = int(event.x() / self.height_shearing)  # + 9
		self.p1.y = int(event.y() / self.width_shearing)  # + 9
		self.drawing = False

	def mouseReleaseEvent(self, event):
		self.p2.x = int(event.x() / self.height_shearing)
		self.p2.y = int(event.y() / self.width_shearing)
		self.drawing = True

# TODO: cooridnates within frame
