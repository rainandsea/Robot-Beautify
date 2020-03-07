# -*- coding: utf-8 -*-
from .robotCheckThread import RobotCheckThread
from .robotBeautifyThread import RobotBeautifyThread
from .widgetFactory import QCodeEditor, WinBtn, MoveLabel, LightBtn, ToolBarBtn
from PyQt5.Qt import QApplication
from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import (
    QIcon,
    QColor,
    QSyntaxHighlighter,
    QTextCharFormat,
)
from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QTabWidget,
    QDesktopWidget,
    QFileDialog
)
import os


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


class RobotBeautifyWindow(QWidget):
    def __init__(self):
        super(RobotBeautifyWindow, self).__init__()
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setObjectName('mainW')
        self.deskTop = QDesktopWidget().availableGeometry()
        self.setFixedSize(self.deskTop.width(), self.deskTop.height())
        self.setWindowIcon(QIcon('./images/logo.png'))
        self.maxWidth = self.deskTop.width()

        # self.warningWindow = QWidget()
        # self.warningWindow.show()

        """init file params"""
        self.openFilePath = ''
        self.saveFilePath = ''
        self.filesDict = {}
        self.editors = {}

        """init some params"""
        self.warningNum = 1

        self.setupUi()

        self.showMaximized()

    def setupUi(self):
        self.createTitle()
        self.createToolsBar()
        # self.createFilesListArea()
        self.createFileDetailArea()
        self.createStatusBar()

        self.titleLabel.doubleClicked.connect(lambda: self.move(0, 0))
        self.closeBtn.clicked.connect(self.close)
        # self.maxBtn.clicked.connect(self.show_start)
        self.minBtn.clicked.connect(self.showMinimized)
        self.newBtn.clicked.connect(self.__addNewTab)
        self.openBtn.clicked.connect(self.__openFile)
        self.saveBtn.clicked.connect(self.__saveFile)
        self.beautifyBtn.clicked.connect(self.__formatContent)
        self.warningBtn.clicked.connect(self.__changeLight)

    def __changeLight(self):
        self.__initLightPos()
        self.lightBtn = [self.redBtn, self.yellowBtn, self.greenBtn]
        if self.warningNum == 0:
            index = 2
        elif self.warningNum <= 10:
            index = 1
        else:
            index = 0
        self.lightBtn[index].move(880 + 55 * index, 10)
        self.lightBtn[index].resize(40, 40)
        self.lightBtn[index].setStyleSheet('border-radius: 20px;')
        if self.warningNum > 10:
            self.warningNum = 0
        else:
            self.warningNum += 5

    def __initLightPos(self):
        for index, btn in enumerate([self.redBtn, self.yellowBtn, self.greenBtn]):
            btn.move(890 + 55 * index, 20)
            btn.resize(20, 20)
            btn.setStyleSheet('border-radius: 10px;')

    def createTitle(self):
        self.titleLabel = MoveLabel(self)
        self.titleLabel.resize(self.maxWidth, 60)
        self.titleLabel.setProperty('class', 'titleLabel')
        self.titleLabel.setText("Robot  Beautify")

        self.logoLabel = QLabel(self)
        self.logoLabel.resize(30, 30)
        self.logoLabel.setObjectName('logoLabel')
        self.logoLabel.move(20, 15)

        self.redBtn = LightBtn('red', self)
        self.redBtn.move(890, 20)
        self.yellowBtn = LightBtn('yellow', self)
        self.yellowBtn.move(945, 20)
        self.greenBtn = LightBtn('green', self)
        self.greenBtn.move(1000, 20)

        # close button
        self.closeBtn = WinBtn(self)
        self.closeBtn.move(self.maxWidth - self.closeBtn.width(), 0)
        self.closeBtn.setIcon(QIcon("./images/close.png"))

        # minimum button
        self.minBtn = WinBtn(self)
        self.minBtn.move(self.maxWidth - self.closeBtn.width() - self.minBtn.width(), 0)
        self.minBtn.setIcon(QIcon("./images/min.png"))

    def createToolsBar(self):
        self.toolsBar = QWidget(self)
        self.toolsBar.setFixedSize(60, 970)
        self.toolsBar.move(0, 60)
        self.toolsBar.setObjectName('toolsBarW')

        self.newBtn = ToolBarBtn('+', self.toolsBar)
        self.openBtn = ToolBarBtn('O', self.toolsBar)
        self.saveBtn = ToolBarBtn('S', self.toolsBar)
        self.beautifyBtn = ToolBarBtn('B', self.toolsBar)
        self.warningBtn = ToolBarBtn('W', self.toolsBar)
        self.newBtn.setShortcut('ctrl+n')  # no need space
        self.openBtn.setShortcut('ctrl+o')
        self.saveBtn.setShortcut('ctrl+s')
        self.beautifyBtn.setShortcut('ctrl+b')
        self.warningBtn.setShortcut('ctrl+w')
        self.newBtn.move(10, 10)
        self.openBtn.move(10, 60)
        self.saveBtn.move(10, 110)
        self.beautifyBtn.move(10, 160)
        self.warningBtn.move(10, 210)

    # def createFilesListArea(self):
    #     self.filesListArea = QWidget(self)
    #     self.filesListArea.resize(200, 1020)
    #     self.filesListArea.move(60, 60)
    #     self.filesListArea.setObjectName('filesListArea')

    def createFileDetailArea(self):
        self.fileDetailArea = QWidget(self)
        self.fileDetailArea.resize(1860, 940)
        self.fileDetailArea.move(60, 60)
        self.fileDetailArea.setObjectName('editW')

        self.tabs = QTabWidget(self.fileDetailArea)
        self.tabs.resize(self.tabs.parent().size())
        self.tabs.setTabShape(QTabWidget.Rounded)
        # self.tabs.setDocumentMode(True)
        # self.tabs.setMovable(True)
        self.tabs.setTabsClosable(True)
        self.tabs.setProperty('class', 'tab')

        defaultEditor = QCodeEditor()
        self.editors['untitled'] = [defaultEditor, RobotHighLighter(defaultEditor.document())]
        self.tabs.addTab(defaultEditor, 'untitled')

        self.tabs.currentChanged.connect(self.__tabChanged)
        self.tabs.tabCloseRequested.connect(self.__tabClosed)

    def createStatusBar(self):
        self.statusBar = QLabel(self)
        self.statusBar.setFixedSize(self.width(), 30)
        self.statusBar.setObjectName('statusBar')
        self.statusBar.move(0, self.height() - self.statusBar.height())

    def __checkContent(self):
        text = self.tabs.currentWidget().toPlainText()
        if not text:
            return None
        self.rc = RobotCheck(text)  # must exit as an instant property to keep alive after function end
        self.rc.done.connect(self.__checkDone)
        self.rc.start()

    def __checkDone(self, warnings):
        print(warnings)

    def __formatContent(self):
        text = self.tabs.currentWidget().toPlainText()
        if not text:
            return None
        self.fc = RobotFormatter(text)
        self.fc.done.connect(self.__formatDone)
        self.fc.start()

    def __formatDone(self, content):
        self.editors[self.tabs.tabText(self.tabs.currentIndex())][0].setPlainText(content)

    def __addNewTab(self):
        if 'untitled' in self.editors.keys():
            self.statusBar.setText('Please save untitled file before create a new one...')
            return None
        defaultEditor = QCodeEditor()
        self.editors['untitled'] = [defaultEditor, RobotHighLighter(defaultEditor.document())]
        self.tabs.addTab(defaultEditor, 'untitled')
        self.tabs.setCurrentIndex(self.tabs.count() - 1)

    def __tabClosed(self, index):
        count = self.tabs.count()
        key = self.tabs.tabText(index)
        self.tabs.removeTab(index)
        del self.editors[key]

        if count == 1:
            self.__addNewTab()

    def __tabChanged(self, index):
        self.statusBar.setText(self.filesDict.get(self.tabs.tabText(index), ''))

    def __openFile(self):
        if not self.openFilePath:
            file = QFileDialog().getOpenFileName(parent=self,
                                                 caption='Select File',
                                                 directory=os.path.join(os.path.expanduser("~"), 'Desktop'),
                                                 filter='Robot Files(*.robot)')
        else:
            file = QFileDialog().getOpenFileName(self,
                                                 caption='Select File',
                                                 directory=self.openFilePath,
                                                 filter='Robot Files(*.robot)')
        if file[0]:
            self.openFilePath = os.path.dirname(file[0])
            tmp = self.tabs.tabText(self.tabs.currentIndex())
            key = file[0].split('/')[-1]
            self.filesDict[key] = file[0]
            if not tmp.endswith('.robot'):  # untitled
                self.editors[key] = self.editors.get(tmp)
                del self.editors[tmp]
                self.tabs.setTabText(self.tabs.currentIndex(), key)
            else:
                editor = QCodeEditor()
                self.editors[key] = [editor, RobotHighLighter(editor.document())]
                self.tabs.insertTab(self.tabs.count(), editor, key)
                self.tabs.setCurrentIndex(self.tabs.count() - 1)
            self.__tabChanged(self.tabs.currentIndex())
            with open(file[0], 'r') as f:
                for line in f.readlines():
                    self.editors.get(key)[0].appendPlainText(line.strip('\n'))

    def __saveFile(self):
        key = self.tabs.tabText(self.tabs.currentIndex())
        if key == 'untitled':
            if not self.saveFilePath:
                file = QFileDialog().getSaveFileName(parent=self,
                                                     caption='Save File',
                                                     directory=os.path.join(os.path.expanduser("~"), 'untitled'),
                                                     filter='Robot Files(*.robot)')
            else:
                file = QFileDialog().getSaveFileName(self,
                                                     caption='Save File',
                                                     directory=self.saveFilePath,
                                                     filter='Robot Files(*.robot)')
            if file[0]:
                self.saveFilePath = os.path.dirname(file[0])
                print('saveFilePath:', self.saveFilePath)
                fileName = file[0]
                key = file[0].split('/')[-1]
                self.filesDict[key] = file[0]
                self.editors[key] = self.editors.get('untitled')
                del self.editors['untitled']
                self.tabs.setTabText(self.tabs.currentIndex(), key)
                self.__tabChanged(self.tabs.currentIndex())
            else:
                fileName = ''
        else:
            fileName = self.filesDict.get(key)
        if fileName:
            with open(fileName, 'w') as f:
                text = self.tabs.currentWidget().toPlainText()
                print(text)
                f.write(text)
            self.__checkContent()


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    with open("../qss/robotBeautify.qss", "r", encoding="utf-8") as f:
        app.setStyleSheet(f.read())
    rbw = RobotBeautifyWindow()
    rbw.show()
    sys.exit(app.exec_())
