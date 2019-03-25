import sys
from PyQt5.QtWidgets import *


 
class ToolBar(QToolBar):
	def __init__(self, title, action_list = None):
		super().__init__()
		self.setWindowTitle(title)
		self.set_actions(action_list)


	def set_actions(self, action_list = None):

		if action_list:
			
			for each in action_list:

				text, icon_path, short_cut, function = each
				new_action = QAction(self)

				if text:
					new_action.setText(text)

				if icon_path:
					new_action.setIcon(QIcon(icon_path))

				if short_cut:
					new_action.setShortcut(short_cut)

				if function:
					new_action.triggered.connect(function)

				self.addAction(new_action)