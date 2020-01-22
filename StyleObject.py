import os
import sys

from PyQt5.QtWidgets import *
from PyQt5.QtCore    import *
from PyQt5.QtGui     import *

class StyleObject(QObject):
    background_changed       = pyqtSignal(QBrush)
    background_brush_changed = pyqtSignal(QBrush)
    font_color_changed       = pyqtSignal(QColor)
    font_changed             = pyqtSignal(QFont)
    align_changed            = pyqtSignal(Qt.AlignmentFlag)
    
    def __init__(self):
        super(StyleObject, self).__init__()
        self._background       =  QBrush(QColor("#FFFFFF"), Qt.SolidPattern)
        self._background_brush =  QBrush(QColor("#FFFFFF"), Qt.SolidPattern)
        self._type_hint_color  =  QPen(QColor("#FFFFFF"))
        self._font_color       =  QColor("#FF0000")
        self._font             =  QFont()
        self._align            =  Qt.AlignRight | Qt.AlignVCenter
        self._border_style     =  Qt.SolidLine
        self._border_width     =  0
        self._bolder_color     =  "#000000"
        self.font_size = 14
        self.font_family = "consolas"

    @property
    def font(self):
        return self._font   

    @font.setter
    def font(self, font):
        self._font = font
        self.font_changed.emit(font)

    @property
    def font_size(self):
        return self._font.pointSize()  

    @font_size.setter
    def font_size(self, size):
        self._font.setPointSize(size)
        self.font_changed.emit(self._font)

    @property
    def font_color(self):
        return self._font_color
        
    @font_color.setter
    def font_color(self, color):
        self._font_color = color
        self.font_color_changed.emit(color)

    @property
    def align(self):
        return self._align

    @align.setter
    def align(self, align):
        self._align = align

    @property
    def font_family(self):
        return self._font.family()  

    @font_family.setter
    def font_family(self, family):
        self._font.setFamily(family)
        self.font_changed.emit(self._font)

    @property
    def font_bold(self):
        return self._font.bold()  

    @font_bold.setter
    def font_bold(self, bold):
        self._font.setBold(bold)
        self.font_changed.emit(self._font)

    @property
    def font_italic(self):
        return self._font.italic()  

    @font_italic.setter
    def font_italic(self, italic):
        self._font.setItalic(italic)
        self.font_changed.emit(self._font)

    @property
    def font_strike(self):
        return self._font.strikeOut()  

    @font_strike.setter
    def font_strike(self, strike):
        self._font.setStrikeOut(strike)
        self.font_changed.emit(self._font)

    @property
    def font_underline(self):
        return self._font.underline()  

    @font_underline.setter
    def font_underline(self, underline):
        self._font.setUnderline(strike)
        self.font_changed.emit(self._font)

    @property
    def background(self):
        return self._background

    @background.setter
    def background(self, brush):
        self._background = brush
        self.background_changed.emit(brush)

    @property
    def background_brush(self):
        return self._background_brush

    @background_brush.setter
    def background_brush(self, brush):
        self._background_brush = brush
        self.background_brush_changed.emit(style)

    @property
    def type_hint_color(self):
        return self._type_hint_color    

    @type_hint_color.setter
    def type_hint_color(self, color):
        self._type_hint_color = color
        self.type_hint_color_changed.emit(color)
