#!/usr/bin/env python
import os
import sys
import types
import warnings
from PyQt5.QtWidgets import *
from PyQt5.QtCore    import *
from PyQt5.QtGui     import *
from HeaderItem      import HHeaderItem, VHeaderItem
from TableModel      import TableModel

class TableWidget(QTableView):
	trigger = pyqtSignal()
	def __init__(self, parent=None):
		super(TableWidget, self).__init__(parent)
		self.column_header = 0
		self.row_header    = 0

		self.col_count = 0
		self.row_count = 0

		table_model = TableModel(self)
 
		sort_proxy = QSortFilterProxyModel(self)
		sort_proxy.setSourceModel(table_model)
 
		self.setModel(sort_proxy)
 
		self.frozen_table_view = QTableView(self)
		self.frozen_table_view.setModel(sort_proxy)
		self.frozen_table_view.verticalHeader().hide()
		self.frozen_table_view.setFocusPolicy(Qt.NoFocus)
		self.frozen_table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
		self.frozen_table_view.setStyleSheet('''border: none; background-color: #8EDE21; selection-background-color: #999''')
		self.frozen_table_view.setSelectionModel(QAbstractItemView.selectionModel(self))
		self.frozen_table_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.frozen_table_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
 
		self.viewport().stackUnder(self.frozen_table_view)
 
		self.setEditTriggers(QAbstractItemView.SelectedClicked)
		self.setStyleSheet('font: 10pt "Courier New"')
		hh = self.horizontalHeader()
		hh.setDefaultAlignment(Qt.AlignCenter)
		hh.setStretchLastSection(True)

	def select_ranges(self):
		selection_model = self.selectionModel();
		if selection_model.hasSelection():
			print (selection_model.selectedRows())
			print(selection_model.selectedColumns())

	def test(self):
		
		for selected in self.selectedRanges():
			print (selected.rightColumn())

	def add_column(self, column_counts = 1):
		self.insert_column_at(column_index = self.columnCount(), column_counts = column_counts)		

	def insert_column_at(self, column_index = 0, column_counts = 1):
		if column_index >= 0 and column_index >= self.row_header:
			for counts in range(column_counts):
				self.insertColumn(column_index)
				self.setHorizontalHeaderItem(column_index , HHeaderItem())
			self.refresh_column_num()

		else :
			warnings.warn("\nfrom %s --> %s: invalid column index or counts" % (type(self).__name__, sys._getframe().f_code.co_name), Warning, stacklevel=2)

	def insert_column_before_selection(self):
		if len(self.selectedRanges()) == 1:
			self.insert_column_at(column_index = self.selectedRanges()[0].leftColumn())

	def insert_column_after_selection(self):
		if len(self.selectedRanges()) == 1:
			self.insert_column_at(column_index = self.selectedRanges()[0].rightColumn()+1)

	def refresh_column_num(self):
		for column_index in range(self.columnCount()):
			self.horizontalHeaderItem(column_index).set_number(column_index + 1 )
	

	def add_row(self, row_counts = 1):
		self.insert_row_at(row_index = self.rowCount(), row_counts = row_counts)		

	def insert_row_at(self, row_index = 0, row_counts = 1):
		if row_index >= 0 and row_index >= self.column_header:
			for counts in range(row_counts):
				self.insertColumn(row_index)
				self.setHorizontalHeaderItem(row_index , VHeaderItem())
			self.refresh_row_num()

		else :
			warnings.warn("\nfrom %s --> %s: invalid row index or counts" % (type(self).__name__, sys._getframe().f_code.co_name), Warning, stacklevel=2)

	def insert_row_before_selection(self):
		if len(self.selectedRanges()) == 1:
			self.insert_row_at(row_index = self.selectedRanges()[0].leftColumn())

	def insert_row_after_selection(self):
		if len(self.selectedRanges()) == 1:
			self.insert_column_at(row_index = self.selectedRanges()[0].rightColumn()+1)

	def refresh_row_num(self):
		for row_index in range(self.columnCount()):
			self.horizontalHeaderItem(row_index).set_number(row_index + 1 )
	


	def rmvCol(self):
		try: 
			selectAry    = []
			for i in range( len(self.selectedRanges())):
				leftCol  = self.selectedRanges()[i].leftColumn()
				colCount = self.selectedRanges()[i].columnCount()
				for j in range( leftCol, leftCol + colCount ):
					selectAry.append( j )

			for i in range( len ( selectAry )):
				self.removeColumn(selectAry[i] - i)
				self.col_count -= 1
			return selectAry
		except AttributeError:
			raise AttributeError


	def rmvRow(self):
		try:
			selectAry    = []
			for i in range( len(self.selectedRanges())):
				topRow   = self.selectedRanges()[i].topRow()
				rowCount = self.selectedRanges()[i].rowCount()
				for j in range( topRow, topRow + rowCount ):
					selectAry.append( j )

			for i in range( len ( selectAry )):
				if (selectAry[i] - i) > 2:
					self.removeRow(selectAry[i] - i)
			return selectAry
					
		except AttributeError:
			raise AttributeError


	def setAxis(self, axis):
		axisAry          = [ 'X', 'Y', 'Z' ]
		try:
			selectAry    = []
			for i in range( len(self.selectedRanges())):
				leftCol  = self.selectedRanges()[i].leftColumn()
				colCount = self.selectedRanges()[i].columnCount()
				for j in range( leftCol, leftCol + colCount ):
					selectAry.append( j )
			for currentCol in selectAry:
				headerLable  = axisAry[axis]
				headerLable += str(self.horizontalHeaderItem(currentCol).text())[1:]
				self.setHorizontalHeaderItem(currentCol, QTableWidgetItem(headerLable))
		except AttributeError:
			raise AttributeError


	def getSelectedData(self):
		try:
			dataSet     = []
			selectArray = []
			axisArray   = []
			clusters    = [[]]
			clusterNum  = 0

			for selected in self.selectedRanges():
				leftCol  = selected.leftColumn()
				colCount = selected.columnCount()
				for index in range(leftCol, leftCol+colCount, 1):
					selectArray.append(index)

			selectArray = sorted(selectArray)

			for i in (selectArray):
				if (str(self.horizontalHeaderItem(i).text())[0]) == 'X':
					axisArray.append(i)
					clusters.append([i])
					clusterNum += 1

				elif (str(self.horizontalHeaderItem(i).text())[0]) == 'Y':
					clusters[clusterNum].append(i)

			# return selectArray, clusters
			for k in clusters:
				for i in k[1:]:
					plotArrayX = []
					plotArrayY = []
					for j in range(2, self.rowCount()):
						itemX = self.item(j,k[0])
						itemY = self.item(j,i)
						if ((type(itemX) == types.NoneType) + (type(itemY) == types.NoneType)) == 0:
							try:
								[ItemXChk, ItemYChk] = [float(itemX.text()), float(itemY.text())]
								plotArrayX.append(float(itemX.text()))
								plotArrayY.append(float(itemY.text()))
							except ValueError:
								print ('ValueError at: row# '       + str(j+1))
							except TypeError:
								print ('TypeError at: row# '        + str(j+1))
							except AttributeError:
								print ('AttributionError at: row# ' + str(j+1))
					dataSet.append([plotArrayX, plotArrayY])
			return selectArray, dataSet
		except AttributeError:
			raise AttributeError


	def keyPressEvent(self, event):
		if event.matches(QKeySequence.Copy):
			self.copy()
		elif event.matches(QKeySequence.Paste):
			self.paste()
		elif event.matches(QKeySequence.Delete):
			self.delete()
		else:
			QTableWidget.keyPressEvent(self, event)

	def copy(self):
		self.tableHandle = self
		selectIdx = []
		if len(self.tableHandle.selectedRanges()) != 0:
			for i in range( len( self.tableHandle.selectedRanges())):
				leftCol  = self.tableHandle.selectedRanges()[i].leftColumn()
				colCount = self.tableHandle.selectedRanges()[i].columnCount()
				topRow   = self.tableHandle.selectedRanges()[i].topRow()
				rowCount = self.tableHandle.selectedRanges()[i].rowCount()
				for currentCol in range( leftCol, leftCol + colCount ):
					row = []
					selectIdx.append([ currentCol, row ])
					for currentRow in range( topRow, topRow + rowCount ):
						row.append(currentRow )                    


		for i in range(len(selectIdx)):
			for j in range( i+1, len(selectIdx), 1):
				try:
					if selectIdx[i][0] == selectIdx[j][0]:
						selectIdx[i][1].extend(selectIdx[j][1])
						selectIdx[j].pop(0)
						selectIdx[j].pop(0)
				except IndexError:
					print ('item({0},{1}) not exist.'.format(i, j))
		copycheck = True
		
		selectIdx =  filter(None, selectIdx)
		
		for i in range(len(selectIdx)-1):
			if len(selectIdx[i][1]) != len(selectIdx[i+1][1]):
				copycheck =False
				print ('alert')
				break
		
		if copycheck == True:
			selectIdx.sort()
			for i in range(len(selectIdx)):
				selectIdx[i][1].sort()
	
			print (selectIdx)
			copyText = ''
			for col in selectIdx:
				for row in col[1]:
					item = self.item(row, col[0])
					if item:
						copyText += item.text()
					copyText += '\t'
				copyText += '\n'
			QApplication.clipboard().setText(copyText)
			print ('copied text: ' + copyText)


	def paste(self):
		pasteAry = []
		self.tableHandle = self
		[ currCol, currRow ]= [self.tableHandle.currentColumn(), self.tableHandle.currentRow()]
		for i in QApplication.clipboard().text().strip().split('\n'):
			pasteAry.append(i.strip().split('\t'))
		RowNum = 0
		ColNum =len(pasteAry)
		if currCol + currRow != -2:
			for i in range(len(pasteAry)):
				RowNum = len(pasteAry[i]) if RowNum < len(pasteAry[i]) else RowNum
				for j in range(len(pasteAry[i])):
					self.tableHandle.setItem( currRow + j, currCol + i,  QTableWidgetItem(pasteAry[i][j]))
		self.setRangeSelected(QTableWidgetSelectionRange(currRow, currCol, currRow + RowNum -1, currCol + ColNum -1), True)

		
		'''still need to expand table if array is too big fo it'''

	def delete(self):
		self.tableHandle = self
		selectIdx = []
		if len(self.tableHandle.selectedRanges()) != 0:
			for i in range( len( self.tableHandle.selectedRanges())):
				leftCol  = self.tableHandle.selectedRanges()[i].leftColumn()
				colCount = self.tableHandle.selectedRanges()[i].columnCount()
				topRow   = self.tableHandle.selectedRanges()[i].topRow()
				rowCount = self.tableHandle.selectedRanges()[i].rowCount()
				for currentCol in range( leftCol, leftCol + colCount ):
					row = []
					selectIdx.append([ currentCol, row ])
					for currentRow in range( topRow, topRow + rowCount ):
						row.append(currentRow )
		for i in selectIdx:
			col = i[0]
			for row in i[1]:
				self.setItem(row, col, QTableWidgetItem(''))


