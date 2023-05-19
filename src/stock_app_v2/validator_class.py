class Validator:
    def __init__(self, block_name, string_moduls, string_components):

        self.block_name = block_name
        self.string_moduls = string_moduls
        self.string_components = string_components
        self.msg = ''
        self.color = 'red'
        self.flag = False

    @staticmethod
    def _check_curly_brackets(string):
        print('Hi from _check_curly_brackets')
        if not string.startswith('{'):
            string = '{' + string
        if not string.endswith('}'):
            string = string + '}'
        print(string)
        return string

    @staticmethod
    def _try_dict(dict_string):
        print(f'Hi from _try_dict: {dict_string}')
        result_string = dict_string
        # msg = ''
        flag = False
        try:
            try_dict = eval(dict_string)
            if (isinstance(try_dict, dict)
                    and all(isinstance(k, int)
                            and (isinstance(v, int) or isinstance(v, float)) for k, v in try_dict.items())):
                # if try_dict != {}:
                #     flag = True
                # else:
                #     msg = 'Пустой словарь'
                flag = True
                result_string = f'{try_dict}'
                msg = result_string
            else:
                msg = 'Неправильный словарь'
        except:
            msg = 'Приведите словарь к виду: {1: 1.5, 2: 6} или 1:1.5,2:6'

        return result_string, msg, flag

    def _dict_validation(self):
        print('Hi from _dict_validation')
        # if not self.string_moduls_dict.startswith('{'):
        #     self.string_moduls_dict = '{' + self.string_moduls_dict
        # if not self.string_moduls_dict.endswith('}'):
        #     self.string_moduls_dict = self.string_moduls_dict + '}'
        self.string_moduls = self._check_curly_brackets(self.string_moduls)
        self.string_components = self._check_curly_brackets(self.string_components)

        moduls_dict_str, msg_moduls, flag_moduls = self._try_dict(self.string_moduls)
        components_dict_str, msg_components, flag_components = self._try_dict(self.string_components)

        self.flag = False if moduls_dict_str == components_dict_str == '{}' else (flag_moduls and flag_components)
        self.msg += f'модули: {msg_moduls},\nкомпоненты: {msg_components}'

        # try:
        #     moduls_dict = eval(self.string_moduls_dict)
        #     if (isinstance(moduls_dict, dict)
        #             and all(isinstance(k, int)
        #                     and (isinstance(v, int) or isinstance(v, float)) for k, v in moduls_dict.items())):
        #         if moduls_dict != {}:
        #             self.msg = f'{moduls_dict}'
        #             self.flag = True
        #             # return moduls_dict  # True,
        #         else:
        #             self.msg = 'Пустой словарь'
        #     else:
        #         self.msg = 'Неправильный словарь'
        # except:
        #     self.msg = 'Приведите словарь к виду: {1: 1.5, 2: 6} или 1:1.5,2:6'
        return moduls_dict_str, components_dict_str

    def _block_name_validation(self):
        print('Hi from _block_name_validation')
        if self.block_name is None \
                or self.block_name == ''\
                or self.block_name.isspace():
            #             moduls_dict = eval(self.textbox2.displayText())
            moduls_dict = eval(self.string_moduls)
            self.block_name = [str(k) for k, v in moduls_dict.items()]
            self.block_name = '_'.join(self.block_name)
        #     self.textbox1.setText(name_str)
        # else:
        #     self.textbox1.setText(self.msg)
        # self.color = 'green'
        # self.msg = f'Добавлено в список блоков для отчета: {self.textbox1.displayText()} -- {self.textbox3.value()} шт.'

    def _validate_input(self):
        modul_dict = {}
        e_componennt_dict = {}
        error_dict = {}

        print(self.string_moduls)
        print(repr(self.string_moduls))

        # raw_strig_from_doc = repr(self.string_moduls)
        # print(raw_strig_from_doc)

        raw_strig_from_doc = self.string_moduls.replace(',', '.')
        raw_list = raw_strig_from_doc.split('\n')
        print(raw_list)

        for modul_str in raw_list:

            modul_str_list = modul_str.split('\t')
            modul_str_list = [s.strip() for s in modul_str_list if s != '']

            print(modul_str_list)
            if modul_str_list[0].lower().startswith('c') or modul_str_list[0].lower().startswith('с'):
                art = modul_str_list[0][1:].strip()
                print(art)
                try:
                    modul_dict[int(art)] = float(modul_str_list[1])
                except Exception as e:
                    print(f'ошибка с буквой с: {e}')
                    error_dict[modul_str] = e
            elif modul_str_list[0].isdigit():
                art = modul_str_list[0]
                print('--', art)
                try:
                    e_componennt_dict[int(art)] = float(modul_str_list[1])
                except Exception as e:
                    print(f'ошибка с буквой с: {e}')
                    error_dict[modul_str] = e
            elif modul_str_list[0].find('+') != -1:
                arts = modul_str_list[0].split('+')
                for art in arts:
                    try:
                        e_componennt_dict[int(art)] = float(modul_str_list[1])
                    except Exception as e:
                        print(f'ошибка с буквой с: {e}')
                        error_dict[modul_str] = e
            else:
                print('---', modul_str)
                error_dict[modul_str] = modul_str

            self.msg = f'ОШИБКИ: {error_dict},\n'
        return f'{modul_dict}', f'{e_componennt_dict}'


    def validate(self):
        print('Hi from validate')
        if self.string_moduls.find('\t') != -1:
            self.string_moduls, self.string_components = self._validate_input()

        moduls_dict_str, components_dict_str = self._dict_validation()
        if self.flag:
            self._block_name_validation()  # creates name, if name is None or ''
            # self.block_list_dict[self.textbox1.displayText()] = [
            #     eval(self.textbox2.toPlainText()),
            #     self.textbox3.value()]
            # self._refresh_comboBox_list()
        #     self.color = 'green'
        # else:
        #     self.color = 'red'
        print(f'validated {self.msg}')
        print(self.block_name, moduls_dict_str, components_dict_str)
        return self.flag, self.msg, self.block_name, moduls_dict_str, components_dict_str
