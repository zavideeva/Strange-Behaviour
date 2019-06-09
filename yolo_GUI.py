import sys
from GUI import *
from PyQt5 import QtWidgets, QtCore


# ok, frame = cam.read()
#
# r = cv2.selectROI("Tracking object", frame)
# r1 = (int(r[0]), int(r[1]))
# r2 = (int(r[0] + r[2]), int(r[1] + r[3]))
# obj1 = TrackableObject("Object", r)
# obj1.init_tracker(frame)
# cv2.rectangle(frame, r1, r2, (0, 255, 0), 2, 1)
# b = cv2.selectROI("Borders", frame)
# obj1.set_borders(b)

class MainWidget(QtWidgets.QWidget):
	def __init__(self, parent=None):

		super().__init__(parent)

		cam = cv2.VideoCapture("video.mp4")
		self.object_detection_widget = ObjectDetectionWidget()
		self.object_detection_widget.coordinates_signal.connect(self.coordinates)
		self.record_video = RecordVideo(cam)  # , [obj1]

		image_data_slot = self.object_detection_widget.image_data_slot
		self.record_video.image_data.connect(image_data_slot)

		self.record_video.text_signal.connect(self.addLog)
		self.record_video.start_recording()

		# main layouts
		self.layout_main = QtWidgets.QVBoxLayout()

		self.layout_cam = QtWidgets.QHBoxLayout()
		self.layout_cam.addWidget(self.object_detection_widget)

		# self.layout_main.addLayout(self.layout_cam)
		self.layout_up = QtWidgets.QHBoxLayout()
		self.layout_up.addLayout(self.layout_cam, stretch=4)

		# layout for buttons
		self.layout_buttons = QtWidgets.QVBoxLayout()

		self.layout_play = QtWidgets.QHBoxLayout()

		self.play_button = QtWidgets.QPushButton('Play')
		self.layout_play.addWidget(self.play_button, 0, QtCore.Qt.AlignLeft)
		self.play_button.clicked.connect(self.play)

		self.search_button = QtWidgets.QPushButton('Search')
		self.layout_play.addWidget(self.search_button, 0, QtCore.Qt.AlignRight)

		self.layout_buttons.addLayout(self.layout_play)

		self.layout_add = QtWidgets.QHBoxLayout()
		self.add_button = QtWidgets.QPushButton('Add')
		self.layout_add.addWidget(self.add_button, 0, QtCore.Qt.AlignLeft)
		self.add_button.clicked.connect(self.detected)
		self.qle = QtWidgets.QLineEdit(self)
		self.layout_add.addWidget(self.qle)

		self.layout_buttons.addLayout(self.layout_add)

		self.item_list = QtWidgets.QListWidget()
		self.layout_buttons.addWidget(self.item_list, 0, QtCore.Qt.AlignLeft)

		self.remove = QtWidgets.QPushButton('remove selected')
		self.layout_buttons.addWidget(self.remove)

		self.remove.clicked.connect(self.removeSelected)
		self.add_button.clicked.connect(self.addItem)

		self.string = "face detected"  # TODO: change it later
		self.logs = QtWidgets.QListWidget()
		self.logs.addItem(self.string)

		self.label = QtWidgets.QLabel()
		self.label.setText("hel")

		self.layout_up.addLayout(self.layout_buttons, stretch=1)

		self.layout_main.addLayout(self.layout_up, stretch=3)
		self.layout_main.addWidget(self.logs, stretch=1)

		self.setLayout(self.layout_main)

		self.addLog("hello there")

	# add new item to list
	def addItem(self):
		self.item_list.addItem(self.qle.text())

	def addLog(self, text):
		self.logs.addItem(text)

	def coordinates(self, x1, y1, x2, y2):
		text = "p1.x:{} p1.y:{} p2.x:{} p2.y:{}".format(x1, y1, x2, y2)
		self.addLog(text)

	def detected(self):
		self.object_detection_widget.isDetected = True

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
