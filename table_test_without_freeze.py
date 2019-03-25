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
from DataModel       import DataModel
from functools       import reduce
from itertools       import chain
class TableWidget(QTableView):
	trigger = pyqtSignal()
	def __init__(self, data = [], parent=None):
		super(TableWidget, self).__init__(parent)
		self.data_model = DataModel(self)
		

	def set_data(self, data):
		if data:
			self.data_model.data_cached = data
			self.update_data_model()

	def selection_check(self):

		self.setItemDelegateForRow() QAbstractItemDelegate


		# for i in range(4,8):
		# 	for j in range(3, 6):
		# 		m = self.model().index(i, j)
		# 		self.selectionModel().select(m, QItemSelectionModel.Select)
		
		
		# print (self.selectionModel().selection())

	def copy_selected_ranges(self):
		selected_data = self.data_in_selected_ranges(self.selectionModel().selection())
		clip_board_text = ('\n'.join(['\t'.join(map(str, row_data)) for row_data in selected_data]))
		QApplication.clipboard().setText(clip_board_text)
		return clip_board_text

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


	def data_in_selected_range(self, selected_range):
		assert isinstance(selected_range, QItemSelectionRange)
		return self.data_in_rect(selected_range.top(), selected_range.bottom(), selected_range.left(), selected_range.right())

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

	def clear_row_at(self, row_index):
		row_data = self.data_model.data_cached[row_index]
		self.data_model.data_cached[row_index] = [ "" for data in range(len(row_data))]
		self.update_data_model()

	def clear_column_at(self, column_index):
		_ =[ each_row_data.__setitem__(column_index, "") for each_row_data in self.data_model.data_cached]
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
			self.insert_column_at(self.selected_columns()[0])
			self.selectColumn(self.selected_columns()[0]+1)

	def insert_column_after_selection(self):
		if len(self.selected_columns())==1:
			self.insert_column_at(self.selected_columns()[0]+1)

	def insert_row_before_selection(self):
		if len(self.selected_rows())==1:
			self.insert_row_at(self.selected_rows()[0])
			self.selectRow(self.selected_rows()[0]+1)

	def insert_row_after_selection(self):
		if len(self.selected_rows())==1:
			self.insert_row_at(self.selected_rows()[0]+1)		
		
	def insert_row_at(self, row_index, row_counts = 1):
		for new_rows in range(row_counts):
			if self.data_model.data_cached:
				self.data_model.data_cached.insert(row_index, ["" for each_column in range(len(self.data_model.data_cached[0]))])
			else:
				self.data_model.data_cached.append([""])

		self.update_data_model()

	def insert_column_at(self, column_index, column_counts = 1):
		for new_columns in range(column_counts):
			if self.data_model.data_cached:
				_ =[ each_row.insert(column_index, "") for each_row in self.data_model.data_cached]
				
			else:
				self.data_model.data_cached.append([""])

		self.update_data_model()

	def delete_selected_rows(self):
		for selected_row_index in sorted(self.selected_rows(), reverse=True):
			self.delete_row_at(selected_row_index)

	def delete_selected_columns(self):
		for selected_column_index in sorted(self.selected_columns(), reverse=True):
			self.delete_column_at(selected_column_index)

	def delete_row_at(self, row_index):
		self.data_model.data_cached.pop(row_index)
		self.selectionModel().clearSelection()
		self.update_data_model()

	def delete_column_at(self, column_index):
		_ = [ each_row.pop(column_index) for each_row in self.data_model.data_cached]
		self.selectionModel().clearSelection()		
		self.update_data_model()		
		
	def update_data_model(self):
		self.setModel(self.data_model)
		self.model().layoutChanged.emit()




	def keyPressEvent(self, event):
		if event.matches(QKeySequence.Copy):
			self.copy_selected_ranges()
		elif event.matches(QKeySequence.Paste):
			self.paste()
		elif event.matches(QKeySequence.Delete):
			self.clear_selected_ranges()
		else:
			QTableView.keyPressEvent(self, event)


