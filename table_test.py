#!/usr/bin/env python
import os
import sys
import types
import warnings
import pickle
from PyQt5.QtWidgets import *
from PyQt5.QtCore    import *
from PyQt5.QtGui     import *
from HeaderItem      import HHeaderItem, VHeaderItem
from DataModel       import DataModel, DataItemModel
from FreezeView      import FreezeView
from CursorTracker   import CursorTracker
from functools       import reduce
from itertools       import chain

class TableWidget(QTableView):
	trigger = pyqtSignal()
	column_removed            = pyqtSignal(int)
	row_removed               = pyqtSignal(int)
	column_inserted           = pyqtSignal(int)
	row_inserted              = pyqtSignal(int)
	data_updated              = pyqtSignal(DataModel)
	vscroll_mode_changed      = pyqtSignal(QAbstractItemView.ScrollMode)
	hscroll_mode_changed      = pyqtSignal(QAbstractItemView.ScrollMode)
	def __init__(self, data = [], parent=None,  *args):
		QTableView.__init__(self, parent, *args)
		self.enable_frozen_view  = False
		self.data_model          = DataItemModel(self)
		self.left_frozen_view    = None
		self.corner_frozen_view  = None
		self.top_frozen_view     = None
		self.cursor_tracker      = None
		self.update_data_model()
		self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
		self.setVerticalScrollMode(  QAbstractItemView.ScrollPerPixel)
		# self.data_model.dataChanged.connect(self.updateDelegates)

		
	def enable_forzen_view(self, row_index, column_index):
		if self.enable_frozen_view == True : return
		start_row_index           = self.rowAt(0)
		start_column_index        = self.columnAt(0)
  
		self.cursor_tracker       = CursorTracker(self)
		self.top_frozen_view      = FreezeView(FreezeView.top,    start_column_index, self.column_counts(), start_row_index,         row_index, self) if row_index                        > 0 else None
		self.left_frozen_view     = FreezeView(FreezeView.left,   start_column_index,         column_index, start_row_index, self.row_counts(), self) if column_index                     > 0 else None
		self.corner_frozen_view   = FreezeView(FreezeView.corner, start_column_index,         column_index, start_row_index,         row_index, self) if (column_index > 0 and row_index) > 0 else None
		
		if any([self.top_frozen_view, self.left_frozen_view, self.corner_frozen_view]):
			self.enable_frozen_view   = True
			if all([self.top_frozen_view, self.left_frozen_view, self.corner_frozen_view]):
				self.viewport().stackUnder(self.top_frozen_view)
				self.left_frozen_view.viewport().stackUnder(self.top_frozen_view)
				self.corner_frozen_view.viewport().stackUnder(self.left_frozen_view)

			elif not any([self.left_frozen_view, self.corner_frozen_view]):
				self.viewport().stackUnder(self.top_frozen_view)

			elif not any([self.top_frozen_view, self.corner_frozen_view]):
				self.viewport().stackUnder(self.left_frozen_view)


	def disable_frozen_view(self):
		if self.top_frozen_view    : self.top_frozen_view.disconnect_to_views()
		if self.left_frozen_view   : self.left_frozen_view.disconnect_to_views()
		if self.corner_frozen_view : self.corner_frozen_view.disconnect_to_views()
		self.cursor_tracker     = None
		self.top_frozen_view    = None
		self.left_frozen_view   = None
		self.corner_frozen_view = None
		self.enable_frozen_view = False


	def connect_frozen_view(self):
		if self.enable_frozen_view:
			if self.top_frozen_view    : self.top_frozen_view.connect_to_views()
			if self.left_frozen_view   : self.left_frozen_view.connect_to_views()
			if self.corner_frozen_view : self.corner_frozen_view.connect_to_views()

	def row_counts(self):
		return self.data_model.rowCount(self)

	def column_counts(self):
		return self.data_model.columnCount(self)

	def set_data(self, data):
		if data:
			# self.data_model.data_cached = data
			self.data_model.set_data(data)
			self.update_data_model()
	
	def froze_view_at_selection(self):
		selection = self.selectionModel().selection()
		if len(selection)==1:
			selected_range = selection[0]
			self.enable_forzen_view(selected_range.top(), selected_range.left())
			self.connect_frozen_view()		




	def selection_check(self):
		print (self.data_model._data_frame)

		# c = self.cell_item_in_selected_ranges(self.selectionModel().selection())
		# for cell in reduce(lambda i, j : i + j, c):

		# 	cell.style.set_background_color("#323232")
		# 	cell.style.set_text_size(6)
		# 	cell.style.set_text_color("#fdfdfd")


			# print(cell.m)
		# self.data_model.set_cell_style(0, 0)
		# self.data_model.update_formatting()
		# print(self.viewport().height())
		# print(self.rowAt(0))
		# self.setIndexWidget(self.model().index(0, 0), QTextEdit())
		# print(self.indexWidget(self.model().index(0, 0)))
		# self.setItemDelegateForRow() QAbstractItemDelegate


		# for i in range(4,8):
		#   for j in range(3, 6):
		#       m = self.model().index(i, j)
		#       self.selectionModel().select(m, QItemSelectionModel.Select)
		
		
		# print (self.selectionModel().selection())

	def copy_selected_ranges(self):
		selected_data = self.data_in_selected_ranges(self.selectionModel().selection())
		clip_board_text = ('\n'.join(['\t'.join(map(str, row_data)) for row_data in selected_data]))
		QApplication.clipboard().setText(clip_board_text)
		return clip_board_text

	def cell_item_in_selected_ranges(self, selection):
		assert isinstance(selection, QItemSelection)
		selected_cell   = []		
		if selection:
			return [reduce(lambda i, j : i + j, self.cell_item_in_selected_range(selected_range)) for selected_range in selection]

	def data_in_selected_ranges(self, selection):
		assert isinstance(selection, QItemSelection)
		selected_data   = []
		if selection:
			same_top        = len(set([selected_range.top()    for selected_range in selection])) == 1
			same_bottom     = len(set([selected_range.bottom() for selected_range in selection])) == 1
			same_left       = len(set([selected_range.left()   for selected_range in selection])) == 1
			same_right      = len(set([selected_range.right()  for selected_range in selection])) == 1
			selection_check = [same_top, same_bottom, same_left, same_right]
			
			if   selection_check == [1,1,1,1]: #only one range selected
				selected_data = self.data_in_selected_range(selection[0])

			elif selection_check == [1,1,0,0]: #multiple range with same height, get and sort data from each and combined by row 
				data_sets     = [ self.data_in_selected_range(selected_range) for selected_range in sorted(selection, key = lambda x : x.left())]
				selected_data = [list(chain.from_iterable(x)) for x in zip(*data_sets)]

			elif selection_check == [0,0,1,1]: #multiple range with same width, get and sort data from each and concate them 
				data_sets     = [ self.data_in_selected_range(selected_range) for selected_range in sorted(selection, key = lambda x : x.top())]
				selected_data = reduce(lambda i, j : i + j, data_sets)
			else:
				print("bad selection") #todo error handling
		return selected_data

	def cell_item_in_selected_range(self, selected_range):
		assert isinstance(selected_range, QItemSelectionRange)
		return self.cell_item_in_rect(selected_range.top(), selected_range.bottom(), selected_range.left(), selected_range.right())

	def data_in_selected_range(self, selected_range):
		assert isinstance(selected_range, QItemSelectionRange)
		return self.data_in_rect(selected_range.top(), selected_range.bottom(), selected_range.left(), selected_range.right())


	def cell_item_in_rect(self, top, bottom, left, right):
		assert all([ isinstance(dimension, int) for dimension in [top, bottom, left, right]])
		selected_cell = []
		for row_index in range(top, bottom+1):
			row_segment_cell = [self.data_model.item(row_index, column_index) for column_index in range(left,right+1)]
			selected_cell.append(row_segment_cell)
		return selected_cell

	def data_in_rect(self, top, bottom, left, right):
		assert all([ isinstance(dimension, int) for dimension in [top, bottom, left, right]])
		selected_data = []
		for row_index in range(top, bottom+1):
			row_segment_data = self.data_model.data_cached[row_index][left:right+1]
			selected_data.append(row_segment_data)
		return selected_data

	def data_in_cell(self, row_index, column_index):
		assert all([ isinstance(dimension, int) for dimension in [row_index, column_index]])
		return self.data_model[row_index][column_index]

	def clear_selected_ranges(self):
		for selected_range in self.selectionModel().selection():
			self.clear_selected_range(selected_range)

	def clear_selected_range(self, selected_range):
		assert isinstance(selected_range, QItemSelectionRange)
		for row_index in range(selected_range.top(), selected_range.bottom()+1):
			for column_index in range(selected_range.left(), selected_range.right()+1):
				self.data_model.data_cached[row_index][column_index] = ""
		self.update_data_model()

	def clear_selected_rows(self):
		for selected_row_index in self.selected_rows():
			self.clear_row_at(selected_row_index)

	def clear_selected_columns(self):
		for selected_column_index in self.selected_columns():
			self.clear_column_at(selected_column_index)

	def clear_column_at(self, column_index):
		self.data_model.clear_column_at(column_index)
		self.update_data_model()

	def clear_row_at(self, row_index):
		self.data_model.clear_cell_at(row_index)
		self.update_data_model()    


	def selected(self):
		for selected_range in self.selectionModel().selection():
			print (selected_range)

	def selected_rows(self):
		return [ model_index.row()    for model_index in self.selectionModel().selectedRows()]

	def selected_columns(self):
		return [ model_index.column() for model_index in self.selectionModel().selectedColumns()]

	def insert_column_before_selection(self):
		if len(self.selected_columns())==1:
			selected = self.selected_columns()[0]
			self.insert_column_at(selected)
			self.selectColumn(selected+1)

	def insert_column_after_selection(self):
		if len(self.selected_columns())==1:
			selected = self.selected_columns()[0]
			self.insert_column_at(selected+1)
			self.selectColumn(selected)

	def insert_row_before_selection(self):
		if len(self.selected_rows())==1:
			selected = self.selected_rows()[0]
			self.insert_row_at(selected)
			self.selectRow(selected+1)

	def insert_row_after_selection(self):
		if len(self.selected_rows())==1:
			selected = self.selected_rows()[0]
			self.insert_row_at(selected+1)
			self.selectRow(selected)

	def insert_row_at(self, row_index, row_counts = 1):
		self.data_model.insert_row_at(row_index)
		self.row_inserted.emit(row_index)
		self.update_data_model()	


	def insert_column_at(self, column_index, column_counts = 1):
		self.data_model.insert_column_at(column_index)
		self.column_inserted.emit(column_index)
		self.update_data_model()



	def remove_selected_rows(self):
		self.remove_row_at(self.selected_rows())


	def remove_selected_columns(self):
		self.remove_column_at(self.selected_columns())


	def remove_row_at(self, row_index):
		self.data_model.remove_row_at(row_index)
		self.row_removed.emit(row_index)
		self.update_data_model()


	def remove_column_at(self, column_index):
		self.data_model.remove_column_at(column_index)
		self.column_removed.emit(column_index)
		self.update_data_model()

	def update_data_model(self):
		self.setModel(self.data_model)
		self.model().layoutChanged.emit()
		self.selectionModel().clearSelection()
		self.data_updated.emit(self.model())
	
	def set_cell_style_at(self, row_index, column_index, **argv):
		for css_attribute in argv:
			style += ("%s : %s; " % (css_attribute, argv[css_attribute]))

		stylesheet % styles


	def showEvent(self, event):
		QTableView.showEvent(self, event)


	def keyPressEvent(self, event):
		if event.matches(QKeySequence.Copy):
			self.copy_selected_ranges()
		elif event.matches(QKeySequence.Paste):
			self.paste()
		elif event.matches(QKeySequence.Delete):
			self.clear_selected_ranges()
		else:
			QTableView.keyPressEvent(self, event)


		
	def resizeEvent(self, event):
		self.update_data_model()	
	

	def mousePressEvent (self, event):
		QTableView.mousePressEvent(self, event)
		print("mousePressEvent", event.button())

	def mouseReleaseEvent (self, event):
		QTableView.mouseReleaseEvent(self, event)
		print("mouseReleaseEvent", event.button())

	def enterEvent(self, event):
		QTableView.enterEvent(self, event)
		print("enterEvent")

	def mouseMoveEvent(self, event):
		QTableView.mouseMoveEvent(self, event)
		#the returned value is always Qt.NoButton for mouse move events.
		print("mouseMoveEvent:", event.button(), event.x(), event.y())

	def setHorizontalScrollMode(self, scroll_mode):
		QTableView.setHorizontalScrollMode(self, scroll_mode)
		self.hscroll_mode_changed.emit(scroll_mode)

	def setVerticalScrollMode(self, scroll_mode):
		QTableView.setVerticalScrollMode(self, scroll_mode)
		self.vscroll_mode_changed.emit(scroll_mode)


