import os
import sys

from PyQt5.QtWidgets import *
from PyQt5.QtCore    import *
from PyQt5.QtGui     import *
from HeaderItem      import HHeaderItem, VHeaderItem
import pandas 
import numpy
import random as r
#no longer required module, replaced by dataitemmodel
# class DataModel(QAbstractTableModel):
# 	""" for data storage and data handling"""
# 	def __init__(self, parent = None, *args):
# 		QAbstractTableModel.__init__(self, parent, *args)

# 		self.data_cached             = []
# 		self.horizontal_header_items = {}
	
# 	def load_data(self, data):
# 		self.data_cached = data
 
# 	def rowCount(self, parent):
# 		return len(self.data_cached)
 
# 	def columnCount(self, parent):
# 		return len(self.data_cached[0]) if self.data_cached else 0
 
# 	def get_value(self, index):
# 		return self.data_cached[index.row()][index.column()]
 
# 	def data(self, index, role):
# 		if not index.isValid():
# 			return None
# 		value = self.get_value(index)
# 		if role == Qt.DisplayRole or role == Qt.EditRole:
# 			return value
# 		elif role == Qt.TextAlignmentRole:
# 				return Qt.AlignCenter
# 		return None
 
# 	def setData(self, index, value, role): 
# 		if index.isValid() and role == Qt.EditRole:
# 			self.data_cached[index.row()][index.column()] = value
# 			self.dataChanged.emit(index, index)
# 			return True
# 		else:
# 			return False
 
# 	def headerData(self, section, orientation, role):
# 		if orientation == Qt.Horizontal and role == Qt.DisplayRole:
# 			axis_text     = "-"
# 			name_text     = ""
# 			if section in self.horizontal_header_items:
# 				axis_text     = self.horizontal_header_items[section]["axis_text"]
# 				name_text     = self.horizontal_header_items[section]["name_text"]
# 			return '%d [%s]\n %s' % (section + 1, axis_text, name_text)

# 		if orientation == Qt.Vertical and role == Qt.DisplayRole:
# 			return ('%d' % (section + 1)).zfill(len(str(len(self.data_cached))))
# 		return None
 
# 	def flags(self, index):
# 		if not index.isValid():
# 			return Qt.ItemIsEnabled
# 		elif index.column() > 1:
# 			return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable
 
# 		return Qt.ItemIsEnabled | Qt.ItemIsSelectable
 

