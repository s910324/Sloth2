import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore    import *
from MainMDIArea     import MainMDIArea
from ToolBar         import ToolBar
 
class MainWindow(QMainWindow):
	def __init__(self):
		super().__init__()
		self.title             = 'Sloth DataPlot'
		self.mdi_area          = MainMDIArea()
		self.menubar           = self.menuBar()

		self.mdi_area.add_sub_window()


		self.init_ui()
	 
	def init_ui(self):
		self.setWindowTitle(self.title)
		self.setCentralWidget(self.mdi_area)
		self.init_menubar()
		self.init_toolbar()
		self.show()

	def init_menubar(self):
		fileMenu       = self.menubar.addMenu('&File')
		editMenu       = self.menubar.addMenu('&Edit')
		viewMenu       = self.menubar.addMenu('&View')
		plotMenu       = self.menubar.addMenu('&Plot')
		colMenu        = self.menubar.addMenu('&Colume')
		wksheetMenu    = self.menubar.addMenu('&Worksheet')
		analysisMenu   = self.menubar.addMenu('&Analysis')
		statisticsMenu = self.menubar.addMenu('&Statistics')
		imageMenu      = self.menubar.addMenu('&Image')
		toolsMenu      = self.menubar.addMenu('&Tools')
		formatMenu     = self.menubar.addMenu('&Format')
		windowMenu     = self.menubar.addMenu('&Window')
		helpMenu       = self.menubar.addMenu('&Help')
 
	def init_toolbar(self):
		self.worksheet_toolbar = ToolBar('Worksheet') 
		self.addToolBar( Qt.TopToolBarArea , self.worksheet_toolbar)

		item_list = [
			["open Project",  None, 'Ctrl+Q', self.print_a],
			["new Project",	  None, None, None],
			["import date",   None, None, None],
			["add Worksheet", None, None, None],
			["add Plot",      None, None, None]
		]
		self.worksheet_toolbar.set_actions(item_list)

	def print_a(self):
		self.mdi_area.add_sub_window()

if __name__ == '__main__':
	app    = QApplication(sys.argv)
	window = MainWindow()
	sys.exit(app.exec_())
