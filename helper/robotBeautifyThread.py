# -*- coding: utf-8 -*-
from PyQt5.QtCore import QThread, pyqtSignal
from .robotContentProcess import RobotContentProcess
import re


class RobotBeautifyThread(QThread):
    done = pyqtSignal(str)

    def __init__(self, content):
        super(RobotBeautifyThread, self).__init__()
        self.conPro = RobotContentProcess(content)

    def run(self):
        try:
            self.conPro.run()
            names_set = self.conPro.names_set
            names_var = self.conPro.names_var
            names_case = self.conPro.names_case
            names_kw = self.conPro.names_kw

            s_out = self.conPro.s_out
            v_out = self.conPro.v_out
            t_out = self.conPro.t_out
            k_out = self.conPro.k_out
            s = self.conPro.s
            v = self.conPro.v
            t = self.conPro.t
            k = self.conPro.k
            s_max_length = max([len(s) for s in names_set], default=0)
            v_max_length = max([len(v) for v in names_var], default=0)
            self.bs = ' '

            # format blank space and alignment
            content_s = self.__format_s_or_v(s_out, s_max_length)
            content_v = self.__format_s_or_v(v_out, v_max_length)
            content_t = self.__format_t_or_k(t_out)
            content_k = self.__format_t_or_k(k_out)

            content_all = ''
            if content_s:
                content_all += s + '\n' + content_s + '\n'
            if content_v:
                content_all += v + '\n' + content_v + '\n'
            if content_t:
                content_all += t + '\n' + content_t + '\n'
            if content_k:
                content_all += k + '\n' + content_k + '\n'

            var_upper = [v.upper().replace(' ', '_').replace('-', '_')
                         for v in names_var]
            content_all = self.__format_suite_var(names_var, content_all)
            content_all = self.__format_other_var(var_upper, content_all)
            content_all = self.__format_case_name(names_case, content_all)
            content_all = self.__format_keywords(names_kw, content_all)

            self.done.emit(content_all)

        except Exception as e:
            print('e:', e)
            with open('../log.txt', 'a+') as f:
                f.write(str(e) + '\n')
        else:
            pass

    def __format_s_or_v(self, content_list, max_length):
        if not content_list:
            return None
        content = ''
        for line in content_list:
            for index, item in enumerate(line):
                if index == 0:
                    content += item
                elif index == 1:
                    content = content + self.bs * \
                              (max_length + 4 - len(line[0])) + item
                else:
                    content = content + self.bs * 4 + item
            content += '\n'
        return content

    def __format_t_or_k(self, content_list):
        if not content_list:
            return None
        content = ''
        name_num = 0
        for line in content_list:
            if line[-1] is True:  # case name or keyword name
                name_num += 1
                # if name_num is big than 1, insert a '\n' before this line
                if name_num > 1:
                    content += '\n' + line[0]
                else:
                    content += line[0]
            else:
                for item in line:
                    content = content + self.bs * 4 + item
            content += '\n'
        return content

    @staticmethod
    def __format_suite_var(suite_v, content):
        for v in suite_v:
            content = content.replace(
                v, v.upper().replace(' ', '_').replace('-', '_'))
        return content

    @staticmethod
    def __format_other_var(var_upper, content):
        all_var = re.findall(r'[\$@&]\{[a-zA-Z0-9_-]*\}', content)
        for var in all_var:
            if var not in var_upper:
                content = content.replace(var, var.replace('-', '_').lower())
        return content

    @staticmethod
    def __format_case_name(names, content):
        for name in names:
            s = name.replace('-', '_').replace(' ', '_')
            s = '_'.join([w[0].upper() + w[1:] for w in s.split('_')])
            content = content.replace(name, s)
        return content

    @staticmethod
    def __format_keywords(keywords, content):
        for kw in keywords:
            if '.' in kw:
                kw = kw.split('.')[-1]
            words = kw.replace('_', ' ').replace('-', ' ').split()
            res = ' '.join([w[0].upper() + w[1:] for w in words])
            content = content.replace(kw, res)
        return content
