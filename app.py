# -*- coding: utf-8 -*-
from helper.robotBeautify import RobotBeautifyWindow
from PyQt5.QtWidgets import QApplication
import sys

if __name__ == '__main__':
    app = QApplication(sys.argv)
    with open("qss/robotBeautify.qss", "r", encoding="utf-8") as f:
        app.setStyleSheet(f.read())
    rbw = RobotBeautifyWindow()
    rbw.show()
    sys.exit(app.exec_())
