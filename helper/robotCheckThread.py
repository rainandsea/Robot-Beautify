# -*- coding: utf-8 -*-
from PyQt5.QtCore import QThread, pyqtSignal
from .robotContentProcess import RobotContentProcess

ROBOT_WARNINGS = []
W = [
    'should not contain "-"',
    'should not contain "_"',
    'should not contain blank space',
    'should be capitalized',
    'should be upper case',
    'should not be used',
    'should have a length not greater than 100',
    'self-defined kw but not used'
]


class RobotCheckThread(QThread):
    done = pyqtSignal(list)

    def __init__(self, content=''):
        super(RobotCheckThread, self).__init__()
        self.conPro = ContentProcess(content)
        self.init_content = content
        self.warnings = []

    def run(self):
        try:
            self.conPro.run()
            names_set = self.conPro.names_set
            names_var = self.conPro.names_var
            names_case = self.conPro.names_case
            names_kw = self.conPro.names_kw
            self_kw = self.conPro.self_kw

            ROBOT_WARNINGS.clear()
            self.__get_warning_pos(names_set, 0)
            self.__get_warning_pos(names_var, 1)
            self.__get_warning_pos(names_case, 2)
            self.__get_warning_pos(names_kw, 3)
            self.__is_self_kw_used(self_kw)

            self.done.emit(ROBOT_WARNINGS)
        except Exception as e:
            with open('../log.txt', 'a+') as f:
                f.write(str(e) + '\n')
        else:
            pass

    def __get_warning_pos(self, names, index):
        self.content = self.init_content
        self.line_list = self.content.split('\n')
        self.start = 0
        for name in names:
            if index == 0:
                res, msg = self.__is_set_name_recommend(name)
                if not res:
                    num = self.__get_line_num(name)
                    self.warnings.append(num)
                    ROBOT_WARNINGS.append(
                        [name + ' ' + msg, num])
            if index == 1:
                res, msg = self.__is_var_recommend(name)
                if not res:
                    num = self.__get_line_num(name)
                    self.warnings.append(num)
                    ROBOT_WARNINGS.append(
                        [name + ' ' + msg, num])
            if index == 2:
                res, msg = self.__is_case_name_recommend(name)
                if not res:
                    num = self.__get_line_num(name)
                    self.warnings.append(num)
                    ROBOT_WARNINGS.append(
                        [name + ' ' + msg, num])
            if index == 3:
                res, msg = self.__is_keyword_recommend(name)
                if not res:
                    num = self.__get_line_num(name)
                    self.warnings.append(num)
                    ROBOT_WARNINGS.append(
                        [name + ' ' + msg, num])

    @staticmethod
    def __is_set_name_recommend(name):
        if name == '...':
            return True, None
        if not name.istitle():
            return False, W[3]
        return True, None

    @staticmethod
    def __is_var_recommend(var):
        if '-' in var:
            return False, W[0]
        if ' ' in var:
            return False, W[2]
        if not var.isupper():
            return False, W[4]
        return True, None

    @staticmethod
    def __is_case_name_recommend(case_name):
        if len(case_name) >= 100:
            return False, W[6]
        if ' ' in case_name:
            return False, W[2]
        if '-' in case_name:
            return False, W[0]
        for word in case_name.split('_'):
            if word[0].islower():
                return False, W[3]
        return True, None

    @staticmethod
    def __is_keyword_recommend(keyword):
        if keyword.isdigit():
            return True, None
        if '.' in keyword and '...' not in keyword:
            keyword = keyword.split('.')[-1]
        if '_' in keyword:
            return False, W[1]
        if '-' in keyword:
            return False, W[0]
        for word in keyword.split():
            if word[0].islower():
                return False, W[3]
        spk = ['comment',
               'run keyword and ignore error'
               ]
        if keyword.lower() in spk:
            return False, W[5]
        return True, None

    def __get_line_num(self, name):
        num = 0
        for index, line_text in enumerate(self.line_list):
            if name in line_text:
                self.content = self.content[self.content.find(name) + len(name):]
                self.line_list = self.content.split('\n')
                num = index + self.start + 1
                self.start = num - 1
                break
        return num

    def __is_self_kw_used(self, self_kw):
        self.content = self.init_content
        self.line_list = self.content.split('\n')
        num = 0
        for kw in self_kw:
            if self.content.count(kw) == 1:
                for index, line_text in enumerate(self.line_list):
                    if kw in line_text:
                        num = index + 1
                self.warnings.append(num)
                ROBOT_WARNINGS.append([kw + ' ' + W[7], num])