class DebugWindow(QMainWindow):
	def __init__(self, parent=None):
		super(DebugWindow, self).__init__(parent)
		self.table       = TableWidget()
		self.toolbar     = QToolBar('main function')

		self.a  = QAction('insert_row_before_selection', self)
		self.b  = QAction('insert_row_after_selection', self)
		self.c  = QAction('insert_column_before_selection', self)
		self.d  = QAction('insert_column_after_selection', self)
		self.e  = QAction("delete_selected_rows", self)
		self.f  = QAction("delete_selected_columns", self)
		self.g  = QAction("clear_selected_rows", self)
		self.h  = QAction("clear_selected_columns", self)		
		self.i  = QAction("clear_selected_ranges", self)
		self.z  = QAction('temp', self)



		self.toolbar.addAction(self.a)
		self.toolbar.addAction(self.b)
		self.toolbar.addAction(self.c)
		self.toolbar.addAction(self.d)      
		self.toolbar.addAction(self.e)
		self.toolbar.addAction(self.f)
		self.toolbar.addAction(self.g)
		self.toolbar.addAction(self.h)		
		self.toolbar.addAction(self.i)

		self.toolbar.addAction(self.z)

		self.a.triggered.connect(lambda _,  : self.table.insert_row_before_selection())
		self.b.triggered.connect(lambda _,  : self.table.insert_row_after_selection())
		self.c.triggered.connect(lambda _,  : self.table.insert_column_before_selection())
		self.d.triggered.connect(lambda _,  : self.table.insert_column_after_selection())
		self.e.triggered.connect(lambda _,  : self.table.delete_selected_rows())
		self.f.triggered.connect(lambda _,  : self.table.delete_selected_columns())
		self.g.triggered.connect(lambda _,  : self.table.clear_selected_rows())
		self.h.triggered.connect(lambda _,  : self.table.clear_selected_columns())
		self.i.triggered.connect(lambda _,  : self.table.clear_selected_ranges())
		self.z.triggered.connect(lambda _,  : self.table.selection_check())
		# self.addColAction.triggered.connect(self.table.add_column)
		# self.rmvColAction.triggered.connect(self.table.rmvCol)
		# self.testAction.triggered.connect(self.table.insert_column_at)
		

		self.addToolBar( Qt.TopToolBarArea , self.toolbar)

		data = [
						[111, 'cell12', 'cell13', 'cell14', 'cell15', 'cell12', 'cell13', 'cell14', 'cell15', 'cell16'],
						[112, 'cell22', 'cell23', 'cell24', 'cell25', 'cell26', 'cell27', 'cell28', 'cell29', 'cell30'],
						[113, 'cell32', 'cell33', 'cell34', 'cell35', 'cell36', 'cell37', 'cell38', 'cell39', 'cell40'],
						[114, 'cell42', 'cell43', 'cell44', 'cell45', 'cell46', 'cell47', 'cell48', 'cell49', 'cell50'],
						[115, 'cell52', 'cell53', 'cell54', 'cell55', 'cell56', 'cell57', 'cell58', 'cell59', 'cell60'],
						[116, 'cell62', 'cell63', 'cell64', 'cell65', 'cell66', 'cell67', 'cell68', 'cell69', 'cell70'],
						[117, 'cell72', 'cell73', 'cell74', 'cell75', 'cell76', 'cell77', 'cell78', 'cell79', 'cell80'],
						[118, 'cell82', 'cell83', 'cell84', 'cell85', 'cell86', 'cell87', 'cell88', 'cell89', 'cell90'],
						[119, 'cell12', 'cell13', 'cell14', 'cell15', 'cell12', 'cell13', 'cell14', 'cell15', 'cell16'],
						[120, 'cell22', 'cell23', 'cell24', 'cell25', 'cell26', 'cell27', 'cell28', 'cell29', 'cell30'],
						[121, 'cell32', 'cell33', 'cell34', 'cell35', 'cell36', 'cell37', 'cell38', 'cell39', 'cell40'],
						[122, 'cell42', 'cell43', 'cell44', 'cell45', 'cell46', 'cell47', 'cell48', 'cell49', 'cell50'],
						[123, 'cell52', 'cell53', 'cell54', 'cell55', 'cell56', 'cell57', 'cell58', 'cell59', 'cell60'],
						[124, 'cell62', 'cell63', 'cell64', 'cell65', 'cell66', 'cell67', 'cell68', 'cell69', 'cell70'],
						[125, 'cell72', 'cell73', 'cell74', 'cell75', 'cell76', 'cell77', 'cell78', 'cell79', 'cell80'],
						[126, 'cell82', 'cell83', 'cell84', 'cell85', 'cell86', 'cell87', 'cell88', 'cell89', 'cell90'],
						[127, 'cell12', 'cell13', 'cell14', 'cell15', 'cell12', 'cell13', 'cell14', 'cell15', 'cell16'],
						[128, 'cell22', 'cell23', 'cell24', 'cell25', 'cell26', 'cell27', 'cell28', 'cell29', 'cell30'],
						[129, 'cell32', 'cell33', 'cell34', 'cell35', 'cell36', 'cell37', 'cell38', 'cell39', 'cell40'],
						[130, 'cell42', 'cell43', 'cell44', 'cell45', 'cell46', 'cell47', 'cell48', 'cell49', 'cell50'],
						[131, 'cell52', 'cell53', 'cell54', 'cell55', 'cell56', 'cell57', 'cell58', 'cell59', 'cell60'],
						[132, 'cell62', 'cell63', 'cell64', 'cell65', 'cell66', 'cell67', 'cell68', 'cell69', 'cell70'],
						[133, 'cell72', 'cell73', 'cell74', 'cell75', 'cell76', 'cell77', 'cell78', 'cell79', 'cell80'],
						[134, 'cell82', 'cell83', 'cell84', 'cell85', 'cell86', 'cell87', 'cell88', 'cell89', 'cell90'],
						[135, 'cell82', 'cell83', 'cell84', 'cell85', 'cell86', 'cell87', 'cell88', 'cell89', 'cell90'],
						[136, 'cell82', 'cell83', 'cell84', 'cell85', 'cell86', 'cell87', 'cell88', 'cell89', 'cell90']
					]

		self.table.set_data(data)

		self.setCentralWidget(self.table)
		self.resize(800,800)

def Debugger():
	app  = QApplication(sys.argv)
	form = DebugWindow()
	form.show()
	app.exec_()

Debugger()