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
		# print(self.parent.model().item(0, 0).text())
		# self.parent.model().item(0, 0).setText("123123123")
		self.parent.model().item(0, 1).setBackground(QColor("#FF0000"))
		# self.parent.model().item(0, 1).setm()


class DataThemeDelegate(QStyledItemDelegate):
	def __init__(self, *args):
		super(DataThemeDelegate, self).__init__(*args)
		self.cell = Cell(self.parent())


	def paint(self, painter, option, index):
		item = index.model().itemFromIndex(index)

		self.draw_cell_background(painter, option, item.style.background_color())
		self.draw_cell_type_hint( painter, option, item)
		

		# i = r.random()
		# self.cell.set_style('defaule' if i > 0.5 else 'red' )



		self.initStyleOption(option, index)
		style = option.widget.style() if option.widget else QApplication.style()
		style.unpolish(self.cell)
		style.polish(self.cell)
		style.drawControl(QStyle.CE_ItemViewItem , option, painter, self.cell)



	def draw_cell_background(self, painter, option, background_color):
		background = QPolygon(4)
		x, y, w, h = option.rect.x(), option.rect.y(), option.rect.width(), option.rect.height()
		background.setPoint(0, QPoint(x+w, y))
		background.setPoint(1, QPoint(x,   y))
		background.setPoint(2, QPoint(x,   y+h))
		background.setPoint(3, QPoint(x+w, y+h))
		
		painter.save()
		painter.setRenderHint(painter.Antialiasing)
		painter.setBrush(QBrush(QColor(background_color))) 
		painter.setPen(Qt.NoPen)
		painter.drawPolygon(background)
		painter.restore()

	def draw_cell_type_hint(self, painter, option, data_type):
		if data_type.data_type()== str:
			triangle = QPolygon(3)
			triangle.setPoint(0, QPoint(option.rect.x()+4, option.rect.y()))
			triangle.setPoint(1, QPoint(option.rect.x(),   option.rect.y()))
			triangle.setPoint(2, QPoint(option.rect.x(),   option.rect.y()+4))
			painter.save()
			painter.setRenderHint(painter.Antialiasing)
			painter.setBrush(QBrush(QColor("#00cc66"))) 
			painter.setPen(Qt.NoPen)
			painter.drawPolygon(triangle)
			painter.restore()

class Cell(QWidget):
	def __init__(self, parent):
		super(Cell, self).__init__(parent)

	def set_style(self, style_group  = 'default'):
		print( self)
		self.setProperty('style_group', style_group)




class DataItem(QStandardItem):
	def __init__(self, data = None):
		QStandardItem.__init__(self)
		self.style = StyleObject()
		self.data   = None
		self.format = ""
		self.set_data(data)
		# print (self.font())
		self.connect_style()

	def connect_style(self):
		self.style.text_size_changed.connect( lambda x : self._set_text_size(x))
		self.style.text_color_changed.connect(lambda x : self._set_text_color(x))

	def _set_text_size(self, size):
		font = self.font()
		font.setPointSize(size)
		self.setFont(font)

	def _set_text_color(self, font_color):
		self.setForeground(QColor(font_color))


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

class StyleObject(QObject):
	text_size_changed  = pyqtSignal(int)
	text_color_changed = pyqtSignal(str)
	
	def __init__(self):
		super(StyleObject, self).__init__()
		self._background_color =  "#FFFFFF"
		self._text_size        =  8
		self._text_color       =  "#000000"
		self._text_h_align     =  Qt.AlignRight
		self._text_v_align     =  Qt.AlignHCenter
		self._text_font        =  "Inconsolata"
		self._text_bold        =  False
		self._text_italic      =  False

	def set_background_color(self, color):
		self._background_color = color

	def set_text_size(self, size):
		self._text_size        = size
		self.text_size_changed.emit(size)

	def set_text_color(self, color):
		self._text_color       = color
		self.text_color_changed.emit(color)

	def background_color(self):
		return self._background_color

	def text_size(self):
		return self._text_size

	def text_color(self):
		return self._text_color