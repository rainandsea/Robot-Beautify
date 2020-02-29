# -*- coding: utf-8 -*-
from PyQt5.Qt import QApplication
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QRect, QRegExp
from PyQt5.QtGui import (
    QIcon,
    QFont,
    QColor,
    QPainter,
    QTextFormat,
    QSyntaxHighlighter,
    QTextCharFormat,
    QCursor
)
from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QTabWidget,
    QPlainTextEdit,
    QDesktopWidget,
    QTextEdit,
)


class RobotHighLighter(QSyntaxHighlighter):
    Rules = []
    Formats = {}

    def __init__(self, document):
        super(RobotHighLighter, self).__init__(document)
        print('RobotHighLighter init...')
        self.initFormats()

        RobotHighLighter.Rules.append(
            (QRegExp(r'^(\*{3} ?)([sS]ettings?|[vV]ariables?|[kK]eywords?|[tT]est [cC]ases?)( ?\*{3})$'), 'table'))
        RobotHighLighter.Rules.append(
            (QRegExp(r'^(\|\s*)?(Library|Resource|Test Timeout|Test Template|Test Teardown|Test Setup|Default Tags'
                     r'|Force Tags|Metadata|Variables|Suite Setup|Suite Teardown|Documentation)(?:(  )|( \| ))'),
             'suite_setting'))
        RobotHighLighter.Rules.append(
            (QRegExp(r'\s+\[(Documentation|Tags|Setup|Teardown|Template|Timeout|Arguments|Return)\]'),
             'case_keyword_setting'))
        RobotHighLighter.Rules.append((QRegExp(r'[\$@&amp;]\{[0-9-a-zA-Z-_ .\[\]]*\}'), 'variable'))
        RobotHighLighter.Rules.append((QRegExp(r'#[\s\S]*'), 'comment'))
        RobotHighLighter.Rules.append((QRegExp(r'^([0-9a-zA-Z_-]+( ?))+(?! +)$'), 'name'))

        # reg = QRegExp(r'^([0-9a-zA-Z_-]+( ?))+(?! +)$')
        # print(reg)
        # print(reg.indexIn('5GC001451_ET_A003_Configured_For_2sub_Sectors_With_Rank3  '))
        # print(reg.matchedLength())

    @staticmethod
    def initFormats():
        baseFormat = QTextCharFormat()
        baseFormat.setFontFamily('Courier New')
        # baseFormat.setFontPointSize(12)
        teams = [
            ['normal', Qt.white],
            ['variable', Qt.green],
            ['table', Qt.yellow],
            ['suite_setting', QColor('#ac80ff')],
            ['case_keyword_setting', QColor('#67d8ef')],
            ['comment', Qt.gray],
            ['name', QColor('#f92472')]
        ]
        for name, color in teams:
            formatter = QTextCharFormat(baseFormat)
            formatter.setForeground(QColor(color))
            if name == 'case_keyword_setting':
                formatter.setFontItalic(True)
            RobotHighLighter.Formats[name] = formatter

    def highlightBlock(self, text):
        textLength = len(text)
        prevState = self.previousBlockState()  # -1

        self.setFormat(0, textLength, RobotHighLighter.Formats['normal'])

        for regex, format in RobotHighLighter.Rules:
            i = regex.indexIn(text)
            while i >= 0:
                length = regex.matchedLength()
                self.setFormat(i, length,
                               RobotHighLighter.Formats[format])
                i = regex.indexIn(text, i + length)

    # def rehighlight(self):
    #     print('re-high light block function...')
    #     QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
    #     QSyntaxHighlighter.rehighlight(self)
    #     QApplication.restoreOverrideCursor()


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
        self.setFixedSize(30, 30)
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

    def paintEvent(self, event):
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
        self.cursorPositionChanged.connect(self.highligtCurrentLine)
        self.setViewportMargins(45, 0, 0, 0)
        self.highligtCurrentLine()

    def resizeEvent(self, *e):
        cr = self.contentsRect()
        rec = QRect(cr.left(), cr.top(), self.number_bar.getWidth(), cr.height())
        self.number_bar.setGeometry(rec)

    def highligtCurrentLine(self):
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


