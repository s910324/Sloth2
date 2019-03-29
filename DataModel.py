import os
import sys

from PyQt5.QtWidgets import *
from PyQt5.QtCore    import *
from PyQt5.QtGui     import *
from HeaderItem      import HHeaderItem, VHeaderItem

class DataModel(QAbstractTableModel):
	def __init__(self, parent = None, *args):
		QAbstractTableModel.__init__(self, parent, *args)

		self.data_cached             = []
		self.horizontal_header_items = {}
	
	def load_data(self, data):
		self.data_cached = data
 
	def rowCount(self, parent):
		return len(self.data_cached)
 
	def columnCount(self, parent):
		return len(self.data_cached[0]) if self.data_cached else 0
 
	def get_value(self, index):
		return self.data_cached[index.row()][index.column()]
 
	def data(self, index, role):
		if not index.isValid():
			return None
		value = self.get_value(index)
		if role == Qt.DisplayRole or role == Qt.EditRole:
			return value
		elif role == Qt.TextAlignmentRole:
				return Qt.AlignCenter
		return None
 
	def setData(self, index, value, role): 
		if index.isValid() and role == Qt.EditRole:
			self.data_cached[index.row()][index.column()] = value
			self.dataChanged.emit(index, index)
			return True
		else:
			return False
 
	def headerData(self, section, orientation, role):
		if orientation == Qt.Horizontal and role == Qt.DisplayRole:
			axis_text     = "-"
			name_text     = ""
			if section in self.horizontal_header_items:
				axis_text     = self.horizontal_header_items[section]["axis_text"]
				name_text     = self.horizontal_header_items[section]["name_text"]
			return '%d [%s]\n %s' % (section + 1, axis_text, name_text)

		if orientation == Qt.Vertical and role == Qt.DisplayRole:
			return ('%d' % (section + 1)).zfill(len(str(len(self.data_cached))))
		return None
 
	def flags(self, index):
		if not index.isValid():
			return Qt.ItemIsEnabled
		elif index.column() > 1:
			return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable
 
		return Qt.ItemIsEnabled | Qt.ItemIsSelectable
 

class DataItemModel(QStandardItemModel):
	def __init__(self, parent = None, *args):
		QStandardItemModel.__init__(self, parent, *args)
		self.parent = parent
		self.data_cached             = []
		self.horizontal_header_items = {}

	def load_data(self, data):
		self.data_cached = data
		for data_row in self.data_cached:
			self.appendRow([QStandardItem(str(data)+"nn") for data in data_row])
		self.parent.setItemDelegate(DataThemeDelegate(self.parent))
 
	def rowCount(self, parent):
		return len(self.data_cached)
 
	def columnCount(self, parent):
		return len(self.data_cached[0]) if self.data_cached else 0
 
	def get_value(self, index):
		return self.data_cached[index.row()][index.column()]
 
	def data(self, index, role):
		if not index.isValid():
			return None
		value = self.get_value(index)
		if role == Qt.DisplayRole or role == Qt.EditRole:
			return value
		elif role == Qt.TextAlignmentRole:
				return Qt.AlignCenter
		return None
 
	def setData(self, index, value, role): 
		if index.isValid() and role == Qt.EditRole:
			self.data_cached[index.row()][index.column()] = value
			self.dataChanged.emit(index, index)
			print("setted")
			return True
		else:
			return False

	def headerData(self, section, orientation, role):
		if orientation == Qt.Horizontal and role == Qt.DisplayRole:
			axis_text     = "-"
			name_text     = ""
			if section in self.horizontal_header_items:
				axis_text     = self.horizontal_header_items[section]["axis_text"]
				name_text     = self.horizontal_header_items[section]["name_text"]
			return '%d [%s]\n %s' % (section + 1, axis_text, name_text)

		if orientation == Qt.Vertical and role == Qt.DisplayRole:
			return ('%d' % (section + 1)).zfill(len(str(len(self.data_cached))))
		return None




class DataThemeDelegate(QStyledItemDelegate):
	def __init__(self, *args):
		super(DataThemeDelegate, self).__init__(*args)
		self.cell = Cell(self.parent())

	def paint(self, painter, option, index):
		item = index.model().itemFromIndex(index)
		self.cell.set_style("na")
		self.initStyleOption(option, index)
		style = option.widget.style() if option.widget else QApplication.style()
		style.unpolish(self.cell)
		style.polish(self.cell)
		style.drawControl(QStyle.CE_ItemViewItem, option, painter, self.cell)

class Cell(QWidget):
	def set_style(self, style_group  = 'Defaule'):
		self.setProperty('style_group', style_group)