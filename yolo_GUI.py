import sys
from GUI import ObjectDetectionWidget, RecordVideo
from PyQt5 import QtWidgets, QtCore


class MainWidget(QtWidgets.QWidget):
	def __init__(self, parent=None):
		super().__init__(parent)

		self.object_detection_widget = ObjectDetectionWidget()
		self.record_video = RecordVideo()

		image_data_slot = self.object_detection_widget.image_data_slot
		self.record_video.image_data.connect(image_data_slot)
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

		self.search_button = QtWidgets.QPushButton('Search')
		self.layout_buttons.addWidget(self.search_button, 0, QtCore.Qt.AlignLeft)

		# self.add_button.clicked.connect(self.mousePressEvent(Qt.QEvent.MouseButtonPress))
		# self.qle.textChanged[str].connect(self.onChanged)

		self.layout_add = QtWidgets.QHBoxLayout()
		self.add_button = QtWidgets.QPushButton('Add')
		self.layout_add.addWidget(self.add_button, 0, QtCore.Qt.AlignLeft)

		self.qle = QtWidgets.QLineEdit(self)
		self.layout_add.addWidget(self.qle)

		self.layout_buttons.addLayout(self.layout_add)

		self.item_list = QtWidgets.QListWidget()
		self.layout_buttons.addWidget(self.item_list, 0, QtCore.Qt.AlignLeft)

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
