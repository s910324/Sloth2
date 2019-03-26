import os
import sys
import math
from PyQt5.QtWidgets import *
from PyQt5.QtCore    import *


class EventTester(QWidget):

	def __init__(self):
		QWidget.__init__(self)
		self.resize(800, 800)


	def mousePressEvent (self, event):
		print("mousePressEvent", event.button())

	def mouseReleaseEvent (self, event):
		print("mouseReleaseEvent", event.button())
		
	def moveEvent(self, event):
		print("widget moveEvent")

	def enterEvent(self, event):
		print("enterEvent")

	def mouseMoveEvent(self, event):
		#the returned value is always Qt.NoButton for mouse move events.
		print("mouseMoveEvent:", event.button(), event.x(), event.y())

	def leaveEvent(self, event):
		print("leaveEvent")

def Debugger():
	app  = QApplication(sys.argv)
	form = EventTester()
	form.show()
	app.exec_()

Debugger()