class DataItemModel(QStandardItemModel):
	""" for data storage and data handling"""
	data_changed = pyqtSignal()
	def __init__(self, parent = None, *args):
		QStandardItemModel.__init__(self, parent, *args)
		self.parent = parent
		self.data_cached             = []
		self._data_frame             = pandas.DataFrame()
		self.horizontal_header_items = {}
		self.format_theme            = ['Cell[style_group=red]::item {background-color: #FF0033; font-style: italic;}', 'Cell[style_group=green]::item {background-color: green;}']
		# self.dataChanged.connect( lambda x, y: print( "DM: ", self.get_cell_data(x.row(), x.column()) ) )
		self.dataChanged.connect( lambda x, y: self.update_cell_data(x.row(), x.column()) )
		self.data_theme_deligate     = DataThemeDelegate(self.parent)

	def set_data(self, data, copy_data = False):
		data_frame       = data if isinstance(data, pandas.core.frame.DataFrame) else pandas.DataFrame(data)
		self._data_frame = data_frame.copy() if copy_data else data_frame

		self.clear()
		for row_index in range(len(self._data_frame)):
			self.appendRow([DataItem(data) for data in self._data_frame.iloc[row_index]])
		self.data_changed.emit()
		self.layoutChanged.emit()
		self.parent.setItemDelegate(self.data_theme_deligate)

	def get_cell_data(self, row_index, column_index):
		return self._data_frame.iloc[row_index, column_index]

	def set_cell_data(self, row_index, column_index, data):
		self._data_frame.iloc[row_index, column_index] = data

	def update_cell_data(self, row_index, column_index):
		data_from_data_item = self.item(row_index, column_index).data()
		self.set_cell_data(row_index, column_index, data_from_data_item)

	def clear_cell_at(self, row_index, column_index):
		self.item(row_index, column_index).setData(numpy.str(""))
		# self.data_theme_deligate.setModelData(QWidget(), self, self.index(row_index, column_index))


	def clear_row_at(self, row_index):
		_ =[ self.clear_cell_at(row_index, column_index) for column_index in range(self.columnCount())]

	def clear_column_at(self, column_index):
		_ =[ self.clear_cell_at(row_index, column_index) for row_index in range(self.rowCount())]

	def insert_column_at(self, column_index, dtype=str, default_value=""):
		new_column       = pandas.DataFrame([ default_value for row_index in range(self.rowCount())])
		left_half        = self._data_frame.iloc[:, :column_index]
		right_half       = self._data_frame.iloc[:, column_index:]
		self._data_frame = pandas.concat([left_half, new_column, right_half], axis = 1, ignore_index=True)
		self.set_data(self._data_frame)

	def insert_row_at(self, row_index, dtype=str, default_value=""):
		new_row          = pandas.DataFrame([[default_value for column_index in range(self.columnCount())]])
		upper_half       = self._data_frame.iloc[:row_index, ]
		lower_half       = self._data_frame.iloc[row_index:, ]
		self._data_frame = pandas.concat([upper_half, new_row, lower_half], axis = 0, ignore_index=True)
		self.set_data(self._data_frame)

	def remove_row_at(self, row_index_list):
		self._data_frame.drop(self._data_frame.index[row_index_list], axis=0, inplace= True)
		self.set_data(self._data_frame)

	def remove_column_at(self, column_index_list):
		print(column_index_list)
		self._data_frame.drop(self._data_frame.columns[column_index_list], axis=1, inplace= True)
		self.set_data(self._data_frame)

	def addDataFrameRows(self, count=1):
		"""

		Adds rows to the dataframe.

		:param count: (int)
			The number of rows to add to the dataframe.
		:return: (bool)
			True on success, False on failure.

		"""
		# don't allow any gaps in the data rows.
		# and always append at the end

		if not self.editable:
			return False

		position = self.rowCount()

		if count < 1:
			return False

		if len(self.dataFrame().columns) == 0:
			# log an error message or warning
			return False

		# Note: This function emits the rowsAboutToBeInserted() signal which
		# connected views (or proxies) must handle before the data is
		# inserted. Otherwise, the views may end up in an invalid state.
		self.beginInsertRows(QtCore.QModelIndex(), position, position + count - 1)

		defaultValues = []
		for dtype in self._dataFrame.dtypes:
			if dtype.type == numpy.dtype('<M8[ns]'):
				val = pandas.Timestamp('')
			elif dtype.type == numpy.dtype(object):
				val = ''
			else:
				val = dtype.type()
			defaultValues.append(val)

		for i in range(count):
			self._dataFrame.loc[position + i] = defaultValues
		self._dataFrame.reset_index()
		self.endInsertRows()
		return True

	def update_formatting(self):
		self.parent.setStyleSheet(''.join(self.format_theme))

	def rowCount(self, parent=None):
		return  len(self._data_frame)

	def columnCount(self, parent=None):
		return len(self._data_frame.columns)


	def headerData(self, section, orientation, role):
		if orientation == Qt.Horizontal and role == Qt.DisplayRole:
			axis_text     = "-"
			name_text     = ""
			if section in self.horizontal_header_items:
				axis_text     = self.horizontal_header_items[section]["axis_text"]
				name_text     = self.horizontal_header_items[section]["name_text"]
			return '%d [%s]\n %s' % (section + 1, axis_text, name_text)

		if orientation == Qt.Vertical and role == Qt.DisplayRole:
			return ('%d' % (section + 1)).zfill(len(str(len(self._data_frame))))
		return None

	def get_cell_style(self, index):
		return type(self.parent.itemDelegate(index).cell)#.styleSheet()

	def set_cell_style(self, index ):#, style):
		# print(self.parent.model().item(0, 0).text())
		# self.parent.model().item(0, 0).setText("123123123")
		self.item(0, 1).style._background_color = "#0033FF"

		# self.parent.model().item(0, 1).setm()


class Cell(QWidget):
	editingFinished = pyqtSignal()
	def __init__(self, parent):
		super(Cell, self).__init__(parent)
		f = self.font()
		f.setPointSize(50)
		# self.setStyleSheet("Cell::item {background-color: #FF0033; font-style: italic; font-size: 225px;}")
	def set_style(self, style_group  = 'default'):
		self.setProperty('style_group', style_group)




