from stock_app_v2.dict_macker_class import DictMaker


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
        if not string.startswith('{'):
            string = '{' + string
        if not string.endswith('}'):
            string = string + '}'
        return string

    @staticmethod
    def _try_dict(dict_string):
        result_string = dict_string
        flag = False
        try:
            try_dict = eval(dict_string)
            if (isinstance(try_dict, dict)
                    and all(isinstance(k, int)
                            and (isinstance(v, int) or isinstance(v, float)) for k, v in try_dict.items())):
                flag = True
                result_string = f'{try_dict}'
                msg = result_string
            else:
                msg = 'Неправильный словарь'
        except:
            msg = 'Приведите словарь к виду: {1: 1.5, 2: 6} или 1:1.5,2:6'

        return result_string, msg, flag

    def _dict_validation(self):
        self.string_moduls = self._check_curly_brackets(self.string_moduls)
        self.string_components = self._check_curly_brackets(self.string_components)

        moduls_dict_str, msg_moduls, flag_moduls = self._try_dict(self.string_moduls)
        components_dict_str, msg_components, flag_components = self._try_dict(self.string_components)

        if flag_moduls:
            moduls_dict, error_modul_dict = DictMaker().remove_zero_values(moduls_dict_str)
            moduls_dict_str = str(moduls_dict)
        else:
            error_modul_dict = {}

        if flag_components:
            components_dict, error_component_dict = DictMaker().remove_zero_values(components_dict_str)
            components_dict_str = str(components_dict)
        else:
            error_component_dict = {}

        self.flag = False if moduls_dict_str == components_dict_str == '{}' else (flag_moduls and flag_components)
        if self.flag:
            self.msg += f'модули: {moduls_dict_str},\nкомпоненты: {components_dict_str}'
        else:
            self.msg += f'Не удалось заполнить словари данными. \nМодули: {msg_moduls} \nКомпоненты: {msg_components}\n'

        if error_modul_dict or error_component_dict:
            self.msg += f'НУЛЕВОЕ КОЛИЧЕСТВО модули: {error_modul_dict}, компоненты {error_component_dict}\n'

        return moduls_dict_str, components_dict_str

    def _block_name_validation(self):
        if self.block_name is None \
                or self.block_name == ''\
                or self.block_name.isspace():
            moduls_dict = eval(self.string_moduls)
            self.block_name = [str(k) for k, v in moduls_dict.items()]
            self.block_name = '_'.join(self.block_name)

    # def _validate_input_txt(self):
    #     modul_dict = {}
    #     component_dict = {}
    #     error_list = []
    #
    #     raw_string_from_doc = self.string_moduls.replace(',', '.')
    #     raw_list = raw_string_from_doc.split('\n')
    #
    #     for modul_str in raw_list:
    #
    #         modul_str_list = modul_str.split('\t')
    #         modul_str_list = [s.strip() for s in modul_str_list if s != '']
    #
    #         if modul_str_list[0].lower().startswith('c') or modul_str_list[0].lower().startswith('с'):
    #             art = modul_str_list[0][1:].strip()
    #             try:
    #                 modul_dict[int(art)] = float(modul_str_list[1])
    #             except Exception as e:
    #                 error_list.append((modul_str, e))
    #         elif modul_str_list[0].isdigit():
    #             art = modul_str_list[0]
    #             try:
    #                 component_dict[int(art)] = float(modul_str_list[1])
    #             except Exception as e:
    #                 error_list.append((modul_str, e))
    #         elif modul_str_list[0].find('+') != -1:
    #             arts = modul_str_list[0].split('+')
    #             for art in arts:
    #                 try:
    #                     component_dict[int(art)] = float(modul_str_list[1])
    #                 except Exception as e:
    #                     error_list.append((modul_str, e))
    #         else:
    #             error_list.append(modul_str)
    #
    #     if error_list:
    #         self.msg = f'ОШИБКИ: {error_list},\n'
    #     return f'{modul_dict}', f'{component_dict}'

    def _validate_input_excel(self):
        even_col_dict = {}
        modul_dict = {}
        component_dict = {}
        error_dict = {}

        input_str = self.string_moduls

        input_str = input_str.replace(',', '.')
        input_str = input_str.strip('\n')
        input_str = input_str.lower()
        input_list = input_str.split('\n')

        for i in range(0, len(input_list) - 1):
            if ((input_list[i].startswith('c') or input_list[i].startswith('с'))
                    and (input_list[i + 1].startswith('c') or input_list[i + 1].startswith('с'))):
                error_dict[input_list[i + 1]] = ''

        for i in range(0, len(input_list) - 1):
            if ((input_list[i].endswith('c') or input_list[i].endswith('с'))
                    and (input_list[i + 1].endswith('c') or input_list[i + 1].endswith('с'))):
                error_dict[input_list[i + 1]] = ''

        input_list = [i for i in input_list if i not in error_dict.keys()]

        even_col_flag = True
        print(len(input_list))

        if len(input_list) % 2:
            even_col_flag = False
        else:
            even_col_dict = dict([(input_list[i], input_list[i + 1]) for i in range(0, len(input_list), 2)])
            for k, v in even_col_dict.items():
                if k.find('.') != -1 or not v.strip().replace('.', '').isdigit() or float(v) > 10:
                    # for QBU-10kV ---- 413c 32  ---- v = 32
                    even_col_flag = False
                    break

        # to take cases with --- float(v) > 10 --- and 2 cols we work through "try"
        try:
            input_dict = even_col_dict if even_col_flag else dict(
                [(input_list[i], input_list[i + 2]) if input_list[i] != ' ' else (input_list[i + 1], input_list[i + 2])
                 for
                 i in range(0, len(input_list), 3)]
            )
        except Exception as e:
            # print(e)
            input_dict = even_col_dict

        for k, v in input_dict.items():
            k = k.strip()
            v = v.strip()
            if (
                    (k.endswith('c') or k.endswith('с'))
                    and k[:-1].strip().isdigit()
                    and v.strip().replace('.', '').isdigit()
            ):
                modul_dict[int(k[:-1])] = float(v)
            elif (
                    (k.startswith('c') or k.startswith('с'))
                    and k[1:].strip().isdigit()
                    and v.strip().replace('.', '').isdigit()
            ):
                modul_dict[int(k[1:])] = float(v)
            elif k.strip().isdigit() and v.strip().replace('.', '').isdigit():
                component_dict[int(k)] = float(v)
            else:
                error_dict[k] = v

        if error_dict:
            self.msg = f'ОШИБКИ: {error_dict},\n'
        return f'{modul_dict}', f'{component_dict}'

    def validate(self):
        # if self.string_moduls.find('\t') != -1:
        #     self.string_moduls, self.string_components = self._validate_input_txt()
        # elif self.string_moduls.find('\n') != -1:
        if self.string_moduls.find('\n') != -1:
            self.string_moduls, self.string_components = self._validate_input_excel()

        moduls_dict_str, components_dict_str = self._dict_validation()
        if self.flag:
            self._block_name_validation()  # creates name, if name is None or ''

        return self.flag, self.msg, self.block_name, moduls_dict_str, components_dict_str
