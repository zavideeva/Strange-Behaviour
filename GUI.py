from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtGui import QPainter, QColor
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

	def image_data_slot(self, image_data):
		self.image = self.get_qimage(image_data)
		# if self.image.size() != self.size():
		# self.setFixedSize(self.image.size())

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
		# painter.fillRect(event.rect(), QtGui.QBrush(self.color))
		self.image = QtGui.QImage()

		self.update()

	def mousePressEvent(self, event):
		self.p1.x = event.x()
		self.p1.y = event.y()
		self.drawing = False

	def mouseReleaseEvent(self, event):
		self.p2.x = event.x()
		self.p2.y = event.y()
		self.drawing = True

		print("{} {}, {} {}".format(self.p1.x, self.p1.y, self.p2.x, self.p2.y))

	# def paintEvent(self, e):
	# 	if self.drawing:
	# 		qp = QPainter()
	# 		qp.begin(self)
	# 		self.drawRectangles(qp)
	# 		qp.end()
	#
	# def drawRectangles(self, qp):
	# 	col = QColor(0, 0, 0)
	# 	col.setNamedColor('#6e6e6e')
	# 	qp.setPen(col)
	#
	# 	qp.setBrush(QColor(50, 100, 50))
	# 	qp.drawRect(self.p1.x, self.p1.y, self.p2.x, self.p2.y)
# TODO: cooridnates within frame
