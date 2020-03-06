# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QLabel, QPushButton, QWidget, QPlainTextEdit, QTextEdit
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QRect
from PyQt5.QtGui import QFont, QColor, QPainter, QTextFormat


class MoveLabel(QLabel):
    doubleClicked = pyqtSignal(bool)

    def __init__(self, *args):
        super(MoveLabel, self).__init__(*args)
        self.move_flag = None
        self.mouse_x0 = 0
        self.mouse_y0 = 0
        self.origin_x = 0
        self.origin_y = 0
        self.main_w = self.parentWidget()

    def mousePressEvent(self, evt):
        if evt.button() == Qt.LeftButton:
            self.move_flag = True
            self.mouse_x0 = evt.globalX()
            self.mouse_y0 = evt.globalY()

            self.origin_x = self.parentWidget().x()
            self.origin_y = self.parentWidget().y()

    def mouseMoveEvent(self, evt):
        if self.move_flag:
            move_x = evt.globalX() - self.mouse_x0
            move_y = evt.globalY() - self.mouse_y0
            self.main_w.move(self.origin_x + move_x, self.origin_y + move_y)

    def mouseReleaseEvent(self, evt):
        self.move_flag = False

    def mouseDoubleClickEvent(self, *args, **kwargs):
        self.doubleClicked.emit(True)


class LightBtn(QPushButton):
    def __init__(self, light_type, parent):
        super(LightBtn, self).__init__(parent)
        self.resize(20, 20)
        self.setFlat(True)
        self.setProperty('class', 'light')
        self.setObjectName(light_type)


class ToolBarBtn(QPushButton):
    def __init__(self, text, parent):
        super(ToolBarBtn, self).__init__(text, parent)
        self.setFlat(True)
        self.setFixedSize(40, 40)
        self.setProperty('class', 'toolBarBtn')


class WinBtn(QPushButton):
    def __init__(self, parent):
        super(WinBtn, self).__init__(parent)
        self.setFlat(True)
        self.resize(60, 60)
        self.setIconSize(QSize(20, 20))
        self.setProperty('class', 'winBtn')


class NumberBar(QWidget):
    def __init__(self, editor):
        QWidget.__init__(self, editor)
        self.editor = editor
        self.editor.blockCountChanged.connect(self.updateWidth)
        # updateRequest emit even if mouse is on editor
        self.editor.updateRequest.connect(self.updateContents)
        self.font = QFont()
        # self.font.setPointSize(10)
        # self.setFont(self.font)
        self.numberBarColor = QColor("#2f3a4b")
        # self.numberBarColor = QColor("#ff0000")

    def paintEvent(self, event):
        print('paint event:', event.rect())
        painter = QPainter(self)
        painter.fillRect(event.rect(), self.numberBarColor)

        block = self.editor.firstVisibleBlock()

        while block.isValid():
            blockNumber = block.blockNumber()
            block_top = self.editor.blockBoundingGeometry(block).translated(self.editor.contentOffset()).top()
            if blockNumber == self.editor.textCursor().blockNumber():
                self.font.setBold(True)
                painter.setPen(QColor("#00ff00"))
            else:
                self.font.setBold(False)
                painter.setPen(QColor("#ffffff"))
            paint_rect = QRect(0, block_top, self.width(), self.editor.fontMetrics().height())
            painter.drawText(paint_rect, Qt.AlignRight | Qt.AlignVCenter, str(blockNumber + 1))
            # painter.drawRect(paint_rect)

            block = block.next()

    def getWidth(self):
        count = self.editor.blockCount()
        if 0 <= count < 99999:
            width = self.fontMetrics().width('99999')
        else:
            width = self.fontMetrics().width(str(count))
        return width  # 35

    def updateWidth(self):
        width = self.getWidth()
        self.editor.setViewportMargins(width + 10, 0, 0, 0)

    def updateContents(self, rect, dy):
        if dy:
            self.scroll(0, dy)
        else:
            self.update(0, rect.y(), self.width(), rect.height())  # trigger paintEvent
        if rect.contains(self.editor.viewport().rect()):
            fontSize = self.editor.currentCharFormat().font().pointSize()
            self.font.setPointSize(fontSize)
            self.font.setStyle(QFont.StyleNormal)
            self.updateWidth()


class QCodeEditor(QPlainTextEdit):
    def __init__(self):
        super(QCodeEditor, self).__init__()
        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.number_bar = NumberBar(self)
        self.currentLineNumber = None
        self.cursorPositionChanged.connect(self.highLightCurrentLine)
        self.setViewportMargins(45, 0, 0, 0)
        self.highLightCurrentLine()

    def resizeEvent(self, *e):
        cr = self.contentsRect()
        rec = QRect(cr.left(), cr.top(), self.number_bar.getWidth(), cr.height())
        self.number_bar.setGeometry(rec)

    def highLightCurrentLine(self):
        newCurrentLineNumber = self.textCursor().blockNumber()
        if newCurrentLineNumber != self.currentLineNumber:
            lineColor = QColor('#222833').lighter(160)
            self.currentLineNumber = newCurrentLineNumber
            hi_selection = QTextEdit.ExtraSelection()
            hi_selection.format.setBackground(lineColor)
            hi_selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            hi_selection.cursor = self.textCursor()
            hi_selection.cursor.clearSelection()
            self.setExtraSelections([hi_selection])
