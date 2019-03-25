import os
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore    import *
from PyQt5.QtGui     import *

class HHeaderItem(object):
	def __init__(self, number = -1, axis = '-', name = '', function = None, parent = None):
		super(HHeaderItem, self).__init__(parent)
		self.number   = number
		self.axis     = axis
		self.name     = name
		self.function = function
		self.set_header()

	def set_header(self):
		self.setText('%d [%s]\n %s' % (self.number, self.axis, self.name))

	def set_number(self, number):
		self.number = number
		self.set_header()


class VHeaderItem(object):
	def __init__(self, number = -1, parent = None):
		super(VHeaderItem, self).__init__(parent)
		self.number   = number
		self.set_header()

	def set_header(self):
		self.setText('%d' % (self.number))

	def set_number(self, number):
		self.number = number
		self.set_header()