class DataItem(QStandardItem):
	def __init__(self, data = None):
		QStandardItem.__init__(self)
		'''data, setdata function is to set indicator value not real data'''
		''' this is a display object, responsble to cell text formatting, styling params are stored with Style Object and rendered by DataThemeDelegate'''
		self.style           = StyleObject()
		self.role            = Qt.EditRole and  Qt.DisplayRole
		self.indicate_format = ""
		self.indicate_value  = ""
		self.setData(data, self.role)
		self.connect_style()
		self._set_text_color("#AA33FF") # takes no effect



	def setData(self, data, role = None):

		if issubclass(type(data), numpy.generic):
			QStandardItem.setData(self, data, role if role else self.role)
		else:
			try:
				self.data_value      = numpy.double(data)
				self.indicate_format = "%.2f"
				QStandardItem.setData(self, self.data_value, role if role else self.role)
				self.emitDataChanged()
			except ValueError:
				self.data_value      = numpy.str(data)
				self.indicate_format = "%s"
				QStandardItem.setData(self, self.data_value, role if role else self.role)
				self.emitDataChanged()
			except TypeError:
				pass 
				'''pass data type error due to style updating '''



	def data(self, role = None):
		if role == Qt.DisplayRole:
			return self.indicate_format % QStandardItem.data(self, role)
		else:
			return QStandardItem.data(self, role if role else self.role) 


	def data_type(self):
		return type(self.data())

	def connect_style(self):
		self.style.text_size_changed.connect( lambda x : self._set_text_size(x))
		self.style.text_color_changed.connect(lambda x : self._set_text_color(x))

	def _set_text_size(self, size): #function not working
		font = self.font()
		font.setPointSize(size)
		QStandardItem.setFont(self,font)


	def _set_text_color(self, font_color):#function not working
		self.setForeground(QBrush(QColor("font_color")) )

	def _to_double(self):
		try:
			value       = numpy.double(self.data())
			self.format = "%.2f"
			self.setText(self.format % value)
			return True
		except ValueError:
			return False

	def _to_float(self):
		try:
			value       = numpy.float(self.data())
			self.format = "%.2f"
			self.setText(self.format % value)
			return True
		except ValueError:
			return False

	def _to_int(self):
		try:
			value       = numpy.int(self.data())
			self.format = "%d"
			self.setText(self.format % value)
			return True
		except ValueError:
			return False

	def _to_str(self):
		try:
			value       = numpy.str(self.data())
			self.format = "%s"
			self.setText(self.format % value)
			return True
		except ValueError:
			return False


	def text(self):
		return (self.indicate_format % self.data)



class DataThemeDelegate(QStyledItemDelegate):
	'''Handle real data theme, active while cell is at edit mode'''
	''' this is a display object, responsble to cell text formatting, styling params are stored with Style Object and rendered by DataThemeDelegate'''
	def __init__(self, *args):
		super(DataThemeDelegate, self).__init__(*args)
		self.cell = Cell(self.parent())
		self.text = ""

	def createEditor(self, parent, option, index):
		# change text style while at editing mode
		self.editor = QLineEdit(parent)
		self.editor.setStyleSheet("QLineEdit{ color: red; background-color: rgba(255, 255, 255, 100); font-size: 55px;}") #should able to be controlled by setBG function
		print ("---", index.model().itemFromIndex(index), index.model().itemFromIndex(index).style.background_color, self.editor)
		

		return self.editor

	def setEditorData(self, editor, index):
		value = index.model().data(index, Qt.EditRole)
		editor.setText(str(value))

		self.text = value


	def setModelData(self, editor, model, index):
		# spinBox.interpretText()
		value = editor.text()
		model.setData(index, value, Qt.EditRole)

	def updateEditorGeometry(self, editor, option, index):
		editor.setGeometry(option.rect)

	def paint(self, painter, option, index):
		data_modle_item = index.model().itemFromIndex(index)
		cell_style      = data_modle_item.style
		self.draw_cell_background(painter, option, cell_style.background_color, cell_style.background_brush_style, cell_style.background_brush_color)
		self.draw_cell_type_hint( painter, option, data_modle_item)
		# self.draw_text(painter, option, self.text)

		i = r.random()
		# self.cell.set_style('default' if i > 0.5 else 'red' )

		self.initStyleOption(option, index)
		style = option.widget.style() if option.widget else QApplication.style()
		style.unpolish(self.cell)
		style.polish(self.cell)
		style.drawControl(QStyle.CE_ItemViewItem , option, painter, self.cell)

		op = QStyleOptionViewItem(option)

		if (index.row() == 2):
			op.font.setBold(True)
			op.palette.setColor(QPalette.Normal, QPalette.Background, Qt.black)
			op.palette.setColor(QPalette.Normal, QPalette.Foreground, Qt.white)
		QStyledItemDelegate.paint(self, painter, op, index)


	def draw_cell_background(self, painter, option, background_color, background_brush_style, background_brush_color):
		background = QPolygon(4)
		x, y, w, h = option.rect.x(), option.rect.y(), option.rect.width(), option.rect.height()
		background.setPoint(0, QPoint(x+w, y))
		background.setPoint(1, QPoint(x,   y))
		background.setPoint(2, QPoint(x,   y+h))
		background.setPoint(3, QPoint(x+w, y+h))

		painter.save()
		painter.setRenderHint(painter.Antialiasing)
		background_brush        = QBrush(QColor(background_color), Qt.SolidPattern)
		background_styled_brush = QBrush(QColor(background_brush_color), background_brush_style)
		
		painter.setBrush(background_brush)
		painter.setPen(Qt.NoPen)
		painter.drawPolygon(background)

		if not(background_brush_style == Qt.SolidPattern):	
			painter.setBrush(background_styled_brush)
			painter.setPen(Qt.NoPen)
			painter.drawPolygon(background)		
		painter.restore()

	def draw_cell_type_hint(self, painter, option, data_type):
		if data_type.data_type() == str:
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

	def draw_text(self, painter, option, text):

			painter.save()
			painter.setRenderHint(painter.Antialiasing)
			painter.setPen(QPen(QColor("#00cc66")))
			painter.drawText(10,10,text)
			painter.restore()
	# def createEditor(self, parent, option, index):
	# 	""" Creates and returns the custom StarEditor object we'll use to edit 
	# 		the StarRating.
	# 	"""
	# 	if index.column() == 0:
	# 		editor = Cell(parent)
	# 		editor.editingFinished.connect(self.commitAndCloseEditor)
	# 		return editor
	# 	else:
	# 		return QStyledItemDelegate.createEditor(self, parent, option, index)

	# def setEditorData(self, editor, index):
	# 	""" Sets the data to be displayed and edited by our custom editor. """
	# 	QStyledItemDelegate.setEditorData(self, editor, index)

	# def setModelData(self, editor, model, index):
	# 	""" Get the data from our custom editor and stuffs it into the model.
	# 	"""
	# 	QStyledItemDelegate.setModelData(self, editor, model, index)

	# def commitAndCloseEditor(self):
	# 	""" Erm... commits the data and closes the editor. :) """
	# 	editor = self.sender()

	# 	# The commitData signal must be emitted when we've finished editing
	# 	# and need to write our changed back to the model.
	# 	self.commitData.emit(editor)
	# 	self.closeEditor.emit(editor)



