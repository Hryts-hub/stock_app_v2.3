import pytest

from stock_app_v2.validator_class import Validator

@pytest.mark.parametrize('test_string, test_name, expected_result',
                         [
                             ('{}', '', (False, 'Пустой словарь', '')),
                             ('{', '', (False, 'Пустой словарь', '')),
                             ('', '', (False, 'Пустой словарь', '')),
                             ('}', '', (False, 'Пустой словарь', '')),
                             ('1', '', (False, 'Неправильный словарь', '')),
                             ('1:1', '', (True, '{1: 1}', '1')),
                             ('zzz', '', (False, 'Приведите словарь к виду: {1: 1.5, 2: 6} или 1:1.5,2:6', '')),
                             ('1:5,2:6,7', '', (False, 'Приведите словарь к виду: {1: 1.5, 2: 6} или 1:1.5,2:6', '')),
                             ('1:5,2:6.7', '', (True, '{1: 5, 2: 6.7}', '1_2')),
                             ('1:5,2:6.7', '    ', (True, '{1: 5, 2: 6.7}', '1_2')),
                             ('1:5,2:6.7', 'zz', (True, '{1: 5, 2: 6.7}', 'zz')),
                         ]
                         )
def test_data_reader_2(test_string, test_name, expected_result):
    res = Validator(test_string, test_name).validate()
    assert res == expected_result

# @pytest.mark.parametrize('test_string, expected_result',
#                          [
#                              ('{}', (False, 'Пустой словарь')),
#                              ('{', (False, 'Пустой словарь')),
#                              ('', (False, 'Пустой словарь')),
#                              ('}', (False, 'Пустой словарь')),
#                              ('1', (False, 'Неправильный словарь')),
#                              ('1:1', (True, '{1: 1}')),
#                              ('zzz', (False, 'Приведите словарь к виду: {1: 1.5, 2: 6} или 1:1.5,2:6')),
#                              ('1:5,2:6,7', (False, 'Приведите словарь к виду: {1: 1.5, 2: 6} или 1:1.5,2:6')),
#                              ('1:5,2:6.7', (True, '{1: 5, 2: 6.7}')),
#                          ]
#                          )
# def test_data_reader_2(test_string, expected_result):
#     res = Validator(test_string).moduls_dict_validation()
#     assert res == expected_result

#
# class Validator:
#     def __init__(self, string_moduls_dict):
#         self.string_moduls_dict = string_moduls_dict
#         self.msg = ''
#         self.color = 'red'
#         self.flag = False
#
#     def moduls_dict_validation(self):
#         # string_moduls_dict = self.textbox2.toPlainText()
#         #         print(string_moduls_dict.startswith('{'))
#         if not self.string_moduls_dict.startswith('{'):
#             self.string_moduls_dict = '{' + self.string_moduls_dict
#         #         print(string_moduls_dict.startswith('{'))
#         if not self.string_moduls_dict.endswith('}'):
#             self.string_moduls_dict = self.string_moduls_dict + '}'
#
#         try:
#             moduls_dict = eval(self.string_moduls_dict)
#             if (isinstance(moduls_dict, dict)
#                     and all(isinstance(k, int)
#                             and (isinstance(v, int) or isinstance(v, float)) for k, v in moduls_dict.items())):
#                 if moduls_dict != {}:
#                     self.msg = f'{moduls_dict}'
#                     self.flag = True
#                     # return moduls_dict  # True,
#                 else:
#                     self.msg = 'Пустой словарь'
#         except:
#             self.msg = 'Приведите словарь к виду: {1: 5, 2: 6} или 1:5,2:6'
#
#         return self.flag, self.msg, self.color
