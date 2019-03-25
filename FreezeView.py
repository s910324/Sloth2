import os
import sys
import math
from PyQt5.QtWidgets import *
from PyQt5.QtCore    import *


class FreezeView(QTableView):
	horizontal_header_resized = pyqtSignal(int, int, int)
	vertical_header_resized   = pyqtSignal(int, int, int)

	top, left, corner         = 0, 1, 2
	def __init__(self, orentation, start_column_index, end_column_index, start_row_index, end_row_index, parent):
		QTableView.__init__(self, parent)
		assert isinstance(parent, QTableView)
		assert orentation in [FreezeView.left, FreezeView.top, FreezeView.corner]
		self.resizable            = False
		self.start_column_index   = start_column_index
		self.start_row_index      = start_row_index
		self.end_column_index     = end_column_index
		self.end_row_index        = end_row_index
		self.parent               = parent
		self.orentation           = orentation
		self.freeze_hiddin_row    = []
		self.freeze_hiddin_column = []
		self.parent_scroll_mode   = {"vertical":None, "horizontal":None}
	
		if orentation == FreezeView.left:
			self.horizontalHeader().setHidden(parent.horizontalHeader().isHidden())
			self.verticalHeader().hide()

		if orentation == FreezeView.top:
			self.verticalHeader().setHidden(parent.verticalHeader().isHidden())
			self.horizontalHeader().hide()
			
		if orentation == FreezeView.corner:
			self.horizontalHeader().hide()
			self.verticalHeader().hide()

		self.setStyleSheet('''border: none;''')
		self.setFocusPolicy(Qt.NoFocus)
		self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)	
		self.show()
	

	def showEvent(self, event):
		QTableView.showEvent(self, event)
		#must initiallize geroetry before resizable is set true, otherwise will receive "set 0 width error"
		#must be called after show event, or the visibility of header will always return false
		self.initiallize_geometry()

	def connect_to_views(self):
		print("c: ", self.verticalHeader().isVisible(), self.horizontalHeader().isVisible())
		self.resizable = True
		parent         = self.parent
		print("b: ", self.verticalHeader().isVisible(), self.horizontalHeader().isVisible())
		self.horizontalHeader().sectionResized.connect(lambda column, old_size, new_size : self.increament_width(  new_size - old_size))
		self.verticalHeader().sectionResized.connect  (lambda    row, old_size, new_size : self.increament_height( new_size - old_size))
		print("a: ", self.verticalHeader().isVisible(), self.horizontalHeader().isVisible())
		if self.orentation == FreezeView.left:
			if parent.corner_frozen_view : self.horizontalHeader().sectionResized.connect(  lambda column, old_size, new_size : parent.corner_frozen_view.setColumnWidth(column, new_size))
			if parent.top_frozen_view    : self.horizontalHeader().sectionResized.connect(  lambda column, old_size, new_size : parent.top_frozen_view.setColumnWidth(column, new_size))
			if parent                    : self.horizontalHeader().sectionResized.connect(  lambda column, old_size, new_size : parent.setColumnWidth(column, new_size))
			if parent                    : parent.verticalHeader().sectionResized.connect(self.initiallize_geometry)
			if parent                    : parent.horizontalHeader().sectionResized.connect( self.initiallize_geometry)
			if parent                    : parent.verticalScrollBar().valueChanged.connect( self.verticalScrollBar().setValue)
			self.verticalScrollBar().valueChanged.connect(parent.verticalScrollBar().setValue)

		if self.orentation == FreezeView.top:
			if parent                    : parent.horizontalScrollBar().valueChanged.connect(self.horizontalScrollBar().setValue)			
			if parent.corner_frozen_view : self.verticalHeader().sectionResized.connect(    lambda    row, old_size, new_size : parent.corner_frozen_view.setRowHeight(row, new_size))
			if parent.left_frozen_view   : self.verticalHeader().sectionResized.connect(    lambda    row, old_size, new_size : parent.left_frozen_view.setRowHeight(row, new_size))
			if parent                    : self.verticalHeader().sectionResized.connect(    lambda    row, old_size, new_size : parent.setRowHeight(row, new_size))
			if parent                    : parent.horizontalHeader().sectionResized.connect( self.initiallize_geometry)
			if parent                    : parent.verticalHeader().sectionResized.connect(self.initiallize_geometry)
			if parent                    : parent.horizontalScrollBar().valueChanged.connect(self.horizontalScrollBar().setValue)	
			self.horizontalScrollBar().valueChanged.connect(parent.horizontalScrollBar().setValue)

		parent.data_updated.connect(self.initiallize_geometry)
		parent.column_removed.connect(self.remove_column_at)
		parent.row_removed.connect(self.remove_row_at)
		parent.column_inserted.connect(self.insert_column_at)
		parent.row_inserted.connect(self.insert_row_at)
		self.setSelectionModel(parent.selectionModel())
		

	def disconnect_to_views(self):
		self.resizable = False
		parent         = self.parent
		if self.orentation == FreezeView.left:
			self.verticalScrollBar().valueChanged.disconnect()
			self.horizontalHeader().sectionResized.disconnect()
			parent.verticalScrollBar().valueChanged.disconnect( self.verticalScrollBar().setValue)
			parent.verticalHeader().sectionResized.disconnect(self.initiallize_geometry)
			parent.horizontalHeader().sectionResized.disconnect(self.initiallize_geometry)
		if self.orentation == FreezeView.top:
			self.horizontalScrollBar().valueChanged.disconnect()
			self.verticalHeader().sectionResized.disconnect()
			parent.horizontalScrollBar().valueChanged.disconnect(self.horizontalScrollBar().setValue)	
			parent.verticalHeader().sectionResized.disconnect(self.initiallize_geometry)
			parent.horizontalHeader().sectionResized.disconnect(self.initiallize_geometry)

		parent.data_updated.disconnect(self.initiallize_geometry)
		parent.column_removed.disconnect(self.remove_column_at)
		parent.row_removed.disconnect(self.remove_row_at)
		parent.column_inserted.disconnect(self.insert_column_at)
		parent.row_inserted.disconnect(self.insert_row_at)			
		self.show_freezed_area()
		self.deleteLater()

	def update_data_model(self, data_model):
		self.setModel(data_model)

	def columnResized(self, column, oldWidth, newWidth):
		QTableView.columnWidth(column, oldWidth, newWidth)

	def resizeEvent(self, event):
		QTableView.resizeEvent(self, event)
		# self.updateFrozenTableGeometry()/////////////////////////////////////required

	def moveCursor(self, cursorAction, modifiers):
		parent = self.parent 
		current = QTableView.moveCursor(parent, cursorAction, modifiers)
		if cursorAction == parent.MoveLeft and current.column() > 1 and parent.visualRect(current).topLeft().x() < (self.columnWidth(0) + self.columnWidth(1)):
			newValue = parent.horizontalScrollBar().value() + parent.visualRect(current).topLeft().x() - (self.columnWidth(0) + self.columnWidth(1))
			parent.horizontalScrollBar().setValue(newValue) # todo not best pratice
		return current
		
	def initiallize_geometry(self):
		parent               = self.parent
		x_header_offset      = parent.verticalHeader().width()    *  (self.verticalHeader().isHidden()   - parent.verticalHeader().isHidden())
		y_header_offset      = parent.horizontalHeader().height() *  (self.horizontalHeader().isHidden() - parent.horizontalHeader().isHidden())
		x                    = parent.frameWidth() + x_header_offset
		y                    = parent.frameWidth() + y_header_offset
		w                    = parent.verticalHeader().width()    *  self.verticalHeader().isVisible()
		h                    = parent.horizontalHeader().height() *  self.horizontalHeader().isVisible()
		self.setModel(parent.model())
		self.set_scroll_mode_constrain()
		print (self.orentation, w, h, self.verticalHeader().isVisible(), self.horizontalHeader().isVisible())
		if self.orentation == FreezeView.top:
			w =  w + parent.viewport().width()   
			h =  h + sum([parent.rowHeight(row_index)      for row_index    in range(   self.start_row_index,      self.end_row_index)])                             
		if self.orentation == FreezeView.left:
			w =  w + sum([parent.columnWidth(column_index) for column_index in range(self.start_column_index,   self.end_column_index)]) 
			h =  h + parent.viewport().height()
		if self.orentation == FreezeView.corner:
			w =  w + sum([parent.columnWidth(column_index) for column_index in range(self.start_column_index,   self.end_column_index)]) 
			h =  h + sum([parent.rowHeight(row_index)      for row_index    in range(   self.start_row_index,      self.end_row_index)])
		self.hide_freezed_area()
		self.set_size( x, y, w, h)
		self.relesae_scroll_mode_constrain()
		print("d: ", self.verticalHeader().isVisible(), self.horizontalHeader().isVisible())
		
	def set_scroll_mode_constrain(self):
		parent = self.parent
		self.parent_scroll_mode = {"vertical":parent.verticalScrollMode(), "horizontal":parent.horizontalScrollMode()}
		parent.setVerticalScrollMode(QAbstractItemView.ScrollPerItem)
		parent.setHorizontalScrollMode(QAbstractItemView.ScrollPerItem)
		self.setVerticalScrollMode(QAbstractItemView.ScrollPerItem)
		self.setHorizontalScrollMode(QAbstractItemView.ScrollPerItem)
	
	def relesae_scroll_mode_constrain(self):
		parent = self.parent
		parent.setVerticalScrollMode(self.parent_scroll_mode["vertical"])
		parent.setHorizontalScrollMode(self.parent_scroll_mode["horizontal"])
		self.setVerticalScrollMode(self.parent_scroll_mode["vertical"])
		self.setHorizontalScrollMode(self.parent_scroll_mode["horizontal"])

	def hide_freezed_area(self):
		parent = self.parent
		for column_index in range(parent.data_model.columnCount(parent)):
			if column_index not in range(self.start_column_index, self.end_column_index):
				self.setColumnHidden(column_index, True)
				if self.orentation == FreezeView.top:
					if not parent.isColumnHidden(column_index):
						parent.setColumnHidden(column_index, True)
						self.freeze_hiddin_column.append(column_index)
			else:
				self.setColumnWidth(column_index, parent.columnWidth(column_index))

		for row_index in range(parent.data_model.rowCount(parent)):
			if row_index not in range(self.start_row_index, self.end_row_index):
				self.setRowHidden(row_index, True)	
				if self.orentation == FreezeView.left:
					if not parent.isRowHidden(row_index):
						parent.setRowHidden(row_index, True)
						self.freeze_hiddin_row.append(row_index)
			else:
				self.setRowHeight(row_index, parent.rowHeight(row_index))

	def show_freezed_area(self):
		parent = self.parent
		for row_index in self.freeze_hiddin_row:
			parent.setRowHidden(row_index, False)
		for column_index in self.freeze_hiddin_column:
			parent.setColumnHidden(column_index, False)		

	def set_size(self, x, y, w, h):
		self.move(x, y)
		self.setFixedWidth(w)
		self.setFixedHeight(h)
		self.updateGeometry()

	def increament_width(self, delta_width):
		if self.resizable:
			print(delta_width)
			self.setFixedWidth(self.width() + delta_width)
			self.updateGeometry()
		
	def increament_height(self, delta_height):
		if self.resizable:
			self.setFixedHeight(self.height() + delta_height)
			self.updateGeometry()
		
	def remove_row_at(self, row_index):
		if row_index in range(self.start_row_index, self.end_row_index):
			self.end_row_index -= 1
			self.initiallize_geometry()

	def remove_column_at(self, column_index):
		if column_index in range(self.start_column_index, self.end_column_index):
			self.end_column_index -= 1
			self.initiallize_geometry()

	def insert_row_at(self, row_index):
		if row_index in range(self.start_row_index, self.end_row_index):
			self.end_row_index += 1
			self.setRowHidden(self.end_row_index, False)
			self.initiallize_geometry()

	def insert_column_at(self, column_index, column_counts = 1):
		if column_index in range(self.start_column_index, self.end_column_index):
			self.end_column_index += 1
			self.setColumnHidden(self.end_column_index, False)
			self.initiallize_geometry()

			