class DebugWindow(QMainWindow):
	def __init__(self, parent=None):
		super(DebugWindow, self).__init__(parent)
		self.table       = TableWidget()
		self.toolbar     = QToolBar('main function')
		self.selectAction  = QAction('select', self)
		self.addColAction  = QAction('add Col', self)
		self.rmvColAction  = QAction('rmv Col', self)
		self.addbefore    = QAction('add before', self)
		self.addafter    = QAction('add after', self)

		self.testAction    = QAction('test', self)
		self.testAction2    = QAction('test2', self)

		self.toolbar.addAction(self.selectAction)
		self.toolbar.addAction(self.addColAction)
		self.toolbar.addAction(self.rmvColAction)
		self.toolbar.addAction(self.addbefore)		
		self.toolbar.addAction(self.addafter)		
		self.toolbar.addAction(self.testAction)
		self.toolbar.addAction(self.testAction2)
		
		self.selectAction.triggered.connect(self.table.getSelectedData)
		self.addColAction.triggered.connect(self.table.add_column)
		self.rmvColAction.triggered.connect(self.table.rmvCol)
		self.testAction.triggered.connect(self.table.insert_column_at)
		self.testAction2.triggered.connect(self.table.test)
		self.addbefore.triggered.connect(self.table.insert_column_before_selection)
		self.addafter.triggered.connect(self.table.insert_column_after_selection)
		self.addToolBar( Qt.TopToolBarArea , self.toolbar)

		self.table.setRowCount(200)
		self.table.add_column(15)

		self.setCentralWidget(self.table)
		self.resize(800,800)

def Debugger():
	app  = QApplication(sys.argv)
	form = DebugWindow()
	form.show()
	app.exec_()

Debugger()