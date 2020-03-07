# -*- coding: utf-8 -*-


class RobotContentProcess(object):
    def __init__(self, content=''):
        super(RobotContentProcess, self).__init__()
        self.line_list = content.split('\n')
        self.__names_set = []  # only get method
        self.__names_var = []
        self.__names_case = []
        self.__names_kw = []
        self.__self_kw = []
        self.__s_out = []
        self.__v_out = []
        self.__t_out = []
        self.__k_out = []
        self.bs = ' '
        self.s = '*** Settings ***'
        self.v = '*** Variables ***'
        self.t = '*** Test Cases ***'
        self.k = '*** Keywords ***'
        self.up_down = [
            'Suite Setup',
            'Suite Teardown',
            'Test Setup',
            'Test Teardown',
            '[Setup]',
            '[Teardown]'
        ]

    @property
    def names_set(self):
        return self.__names_set

    @property
    def names_var(self):
        return self.__names_var

    @property
    def names_case(self):
        return self.__names_case

    @property
    def names_kw(self):
        return self.__names_kw

    @property
    def self_kw(self):
        return self.__self_kw

    @property
    def s_out(self):
        return self.__s_out

    @property
    def v_out(self):
        return self.__v_out

    @property
    def t_out(self):
        return self.__t_out

    @property
    def k_out(self):
        return self.__k_out

    def run(self):
        L = [self.s.lower(), self.v.lower(), self.t.lower(), self.k.lower()]
        cur_index = 0
        for line_text in self.line_list:
            if line_text.strip().lower() in L:
                cur_index = L.index(line_text.strip().lower())
                continue

                # Settings
            if cur_index == 0:
                text_list = self.__get_text_list(line_text)
                if text_list:
                    self.__s_out.append(text_list)
                    self.__names_set.append(text_list[0])
                    if text_list[0].title() in self.up_down:
                        words = self.__get_keywords(text_list[1:])
                        self.__names_kw.extend(words)

                # Variables
            if cur_index == 1:
                text_list = self.__get_text_list(line_text)
                if text_list:
                    self.__v_out.append(text_list)
                    if text_list[0] != '...':
                        self.__names_var.append(text_list[0])

                # Test Cases
            if cur_index == 2:
                if self.__is_case_name(line_text):
                    self.__names_case.append(line_text.strip())
                    self.__t_out.append([line_text.strip(), True])
                    continue
                text_list = self.__get_text_list(line_text)
                if text_list:
                    self.__t_out.append(text_list)
                    if text_list[0].title() in self.up_down or text_list[0][0] != '[':
                        self.__names_kw.extend(self.__get_keywords(text_list))
                # Keywords
            if cur_index == 3:
                if len(line_text) > 0 and not line_text.startswith(self.bs):
                    self.__names_kw.append(line_text.strip())
                    self.__self_kw.append(line_text.strip())
                    self.__k_out.append([line_text.strip(), True])
                    continue
                text_list = self.__get_text_list(line_text)
                if text_list:
                    self.__k_out.append(text_list)
                    self.__names_kw.extend(self.__get_keywords(text_list))

    def __get_text_list(self, line_text):
        text_list = line_text.split(self.bs * 2)
        text_list = self.__remove_blank_spaces(text_list)
        return text_list

    @staticmethod
    def __remove_blank_spaces(text_list):
        new_text_list = []
        for item in text_list:
            if item:
                new_text_list.append(item.strip())
        return new_text_list if new_text_list else None

    def __is_case_name(self, line_text):
        if len(line_text) > 0 and not line_text.startswith(self.bs):
            return True
        return False

    @staticmethod
    def __is_keyword(item):
        if item[0].isdigit():
            return False
        if item in ['_', ';', '.', '\\', '\n', '...']:
            return False
        for char in ['=', '$', '@', '&', ':', '[', ']', '\\', '|']:
            if char in item:
                return False
        return True

    def __get_keywords(self, text_list):
        return [item for item in text_list if self.__is_keyword(item)]
