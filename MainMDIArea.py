import sys
from PyQt5.QtWidgets import *
from MDISubWindow    import MDISubWindow

 
class MainMDIArea(QMdiArea):
	def __init__(self):
		super().__init__()
		self.id_counter = 0
		

	def __len__(self):
		return len(self.subWindowList())

	def __getitem__(self, index):
		return self.subWindowList()[index]


	def add_sub_window(self):
		new_sub_window = MDISubWindow(win_id = "ID-%d" % (self.id_counter), name = "Untitled #%d" % (self.id_counter + 1))
		self.addSubWindow(new_sub_window)	
		self.id_counter += 1
		new_sub_window.showMaximized()
		return new_sub_window

	def remove_sub_window(self, window):
		self.removeSubWindow(window)


	def show_all_sub_window(self):
		for each_window in self.subWindowList():
			each_window.showMaximized()


	def hide_all_sub_window(self):
		for each_window in self.subWindowList():
			each_window.showMinimized()

	def add_plot_window(self):
		pass

	def add_table_window(self):
		pass
