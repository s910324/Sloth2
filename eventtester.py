# import os
# import sys
# import math
# from PyQt5.QtWidgets import *
# from PyQt5.QtCore    import *


# class EventTester(QWidget):

# 	def __init__(self):
# 		QWidget.__init__(self)
# 		self.resize(800, 800)


# 	def mousePressEvent (self, event):
# 		print("mousePressEvent", event.button())

# 	def mouseReleaseEvent (self, event):
# 		print("mouseReleaseEvent", event.button())
		
# 	def moveEvent(self, event):
# 		print("widget moveEvent")

# 	def enterEvent(self, event):
# 		print("enterEvent")

# 	def mouseMoveEvent(self, event):
# 		#the returned value is always Qt.NoButton for mouse move events.
# 		print("mouseMoveEvent:", event.button(), event.x(), event.y())

# 	def leaveEvent(self, event):
# 		print("leaveEvent")

# def Debugger():
# 	app  = QApplication(sys.argv)
# 	form = EventTester()
# 	form.show()
# 	app.exec_()

# Debugger()

from PyQt5 import QtWidgets, QtGui, QtCore

class_values = ["zero", "one", "two"]

class Cell(QtWidgets.QWidget):
    def initFromItem(self, item):
        self.setProperty('dataClass', class_values[int(item.text())])

class TDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, *a):
        super(TDelegate, self).__init__(*a)
        self.cell = Cell(self.parent())

    def paint(self, painter, option, index):
        item = index.model().itemFromIndex(index)
        self.cell.initFromItem(item)
        self.initStyleOption(option, index)
        style = option.widget.style() if option.widget else QtWidgets.QApplication.style()
        style.unpolish(self.cell)
        style.polish(self.cell)
        style.drawControl(QtWidgets.QStyle.CE_ItemViewItem, option, painter, self.cell)

class TTableModel(QtGui.QStandardItemModel):
    def __init__(self, parent=None):
        super(TTableModel, self).__init__(parent)
        for i in range(5):
            self.appendRow([QtGui.QStandardItem(str((x+i) % 3)) for x in range(5)])

class TTableView(QtWidgets.QTableView):
    def __init__(self, parent=None):
        super(TTableView, self).__init__(parent)
        self.setItemDelegate(TDelegate(self))

class Main(QtWidgets.QMainWindow):
    def __init__(self):
        super(Main, self).__init__()
        self.table = TTableView(self)
        self.model = TTableModel(self)
        self.table.setModel(self.model)
        self.setCentralWidget(self.table)

if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet("""
Cell[dataClass=zero]::item { background-color: gray; }
Cell[dataClass=one]::item { background-color: green; font-style: italic }
Cell[dataClass=two]::item { font-weight: bold }
""")
    mainWin = Main()
    mainWin.show()
    sys.exit(app.exec_())