class StyleObject(QObject):
	background_color_changed       = pyqtSignal(str)
	background_brush_style_changed = pyqtSignal(QBrush)
	background_brush_color_changed = pyqtSignal(str)
	text_size_changed              = pyqtSignal(int)
	text_color_changed             = pyqtSignal(str)
	
	def __init__(self):
		super(StyleObject, self).__init__()
		self._background_color       =  "#FFFFFF"       #achieved by DataThemeDelegate draw background
		self._background_brush_style =  Qt.Dense3Pattern
		self._background_brush_color =  "#33ff33"
		self._type_hint_color        =  "#33ff33"
		self._text_size              =  8
		self._text_color             =  "#000000"
		self._text_font              =  "Inconsolata"
		self._text_bold              =  False
		self._text_italic            =  False
		self._text_underline         =  False
		self._text_deleteline        =  False
		self._text_h_align           =  Qt.AlignRight
		self._text_v_align           =  Qt.AlignHCenter
		self._border_style           =  Qt.SolidLine
		self._border_width           =  0
		self._bolder_color           =  "#000000"



	@property
	def background_color(self):
		return self._background_color	

	@background_color.setter
	def background_color(self, color):
		self._background_color = color
		self.background_color_changed.emit(color)

	@property
	def background_brush_style(self):
		return self._background_brush_style	

	@background_brush_style.setter
	def background_brush_style(self, style):
		self._background_brush_style = style
		self.background_brush_style_changed.emit(style)

	@property
	def background_brush_color(self):
		return self._background_brush_color	

	@background_brush_color.setter
	def background_brush_color(self, color):
		self._background_brush_color = color
		self.background_brush_color_changed.emit(color)

	@property
	def type_hint_color(self):
		return self._type_hint_color	

	@type_hint_color.setter
	def type_hint_color(self, color):
		self._type_hint_color = color
		self.type_hint_color_changed.emit(color)

	@property
	def text_size(self):
		return self._text_size

	@text_size.setter
	def text_size(self, size):
		self._text_size = size
		self.text_size_changed.emit(size)

	@property
	def text_color(self):
		return self._text_color
		
	@text_color.setter
	def text_color(self, color):
		self._text_color = color
		self.text_color_changed.emit(color)

	@property
	def text_h_align(self):
		return self._text_h_align

	@text_h_align.setter
	def text_h_align(self, align):
		if align in [Qt.AlignLeft, Qt.AlignRight, Qt.AlignHCenter, Qt.AlignJustify]:
			self._text_h_align = align
		else:
			raise TypeError("StyleObject invalid test align type %s, %s" & (type(align), align))