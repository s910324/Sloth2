import os
import sys
import math
from PyQt5.QtWidgets import *
from PyQt5.QtCore    import *
from PyQt5.QtGui     import *
class CursorTracker(object):
	def __init__(self, parent):
		object.__init__(self)
		self.parent             = parent
		self.top_freeze_view    = None
		self.left_freeze_view   = None
		self.corner_freeze_view = None
		self.anchor             = QPoint()
		self.pivot              = QPoint()

	def set_anchor(self, cursor_event):
		assert isinstance(cursor_event, QMouseEvent)
		if cursor_event.button() == Qt.LeftButton:
			self.anchor.setX(cursor_event.x())
			self.anchor.setY(cursor_event.y())
			# connect to freezeview left click event
	
	def set_pivot(self, cursor_event):
		assert isinstance(cursor_event, QMouseEvent)
		if self.anchor.x(): #??????????? do work?
			self.pivot.setX(cursor_event.x())
			self.pivot.setY(cursor_event.y())
			self.parent.setSelection(QRect(self.anchor, self.pivot), QItemSelectionModel.ClearAndSelect)
			# connect to freezeview mouseMoveEvent if left mouse is clicked
			# QRect(topleft, bottomright)
				

	def clear_points(self, cursor_event):
		assert isinstance(cursor_event, QMouseEvent)
		if cursor_event.button() == Qt.LeftButton:
			self.anchor = QPoint()
			self.pivot  = QPoint()

	def rect_width(self):
		return abs(self.pivot.x - self.anchor.x)

	def rect_height(self):
		return abs(self.pivot.y - self.anchor.y)

class DictObject(object):
    def __init__(self, dict):
        self.__dict__ = dict