class DebugWindow(QMainWindow):
	def __init__(self, parent=None):
		super(DebugWindow, self).__init__(parent)
		self.table       = TableWidget(self)

		self.toolbar1     = QToolBar('Row Column function')
		self.toolbar2     = QToolBar('table function')
		self.toolbar3     = QToolBar('table formatting')

		self.a  = QAction('insert_row_before_selection', self)
		self.b  = QAction('insert_row_after_selection', self)
		self.c  = QAction('insert_column_before_selection', self)
		self.d  = QAction('insert_column_after_selection', self)
		self.e  = QAction("remove_selected_rows", self)
		self.f  = QAction("remove_selected_columns", self)
		self.g  = QAction("clear_selected_rows", self)
		self.h  = QAction("clear_selected_columns", self)       
		self.i  = QAction("clear_selected_ranges", self)
		self.j  = QAction('enable frozen view', self)
		self.k  = QAction('disable frozen view', self)
		self.l  = QAction('smooth scroll', self)
		self.m  = QAction('scroll by item', self)
		self.n  = QAction('show header', self)
		self.o  = QAction('hide header', self)
		self.p  = QAction('set bold', self)
		self.q  = QAction('set italic', self)
		self.r  = QAction('set underlined', self)
		self.s  = QAction('align left', self)
		self.t  = QAction('align center', self)
		self.u  = QAction('align right', self)
		self.v  = QAction('align top', self)
		self.w  = QAction('align middle', self)
		self.x  = QAction('align bottom', self)
		self.y  = QAction('set bd color', self)
		self.z  = QAction('set txt color', self)
		self.zz = QAction('test', self)



		self.toolbar1.addAction(self.a)
		self.toolbar1.addAction(self.b)
		self.toolbar1.addAction(self.c)
		self.toolbar1.addAction(self.d)      
		self.toolbar1.addAction(self.e)
		self.toolbar1.addAction(self.f)
		self.toolbar1.addAction(self.g)
		self.toolbar1.addAction(self.h)      
		self.toolbar2.addAction(self.i)
		self.toolbar2.addAction(self.j)
		self.toolbar2.addAction(self.k)
		self.toolbar2.addAction(self.l)
		self.toolbar2.addAction(self.m)		
		self.toolbar2.addAction(self.n)
		self.toolbar2.addAction(self.o)
		self.toolbar2.addAction(self.zz)
		self.toolbar3.addAction(self.p)
		self.toolbar3.addAction(self.q)
		self.toolbar3.addAction(self.r)
		self.toolbar3.addAction(self.s)
		self.toolbar3.addAction(self.t)
		self.toolbar3.addAction(self.u)
		self.toolbar3.addAction(self.v)
		self.toolbar3.addAction(self.w)
		self.toolbar3.addAction(self.x)
		self.toolbar3.addAction(self.y)
		self.toolbar3.addAction(self.z)

		self.a.triggered.connect(lambda _,  : self.table.insert_row_before_selection())
		self.b.triggered.connect(lambda _,  : self.table.insert_row_after_selection())
		self.c.triggered.connect(lambda _,  : self.table.insert_column_before_selection())
		self.d.triggered.connect(lambda _,  : self.table.insert_column_after_selection())
		self.e.triggered.connect(lambda _,  : self.table.remove_selected_rows())
		self.f.triggered.connect(lambda _,  : self.table.remove_selected_columns())
		self.g.triggered.connect(lambda _,  : self.table.clear_selected_rows())
		self.h.triggered.connect(lambda _,  : self.table.clear_selected_columns())
		self.i.triggered.connect(lambda _,  : self.table.clear_selected_ranges())
		self.j.triggered.connect(lambda _,  : self.table.froze_view_at_selection())
		self.k.triggered.connect(lambda _,  : self.table.disable_frozen_view())
		self.l.triggered.connect(lambda _,  : [self.table.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel), self.table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)])
		self.m.triggered.connect(lambda _,  : [self.table.setVerticalScrollMode(QAbstractItemView.ScrollPerItem), self.table.setHorizontalScrollMode(QAbstractItemView.ScrollPerItem)])
		self.n.triggered.connect(lambda _,  : [self.table.horizontalHeader().show(), self.table.verticalHeader().show()])
		self.o.triggered.connect(lambda _,  : [self.table.horizontalHeader().hide(), self.table.verticalHeader().hide()])		
		self.zz.triggered.connect(lambda _,  : self.table.selection_check())
		# self.addColAction.triggered.connect(self.table.add_column)
		# self.rmvColAction.triggered.connect(self.table.rmvCol)
		# self.testAction.triggered.connect(self.table.insert_column_at)
		

		self.addToolBar( Qt.TopToolBarArea , self.toolbar1)
		self.addToolBarBreak(Qt.TopToolBarArea)
		self.addToolBar( Qt.TopToolBarArea , self.toolbar2)
		self.addToolBarBreak(Qt.TopToolBarArea)
		self.addToolBar( Qt.TopToolBarArea , self.toolbar3)		
		data = []
		for r in range(50):
			row_data = []
			for c in range(30):
				row_data.append("cell %s, %s" % (str(r).zfill(2), str(c).zfill(2)))
			data.append(row_data)

		data[0][0] = "2.1234355"

		self.table.set_data(data)

		self.setCentralWidget(self.table)
		self.resize(1200,800)



def Debugger():
	app  = QApplication(sys.argv)
	form = DebugWindow()
	QFontDatabase.addApplicationFont("./res/font/Inconsolata-Regular.ttf");
	f = QFile("./stylesheet.css")
	f.open(QFile.ReadOnly | QFile.Text)
	ts = QTextStream(f)
	stylesheet = ts.readAll()
	app.setStyleSheet(stylesheet)
	form.show()
	app.exec_()
	




Debugger()