class RobotBeautifyWindow(QWidget):
    def __init__(self):
        super(RobotBeautifyWindow, self).__init__()
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setObjectName('mainW')
        self.deskTop = QDesktopWidget().availableGeometry()
        self.setFixedSize(self.deskTop.width(), self.deskTop.height())
        self.setWindowIcon(QIcon('logo.png'))

        self.editor = QCodeEditor()
        self.highLighter = RobotHighLighter(self.editor.document())

        self.max_width = self.deskTop.width()
        self.setupUi()

        self.showMaximized()

    def setupUi(self):
        self.createTitle()
        self.createToolsBar()
        # self.createFilesListArea()
        self.createFileDetailArea()

        self.titleLabel.doubleClicked.connect(lambda: self.move(0, 0))
        self.closeBtn.clicked.connect(self.close)
        # self.maxBtn.clicked.connect(self.show_start)
        self.minBtn.clicked.connect(self.showMinimized)

    def createTitle(self):
        self.titleLabel = MoveLabel(self)
        self.titleLabel.resize(self.max_width, 60)
        self.titleLabel.setProperty('class', 'titleLabel')
        self.titleLabel.setText("Robot  Beautify")

        self.logoLabel = QLabel(self)
        self.logoLabel.resize(30, 30)
        self.logoLabel.setObjectName('logoLabel')
        self.logoLabel.move(20, 15)

        self.redBtn = LightBtn('red', self)
        self.redBtn.move(890, 15)
        self.yellowBtn = LightBtn('yellow', self)
        self.yellowBtn.move(945, 15)
        self.greenBtn = LightBtn('green', self)
        self.greenBtn.move(1000, 15)

        # close button
        self.closeBtn = WinBtn(self)
        self.closeBtn.move(self.max_width - self.closeBtn.width(), 0)
        self.closeBtn.setIcon(QIcon("close.png"))

        # self.maxBtn = QPushButton(self)
        # self.maxBtn.setFlat(True)
        # self.maxBtn.resize(winBtnW, titleH)
        # self.maxBtn.move(self.max_width - self.closeBtn.width() - self.maxBtn.width(), 0)
        # self.maxBtn.setIcon(QIcon("max.png"))
        # self.maxBtn.setIconSize(iconS)
        # self.maxBtn.setProperty('class', 'winBtn')

        # minimum button
        self.minBtn = WinBtn(self)
        self.minBtn.move(self.max_width - self.closeBtn.width() - self.minBtn.width(), 0)
        self.minBtn.setIcon(QIcon("min.png"))

    def createToolsBar(self):
        self.toolsBar = QWidget(self)
        self.toolsBar.setFixedSize(60, 1020)
        self.toolsBar.move(0, 60)
        self.toolsBar.setObjectName('toolsBarW')

        self.newBtn = ToolBarBtn('+', self.toolsBar)
        self.openBtn = ToolBarBtn('O', self.toolsBar)
        self.saveBtn = ToolBarBtn('S', self.toolsBar)
        self.checkBtn = ToolBarBtn('C', self.toolsBar)
        self.errorBtn = ToolBarBtn('W', self.toolsBar)
        self.newBtn.move(10, 10)
        self.openBtn.move(10, 60)
        self.saveBtn.move(10, 110)
        self.checkBtn.move(10, 160)
        self.errorBtn.move(10, 210)

    # def createFilesListArea(self):
    #     self.filesListArea = QWidget(self)
    #     self.filesListArea.resize(200, 1020)
    #     self.filesListArea.move(60, 60)
    #     self.filesListArea.setObjectName('filesListArea')

    def createFileDetailArea(self):
        self.fileDetailArea = QWidget(self)
        self.fileDetailArea.resize(1860, 1020)
        self.fileDetailArea.move(60, 60)
        self.fileDetailArea.setObjectName('editW')

        self.tabs = QTabWidget(self.fileDetailArea)
        self.tabs.resize(self.tabs.parent().size())
        self.tabs.setTabShape(QTabWidget.Rounded)
        # self.tabs.setDocumentMode(True)
        # self.tabs.setMovable(True)
        self.tabs.setTabsClosable(True)
        self.tabs.setProperty('class', 'tab')

        # tab2 = QCodeEditor()
        # tab1 = QPlainTextEdit()
        # tab2 = QPlainTextEdit()
        self.tabs.addTab(self.editor, 'tab1')
        # self.tabs.addTab(tab2, 'tab2')

        self.tabs.tabCloseRequested.connect(lambda index: print(index))


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    with open("robotBeautify.qss", "r", encoding="utf-8") as f:
        app.setStyleSheet(f.read())
    rbw = RobotBeautifyWindow()
    rbw.show()
    sys.exit(app.exec_())
