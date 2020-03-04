# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QApplication, QWidget, QListWidget, QListWidgetItem, QLabel, QLineEdit, QScrollBar
from PyQt5.QtCore import QSize, Qt


class WarningItem(QWidget):
    qss = """
    QWidget#item:hover {
        background-color: red;
    }
    
    QLabel {
        padding-left: 10px;
        font-family: 'Arial';
        background-color: cyan;
    }
    
    QLabel#msg {
        font-size: 15px;
    }
    
    QLabel#line {
        font-size: 12px;
        border: none;
    }
    """

    def __init__(self, msg, line):
        super(WarningItem, self).__init__()
        self.msg = msg
        self.line = line
        self.resize(880, 70)
        self.setupUi()
        self.setObjectName('item')
        self.setStyleSheet(WarningItem.qss)

    def setupUi(self):
        msgLabel = QLabel(self.msg, self)
        msgLabel.setAlignment(Qt.AlignVCenter)
        msgLabel.setObjectName('msg')
        lineLabel = QLabel('line:%s' % self.line, self)
        lineLabel.setObjectName('line')
        lineLabel.move(0, 35)
        msgLabel.resize(self.width(), 35)
        lineLabel.resize(self.width(), 35)


class WarningWindow(QWidget):
    qss = """
    QWidget#main {
        background-color: #ebedef;
    }
    
    QLineEdit {
        margin: 5px;
        border-radius:4px;
    }
    
    QListWidget {
        border: none;
        margin: 5px;
    }
    
    QScrollBar:horizontal {
        border: 2px solid red;
        background: #32CC99;
        height: 15px;
        margin: 0px 20px 0 20px;
    }
    QScrollBar::handle:horizontal {
        background: blue;
        min-width: 20px;
    }
    QScrollBar::add-line:horizontal {
        border: 2px solid cyan;
        background: #32CC99;
        width: 20px;
        subcontrol-position: right;
        subcontrol-origin: margin;
    }
    
    QScrollBar::sub-line:horizontal {
        border: 2px solid gold;
        background: #32CC99;
        width: 20px;
        subcontrol-position: left;
        subcontrol-origin: margin;
    }
    
    QScrollBar:left-arrow:horizontal, QScrollBar::right-arrow:horizontal {
        border: 2px solid red;
        width: 3px;
        height: 3px;
        background: white;
    }

    QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
        background: green;
    }
    
    QScrollBar:vertical {
        border: 2px solid grey;
        background: #32CC99;
        width: 15px;
        margin: 22px 0 22px 0;
    }
    
    QScrollBar::handle:vertical {
        background: white;
        min-height: 20px;
    }
    QScrollBar::add-line:vertical {
        border: 2px solid grey;
        background: #32CC99;
        height: 20px;
        subcontrol-position: bottom;
        subcontrol-origin: margin;
    }
    
    QScrollBar::sub-line:vertical {
        border: 2px solid grey;
        background: #32CC99;
        height: 20px;
        subcontrol-position: top;
        subcontrol-origin: margin;
    }
    
    QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
        border: 2px solid grey;
        width: 3px;
        height: 3px;
        background: white;
    }
    
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
        background: none;
    }
    
    """

    def __init__(self):
        super(WarningWindow, self).__init__()
        # self.setMinimumWidth(900)
        # self.setMaximumWidth(1920)
        self.resize(900, 600)
        self.setWindowFlags(self.windowFlags() | Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        # self.setWindowOpacity(0.9)
        # self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # self.setAttribute(Qt.WA_TranslucentBackground, True)
        # self.setContentsMargins(10,20,30,40)
        self.setObjectName('main')

        self.setupUi()
        self.setStyleSheet(WarningWindow.qss)

    def setupUi(self):
        searchEdit = QLineEdit(self)
        searchEdit.setFixedSize(self.width(), 40)
        searchEdit.setAlignment(Qt.AlignVCenter)

        self.listW = QListWidget(self)
        self.listW.setFixedSize(self.width(), 550)
        self.listW.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.listW.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.listW.move(0, 40)

        for i in range(10):
            item = QListWidgetItem(self.listW)
            item.setSizeHint(QSize(900, 70))
            w = WarningItem('${gnb_ip} should be upper case', line=36)
            self.listW.setItemWidget(item, w)
            if i == 0:
                w.setStyleSheet('background-color: red;')

        height = self.listW.count() * 60
        if height <= 600:
            self.setFixedHeight(height)
        else:
            self.setFixedHeight(600)


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    w = WarningItem('${gnb_ip} should be upper case', line=36)
    w.show()
    sys.exit(app.exec_())
