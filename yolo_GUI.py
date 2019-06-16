import sys
from GUI import *
from PyQt5 import QtCore, QtWidgets
import cv2

class MainWidget(QtWidgets.QWidget):

	def __init__(self, parent=None):
		super().__init__(parent)
		self.x1 = None
		self.y1 = None
		self.x2 = None
		self.y2 = None

		#  Video Source
		cam = cv2.VideoCapture("video.mp4")

		#  Create object detection widget and record video object
		self.object_detection_widget = ObjectDetectionWidget()
		self.record_video = RecordVideo(cam)
		#  layouts
		self.layout_main = QtWidgets.QVBoxLayout()
		self.layout_cam = QtWidgets.QHBoxLayout()
		self.layout_up = QtWidgets.QHBoxLayout()
		self.layout_buttons = QtWidgets.QVBoxLayout()
		self.layout_play = QtWidgets.QHBoxLayout()
		self.layout_add = QtWidgets.QHBoxLayout()

		# Push buttons
		self.play_button = QtWidgets.QPushButton('Play')
		self.search_button = QtWidgets.QPushButton('Search')
		self.add_button = QtWidgets.QPushButton('Add')
		self.remove = QtWidgets.QPushButton('remove selected')

		self.qle = QtWidgets.QLineEdit(self)
		self.item_list = QtWidgets.QListWidget()
		self.logs = QtWidgets.QListWidget()
		self.label = QtWidgets.QLabel()

		self.layout_cam.addWidget(self.object_detection_widget)
		self.layout_up.addLayout(self.layout_cam, stretch=4)  # TODO: try stretch =5
		self.layout_buttons.addLayout(self.layout_play)

		self.layout_play.addWidget(self.play_button, 0, QtCore.Qt.AlignLeft)
		self.layout_play.addWidget(self.search_button, 0, QtCore.Qt.AlignRight)

		self.layout_add.addWidget(self.add_button, 0, QtCore.Qt.AlignLeft)
		self.layout_add.addWidget(self.qle)

		self.layout_buttons.addLayout(self.layout_add)
		self.layout_buttons.addWidget(self.item_list, 0, QtCore.Qt.AlignLeft)
		self.layout_buttons.addWidget(self.remove)

		self.layout_up.addLayout(self.layout_buttons, stretch=1)
		self.layout_main.addLayout(self.layout_up, stretch=3)
		self.layout_main.addWidget(self.logs, stretch=1)

		# signal connection of widgets
		image_data_slot = self.object_detection_widget.image_data_slot
		self.object_detection_widget.coordinates_signal.connect(self.set_coordinates)
		self.record_video.image_data.connect(image_data_slot)
		self.record_video.image_data.connect(self.create_object)
		self.record_video.text_signal.connect(self.addLog)
		self.record_video.start_recording()

		# connection button with signal
		self.play_button.clicked.connect(self.play)
		# self.play_button.clicked.connect(self.detected)
		self.add_button.clicked.connect(self.detected)
		self.remove.clicked.connect(self.removeSelected)
		self.add_button.clicked.connect(self.addItem)

		self.setLayout(self.layout_main)

	# add new item to list
	def addItem(self):
		if self.qle.text().__len__() != 0 and self.x1 is not None:
			text = "{}: p1.x:{} p1.y:{} p2.x:{} p2.y:{}".format(self.qle.text(), self.x1, self.y1, self.x2, self.y2)
			self.item_list.addItem(text)

	def create_object(self, frame):
		if self.object_detection_widget.isDetected and self.x1 is not None:
			print("I am here")
			r1 = self.x1, self.y1
			r2 = self.x2, self.y2
			r = (self.x1, self.y1, int(self.x2 - self.x1), int(self.y2 - self.y1))
			obj1 = TrackableObject("Object", r)
			obj1.init_tracker(frame)
			cv2.imshow('title', frame)
			# b = cv2.selectROI("Borders", frame)
			obj1.set_borders(r)
			self.record_video.add_object(obj1)

			# cv2.rectangle(frame, r1, r2, (0, 255, 0), 2, 1)

	def set_coordinates(self, x1, y1, x2, y2):
		self.x1 = x1
		self.y1 = y1
		self.x2 = x2
		self.y2 = y2

	def addLog(self, text):
		self.logs.addItem(text)

	def detected(self):
		self.record_video.isDetected = not self.record_video.isDetected
		self.object_detection_widget.isDetected = not self.object_detection_widget.isDetected
	def removeSelected(self):
		selected = self.item_list.selectedItems()
		if selected == None: return
		for item in selected:
			self.item_list.takeItem(self.item_list.row(item))

	def play(self):
		self.record_video.tracking = not self.record_video.tracking


def main():
	app = QtWidgets.QApplication(sys.argv)
	app.setStyle('Oxygen')  # "Fusion" and "Breeze" are also fine
	main_window = QtWidgets.QMainWindow()

	# create an instance of class MainWidget
	main_widget = MainWidget()

	main_window.setCentralWidget(main_widget)
	main_window.showMaximized()
	sys.exit(app.exec_())


if __name__ == '__main__':
	main()
# cam.release()
# cv2.destroyAllWindows()
