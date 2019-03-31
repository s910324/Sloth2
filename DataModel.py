import os
import sys

from PyQt5.QtWidgets import *
from PyQt5.QtCore    import *
from PyQt5.QtGui     import *
from HeaderItem      import HHeaderItem, VHeaderItem
import random as r

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
		self.format_theme            = ['Cell[style_group=red]::item {background-color: red;font-style: italic;}', 'Cell[style_group=green]::item {background-color: green;}']

	def load_data(self, data):
		self.data_cached = data
		for index, data_row in enumerate(self.data_cached):
			self.appendRow([DataItem(data) for data in data_row])
		self.parent.setItemDelegate(DataThemeDelegate(self.parent))
		self.update_formatting()

	def update_formatting(self):
		self.parent.setStyleSheet(''.join(self.format_theme))

	def rowCount(self, parent):
		return len(self.data_cached)
 
	def columnCount(self, parent):
		return len(self.data_cached[0]) if self.data_cached else 0
 
	# def get_value(self, index):
	# 	return self.data_cached[index.row()][index.column()]
 
	# def data(self, index, role):
	# 	if not index.isValid():
	# 		return None
	# 	value = self.get_value(index)
	# 	if role == Qt.DisplayRole or role == Qt.EditRole:
	# 		return value
	# 	elif role == Qt.TextAlignmentRole:
	# 			return Qt.AlignCenter
	# 	return None
 
	# def setData(self, index, value, role): 
	# 	print ("asdasd")
	# 	if index.isValid() and role == Qt.EditRole:
	# 		self.data_cached[index.row()][index.column()] = value
	# 		self.dataChanged.emit(index, index)
	# 		return True
	# 	else:
	# 		return False

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

	def get_cell_style(self, index):
		return type(self.parent.itemDelegate(index).cell)#.styleSheet()

	def set_cell_style(self, index , style):
		print(self.parent.model().item(0, 0).text())
		self.parent.model().item(0, 0).setText("123123123")
		self.parent.model().item(0, 1).setBackground(QColor("#FF0000"))


class DataThemeDelegate(QStyledItemDelegate):
	def __init__(self, *args):
		super(DataThemeDelegate, self).__init__(*args)
		self.cell = Cell(self.parent())

	def paint(self, painter, option, index):
		item = index.model().itemFromIndex(index)
		# i = r.random()
		# self.cell.set_style('defaule' if i > 0.5 else 'red' )
		self.initStyleOption(option, index)
		style = option.widget.style() if option.widget else QApplication.style()
		style.unpolish(self.cell)
		style.polish(self.cell)
		style.drawControl(QStyle.CE_ItemViewItem , option, painter, self.cell)


		super(DataThemeDelegate, self).paint(painter, option, index)

		polygonTriangle = QPolygon(3)
		polygonTriangle.setPoint(0, QPoint(option.rect.x()+5, option.rect.y()))
		polygonTriangle.setPoint(1, QPoint(option.rect.x(), option.rect.y()))
		polygonTriangle.setPoint(2, QPoint(option.rect.x(), option.rect.y()+5))

		painter.save()
		painter.setRenderHint(painter.Antialiasing)
		painter.setBrush(QBrush(QColor(Qt.darkGreen))) 
		painter.setPen(QPen(QColor(Qt.darkGreen)))
		painter.drawPolygon(polygonTriangle)
		painter.restore()

class Cell(QWidget):
	def __init__(self, *args):
		super(Cell, self).__init__(*args)


	def set_style(self, style_group  = 'default'):
		self.setProperty('style_group', style_group)

class DataItem(QStandardItem):
	def __init__(self, data = None):
		QStandardItem.__init__(self)
		self.data   = None
		self.format = ""
		self.set_data(data)
		print (self.data, self.format)

	def to_float(self):
		try:
			self.data   = float(self.data)
			self.format = "%.2f"
			return True
		except ValueError:
			return False

	def to_int(self):
		try:
			self.data = int(self.data)
			self.format = "%d"
			return True
		except ValueError:
			return False

	def to_str(self):
		try:
			self.data = str(self.data)
			self.format = "%s"
			return True
		except ValueError:
			return False

	def data_type(self):
		return type(self.data)

	def set_data(self, data):

		self.data = data
		if self.to_float():
			self.setText(self.text())
			return True
		if self.to_int():
			self.setText(self.text())
			return True
		if self.to_str():
			self.setText(self.text())
			return True			
		return False


	def text(self):
		return (self.format % self.data)


