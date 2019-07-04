from PyQt5 import QtWidgets, QtGui, QtCore
import cv2
import numpy as np
import yolo_detect

class RecordVideo(QtCore.QObject):
	image_data = QtCore.pyqtSignal(np.ndarray)
	text_signal = QtCore.pyqtSignal([str])

	def __init__(self, camera=0, parent=None):  # , [obj1]
		super().__init__(parent)
		self.camera = camera

		self.timer = QtCore.QBasicTimer()
		self.tracking = False
		self.objects = list()
		self.last_frame = 255 * np.ones((1000, 1000, 3), np.uint8)
		self.isDetected = False
		self.yolo_detect = False

	def start_recording(self):
		self.timer.start(0, self)

	def add_object(self, obj):
		self.objects.append(obj)

	def removeObject(self, text):
		for item in self.objects:
			if item.name == text:
				self.objects.remove(item)

	def timerEvent(self, event):
		if not self.tracking and not self.isDetected:  # event.timerId() != self.timer.timerId() or
			self.image_data.emit(self.last_frame)
			return

		read, img = self.camera.read()
		if read:
			if self.yolo_detect:
				self.yolo_detect = False
				self.yolo(img)
				# 	self.tracking = False

			self.detect(img)
			self.last_frame = img
		self.image_data.emit(self.last_frame)

	def yolo(self, image):
		start = yolo_detect.time.time()
		coco_objects = yolo_detect.find_electric_objects('yolo-coco',
														 yolo_detect.MIN_PROB,
														 yolo_detect.OVERLAP_THRESHHOLD, image)
		end = yolo_detect.time.time()
		for coco_object in coco_objects:
			coords = coco_object.coords
			cv2.rectangle(image, (coords[0], coords[1]), (coords[0] + coords[2], coords[1] + coords[3]), (0, 255, 0))
		self.objects = self.objects + init_obj_detection(coco_objects, image)


	def detect(self, img):
		for i in range(len(self.objects)):
			upd, obj = self.objects[i].tracker.update(img)
			if upd:
				x1 = (int(obj[0]), int(obj[1]))
				x2 = (int(obj[0] + obj[2]), int(obj[1] + obj[3]))
				self.objects[i].coords = x1 + x2
				if self.objects[i].borders and not self.objects[i].is_object_inside():
					self.text_signal.emit("WARNING: OBJECT IS OUTSIDE OF BORDERS")  # TODO: add time variable
					self.text_signal.emit("Borders: {}".format(self.objects[i].borders))
					self.text_signal.emit("Coord: {}".format(self.objects[i].coords))
				cv2.rectangle(img, x1, x2, (255, 0, 0), 2, 1)
				cv2.putText(img, self.objects[i].name, get_first_point(self.objects[i].coords),
							cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 255, 255))
			# if self.objects[i].borders:
			# 	cv2.rectangle(img, get_first_point(self.objects[i].borders),
			# 				  get_second_point(self.objects[i].borders),
			# 				  (0, 255, 0), 2, 1)
			else:
				self.objects[i].detect_obj(False)


