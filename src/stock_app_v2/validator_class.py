from stock_app_v2.dict_macker_class import DictMaker
from typing import Tuple


class Validator:
    def __init__(self, block_name, string_moduls, string_components):

        self.block_name = block_name
        self.string_moduls = string_moduls
        self.string_components = string_components
        self.msg = ''
        self.flag = False

    @staticmethod
    def _check_curly_brackets(string: str) -> str:
        """
        Ensures that the given string starts with an opening curly bracket '{' and ends with a closing curly bracket '}'.

        Parameters:
        string (str): The input string to check and adjust.

        Returns:
        str: The modified string, guaranteed to start with '{' and end with '}'.
        """
        if not string.startswith('{'):
            string = '{' + string
        if not string.endswith('}'):
            string = string + '}'
        return string

    @staticmethod
    def _try_dict(dict_string: str) -> Tuple[str, str, bool]:
        """
        Attempts to convert a string representation of a dictionary into a valid dictionary.

        The function validates the input string, identifies errors, and handles specific conditions:
        1. Combines values for duplicate keys.
        2. Filters out keys or values that are zero.
        3. Handles specific error cases related to the character 'c'.

        Parameters:
        dict_string (str): The input string representing a dictionary. Example: "{1: 2, 3: 4}".

        Returns:
        Tuple[str, str, bool]:
        - A string representation of the processed dictionary.
        - A message string describing errors or issues encountered.
        - A boolean flag indicating whether the dictionary is valid and non-empty.
        """

        msg = ''        # Message to describe any errors encountered

        # Convert input string to a list of key-value pairs
        prepared_list = dict_string.strip()[1:-1].strip().split(',') if dict_string != '{}' else []

        # Prepare list to convert into a dictionary: ensure key-value pair structure
        prepared_list = [tuple(s.split(':')) for s in prepared_list] if prepared_list else []

        # Process the list and handle specific error conditions
        # (k, v) --> (str, str) ==> {k: v} --> {int: float}
        # [(k, v1), (k, v2)] ==> {k: v1+v2}
        error_dict_c, tested_dict, error_dict = DictMaker().make_dicts_of_modul_compo_err(prepared_list)

        if error_dict_c:
            msg += f'Артикулы, содержавшие латинскую букву "с" в начале или конце слова, ' \
                   f'оставлены в текущем словаре: {error_dict_c}\n'

        # if in (k, v) k contains "c", add {k: v} into tested_dict
        tested_dict = {**error_dict_c, **tested_dict}

        # remove k==0 and v==0.0 from tested_dict to error_dict_0
        tested_dict, error_dict_0 = DictMaker().remove_zero_values(tested_dict)

        error_dict = {
            **error_dict,
            **error_dict_0
        }

        # Indicates whether the output dictionary is valid and non-empty
        flag = True if tested_dict else False

        if error_dict:
            msg += f'Cловарь ошибок: {error_dict}. \n'

        return f'{tested_dict}', msg, flag

    def _dict_validation(self):
        """
        Validates the manual input of `self.string_moduls` and `self.string_components`,
        checking whether they can be correctly converted into dictionaries of the format {int: float}.
        :return:
        """

        self.string_moduls = self._check_curly_brackets(self.string_moduls)
        self.string_components = self._check_curly_brackets(self.string_components)

        self.string_moduls, msg_moduls, flag_moduls = self._try_dict(self.string_moduls)
        self.string_components, msg_components, flag_components = self._try_dict(self.string_components)

        self.flag = False if self.string_moduls == self.string_components == '{}' else (flag_moduls or flag_components)

        if not self.flag:
            self.msg += f'\nНе удалось заполнить словари данными.\n'

        if msg_moduls or msg_components:
            self.msg += '\nИНСТРУКЦИЯ:\n' \
                        'Приведите словарь к виду {ЦЕЛОЕ ЧИСЛО: ДРОБНОЕ ЧИСЛО (пример дроб.числа - 1.5)}. \n' \
                        'Число - НЕНУЛЕВОЕ, разделитель дробной части - ТОЧКА, \n' \
                        'разделитель пар артикул:количество - ЗАПЯТАЯ. \n' \
                        'ПРИМЕР (фигурные скобки и пробелы не обязательны): {1111: 1.5, 222: 6} или 1111:1.5,222:6\n'
            self.msg += f'\nОШИБКИ:\n'

        if msg_moduls:
            self.msg += f'    модули -- {msg_moduls}\n'

        if msg_components:
            self.msg += f'    комопоненты -- {msg_components}\n'

    def _block_name_validation(self):
        """
        Ensures `self.block_name` is valid.
        If `self.block_name` is `None` or an empty string,
        it assigns a default or generated name
        :return:
        """
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

    def _validate_input_excel(self) -> Tuple[str, str]:
        """
        Validates input data from an Excel-like table (in string format) with newline-separated rows.
        Determines whether the input has 2 or 3 columns and processes the data into dictionaries:
        - Module dictionary {int: float}
        - Component dictionary {int: float}
        - Error dictionary for invalid entries

        Returns:
        Tuple[str, str]:
        - String representation of the module dictionary
        - String representation of the component dictionary
        """

        # print(f'self.string_moduls: {repr(self.string_moduls)}')        

        # Convert delimiters and characters: ',' to '.' and Russian 'с' to English 'c'
        input_str = self.string_moduls.replace(',', '.').strip('\n').lower().replace('с', 'c')  # rus --> eng
        input_list = input_str.split('\n')

        # If the number of cells doesn't divide evenly into 2 or 3 columns, processing is not possible
        if len(input_list) % 2 and len(input_list) % 3:
            self.msg += 'ОШИБКИ: не удалось определить количество столбцов в исходной таблице.\n'
            return '{}', '{}'

        # Assume 2 columns by default
        even_col_flag = True
        prepared_list = []
        error_dict_even = {}

        # Check if input has an even number of rows for 2-column format
        if len(input_list) % 2:
            even_col_flag = False
        else:

            prepared_list = [(input_list[i], input_list[i + 1]) for i in range(0, len(input_list), 2)]

            if len(input_list) % 3 == 0:
                # Check if it could be a 3-column format
                for t in prepared_list:
                    if '.' in t[0] or 'c' in t[1]:
                        even_col_flag = False
                        break
                # No changes to prepared_list yet; further validation during dict conversion
            else:
                error_dict_even = {
                    **{t[0]: t[1] for t in prepared_list if '.' in t[0]},
                    **{t[1]: '' for t in prepared_list if 'c' in t[1]}
                }
                prepared_list = [
                    t for t in prepared_list
                    if t[0] not in error_dict_even.keys() and t[1] not in error_dict_even.keys()
                ]

        # Process for 3-column format if not 2-column
        error_dict_odd = {}

        if not even_col_flag:

            prepared_list = []

            for i in range(0, len(input_list), 3):

                if input_list[i] != ' ' and input_list[i + 1] != ' ':
                    error_dict_odd[input_list[i]] = 'проверить артикул-количетсво'
                    error_dict_odd[input_list[i + 1]] = 'проверить артикул-количество'

                if input_list[i].strip().replace('c', '').isdigit() and (
                        input_list[i + 1] == ' ' or not input_list[i + 1].strip().replace('c', '').isdigit()
                ):
                    prepared_list.append((input_list[i], input_list[i + 2]))
                    error_dict_odd.pop(input_list[i], None)

                if (
                        input_list[i] == ' ' or not input_list[i].strip().replace('c', '').isdigit()
                ) and input_list[i + 1].strip().replace('c', '').isdigit():
                    prepared_list.append((input_list[i + 1], input_list[i + 2]))
                    error_dict_odd.pop(input_list[i + 1], None)

        # Convert prepared_list into dictionaries
        modul_dict, component_dict, error_dict_mce = DictMaker().make_dicts_of_modul_compo_err(prepared_list)

        # Combine all error dictionaries
        error_dict = {**error_dict_even, **error_dict_odd, **error_dict_mce}

        # Create user-facing error messages
        if error_dict:
            self.msg += '\nИНСТРУКЦИЯ:\n' \
                        'Число столбцов в таблице должно быть 2 или 3.\n' \
                        'При неверном вводе исходной таблицы словарь пар артикул-количество может содержать ошибки.\n' \
                        'Значения в исходной таблице должны быть:\n' \
                        '    артикулы -- целые числа с буквой "С" в начале или конце ' \
                        '(рус. или англ. в любом регистре)\n' \
                        '    количества -- целые или дробные числа (десятичный разделитель - ТОЧКА или ЗАПЯТАЯ).\n' \
                        'Ячейки могут быть пустыми.\n '
            self.msg += f'\nОШИБКИ: {error_dict},\n'

        if len(input_list) % 3 == 0 and len(input_list) % 2 == 0 and not modul_dict:
            self.msg += '\n   !!! Таблица ТОЛЬКО из компонентов в 3 столбца и четное число строк ' \
                        'распознается с ошибками !!!\n' \
                        'В этом случае добавьте лишнюю строку. (сделайте число строк нечетным)\n'

        return f'{modul_dict}', f'{component_dict}'

    def validate(self):
        """
        Validates the input strings for modules and components, ensuring they can be converted into dictionaries,
        and performs additional checks on the block name.

        Returns:
        tuple: A tuple containing:
            - `self.flag` (bool): Indicates whether the validation was successful.
            - `self.msg` (str): A message describing the result of the validation process.
            - `self.block_name` (str): The validated or generated block name.
            - `moduls_dict_str` (str): A string representation of the dictionary created from `self.string_moduls`.
            - `components_dict_str` (str): A string representation of the dictionary created from `self.string_components`.
        """

        # convert an input table (string with '\n') into dictionaries like d={int: float} in str format as f'{d}'
        if self.string_moduls.find('\n') != -1:
            self.string_moduls, self.string_components = self._validate_input_excel()

        # Validates the manual input of `self.string_moduls` and `self.string_components`,
        # checking whether they can be correctly converted
        # into dictionaries of the format {int: float}.
        self._dict_validation()

        # Ensures `self.block_name` is valid.
        # If `self.block_name` is `None` or an empty string,
        # it assigns a default or generated name
        if self.flag:
            self._block_name_validation()

        return self.flag, self.msg, self.block_name, self.string_moduls, self.string_components
