import os
import sys
import math
from PyQt5.QtWidgets import *
from PyQt5.QtCore    import *

class CursorTracker(object):
	def __init__(self, parent):
		object.__init__(self)
		self.parent             = parent
		self.top_freeze_view    = None
		self.left_freeze_view   = None
		self.corner_freeze_view = None
		self.anchor             = DictObject({"x"  : None,  "y" : None})
		self.pivot              = DictObject({"x"  : None,  "y" : None})

	def set_anchor(self, cursor_event):
		assert isinstance(cursor_event, PyQt5.QtGui.QMouseEvent)
		self.anchor.x, self.anchor.y = cursor_event.x(), cursor_event.y()
	




	def rect_width(self):
		return abs(self.pivot.x - self.anchor.x)

	def rect_height(self):
		return abs(self.pivot.y - self.anchor.y)

class DictObject(object):
    def __init__(self, dict):
        self.__dict__ = dict


