import sys
from PyQt5.QtWidgets import *

 
class MDISubWindow(QWidget):
	def __init__(self, win_id, name):
		super().__init__()
		self.__win_id = win_id
		self.__name   = name
		self.__lock   = False
		self.__init_ui__()

	def __init_ui__(self):
		self.setWindowTitle(self.__name)

	def get_id(self):
		return self.__win_id
		
	def set_id(self, new_id):
		self.__win_id = new_id

	def get_name(self):
		return self.__name

	def set_name(self, name):
		self.__name = name


	def closeEvent(self, event):
		if self.__lock:
			self.showMinimized()
			event.ignore()
			
		else:
			event.accept()
			self.showMaximized()

	def unlock(self) :
		self.__lock = False

	def lock(self) :
		self.__lock = True

if __name__ == '__main__':
	app = QApplication(sys.argv)
	frame = MDISubWindow(0, "name")
	frame.showMaximized()    
	app.exec_()
	sys.exit
