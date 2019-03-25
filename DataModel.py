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

 
    def rowCount(self, parent):
        return len(self.data_cached)
 
    def columnCount(self, parent):
        return len(self.data_cached[0]) if self.data_cached else 0
 
    def get_value(self, index):
        i = index.row()
        j = index.column()
        return self.data_cached[i][j]
 
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
 
 