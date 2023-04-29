class Validator:
    def __init__(self, string_moduls_dict, block_name):
        self.string_moduls_dict = string_moduls_dict
        self.block_name = block_name
        self.msg = ''
        self.color = 'red'
        self.flag = False

    def _moduls_dict_validation(self):
        # string_moduls_dict = self.textbox2.toPlainText()
        #         print(string_moduls_dict.startswith('{'))
        if not self.string_moduls_dict.startswith('{'):
            self.string_moduls_dict = '{' + self.string_moduls_dict
        #         print(string_moduls_dict.startswith('{'))
        if not self.string_moduls_dict.endswith('}'):
            self.string_moduls_dict = self.string_moduls_dict + '}'

        try:
            moduls_dict = eval(self.string_moduls_dict)
            if (isinstance(moduls_dict, dict)
                    and all(isinstance(k, int)
                            and (isinstance(v, int) or isinstance(v, float)) for k, v in moduls_dict.items())):
                if moduls_dict != {}:
                    self.msg = f'{moduls_dict}'
                    self.flag = True
                    # return moduls_dict  # True,
                else:
                    self.msg = 'Пустой словарь'
            else:
                self.msg = 'Неправильный словарь'
        except:
            self.msg = 'Приведите словарь к виду: {1: 1.5, 2: 6} или 1:1.5,2:6'

        # return self.flag, self.msg

    def _block_name_validation(self):
        if self.block_name is None \
                or self.block_name == ''\
                or self.block_name.isspace():
            #             moduls_dict = eval(self.textbox2.displayText())
            moduls_dict = eval(self.string_moduls_dict)
            self.block_name = [str(k) for k, v in moduls_dict.items()]
            self.block_name = '_'.join(self.block_name)
        #     self.textbox1.setText(name_str)
        # else:
        #     self.textbox1.setText(self.msg)
        # self.color = 'green'
        # self.msg = f'Добавлено в список блоков для отчета: {self.textbox1.displayText()} -- {self.textbox3.value()} шт.'

    def validate(self):
        self._moduls_dict_validation()
        if self.flag:
            self._block_name_validation()  # creates name, if name is None or ''
            # self.block_list_dict[self.textbox1.displayText()] = [
            #     eval(self.textbox2.toPlainText()),
            #     self.textbox3.value()]
            # self._refresh_comboBox_list()
        #     self.color = 'green'
        # else:
        #     self.color = 'red'
        return self.flag, self.msg, self.block_name