class ObjectDetectionWidget(QtWidgets.QWidget, QtCore.QObject):
	coordinates_signal = QtCore.pyqtSignal(int, int, int, int)
	coordinates_signal_b = QtCore.pyqtSignal(int, int, int, int)

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
		self.border_p1 = self.Point()
		self.border_p2 = self.Point()
		self.drawing = False
		self._red = (0, 0, 255)
		self._green = (0, 255, 0)
		self._width = 2
		self.height_shearing = 1
		self.width_shearing = 1
		self.isDetected = False
		self.imageCV = None
		self.isTarget = True

	def image_data_slot(self, image_data):
		self.imageCV = image_data
		self.image = self.get_qimage(image_data)
		if self.drawing:
			if self.isTarget:
				self.drawTarget(image_data)
			else:
				self.drawBorder(image_data)

		self.height_shearing = self.image.size().height() / self.size().height()
		self.width_shearing = self.image.size().width() / self.size().width()
		self.update()

	def drawTarget(self, image_data):
		cv2.rectangle(image_data, (self.p1.x, self.p1.y), (self.p2.x, self.p2.y), self._red, self._width)

	def drawBorder(self, image_data):
		cv2.rectangle(image_data, (self.border_p1.x, self.border_p1.y), (self.border_p2.x, self.border_p2.y),
					  self._green, self._width)

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
		self.isDetected = False
		# TODO: change isTarget is isNotTarget
		if not self.isTarget:
			self.p1.x = int(event.x() * self.width_shearing)
			self.p1.y = int(event.y() * self.height_shearing)
		else:
			self.border_p1.x = int(event.x() * self.width_shearing)
			self.border_p1.y = int(event.y() * self.height_shearing)
		self.drawing = False

	def mouseReleaseEvent(self, event):
		if not self.isTarget:
			self.p2.x = int(event.x() * self.width_shearing)
			self.p2.y = int(event.y() * self.height_shearing)
			self.coordinates_signal.emit(self.p1.x, self.p1.y, self.p2.x, self.p2.y)
		else:
			self.border_p2.x = int(event.x() * self.width_shearing)
			self.border_p2.y = int(event.y() * self.height_shearing)
			self.coordinates_signal_b.emit(self.border_p1.x, self.border_p1.y, self.border_p2.x, self.border_p2.y)
		self.drawing = True
		self.isTarget = not self.isTarget


class TrackableObject:
	"""
	Class which
	"""
	tracker = None
	borders = None
	object_not_found = 0

	def __init__(self, name='Object', coords=None):
		self.name = name
		self.coords = tuple(coords)

	def init_tracker(self, image):
		self.tracker = create_tracker(1)
		init_track = self.tracker.init(image, self.coords)

	def is_object_inside(self):
		b_x1, b_y1, b_x2, b_y2 = self.borders
		x1, y1, x2, y2 = self.coords
		return (b_x1 < x1) and (b_y1 < y1) and (x2 < b_x2) and (y2 < b_y2)

	def detect_obj(self, ans):
		if not ans:
			self.object_not_found += 1
		else:
			self.object_not_found = 0

	# if self.object_not_found > 5:
	#     print("WARNING:{} IS NOT FOUND!!!".format(self.name))

	def set_borders(self, coords):
		self.borders = (coords[0], coords[1], coords[0] + coords[2], coords[1] + coords[3])


def create_tracker(index):
	# types of trackers
	tracker_types = ("MIL", "KCF", "Boosting", "CSRT", "MedianFlow", "MOSSE")
	# set type of tracker
	cur_type = tracker_types[index]

	if cur_type == "MIL":
		return cv2.TrackerMIL_create()
	elif cur_type == "KCF":
		# faster FPS throughput, but handles slightly lower
		# object tracking accuracy
		return cv2.TrackerKCF_create()
	elif cur_type == "Boosting":
		return cv2.TrackerBoosting_create()
	elif cur_type == "CSRT":
		# higher object tracking accuracy, low FPS throughput
		return cv2.TrackerCSRT_create()
	elif cur_type == "MedianFlow":
		return cv2.TrackerMedianFlow_create()
	elif cur_type == 'MOSSE':
		# perfect for pure speed
		return cv2.TrackerMOSSE_create()
	else:
		return cv2.TrackerMIL_create()


def init_obj_detection(objects_map, img):
	objects = []
	for coco_object in objects_map:
		obj = TrackableObject(coco_object.name, coco_object.coords)
		obj.init_tracker(img)
		objects.append(obj)
	return objects


def get_first_point(coords):
	return coords[0], coords[1]


def get_second_point(coords):
	return coords[2], coords[3]

# def detect(object_map, camera, img):
# 	objs = init_obj_detection(object_map, img)
# 	tracking(camera, objs)
