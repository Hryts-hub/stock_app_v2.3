import pytest

from stock_app_v2.validator_class import Validator


# dict_validator_flag, self.msg, block_name, moduls_dict_str, components_dict_str
@pytest.mark.parametrize('block_name, moduls_dict_str, components_dict_str, expected_result',
                         [
                             # 0
                             ('', '{}', '{}', (
                                     False, 'Не удалось заполнить словари данными. \nМодули: {} \nКомпоненты: {}\n',
                                     '', '{}', '{}')),
                             # 1
                             ('', '{', '{}', (
                                     False, 'Не удалось заполнить словари данными. \nМодули: {} \nКомпоненты: {}\n',
                                     '', '{}', '{}')),
                             # 2
                             ('', '}', '{}', (
                                     False, 'Не удалось заполнить словари данными. \nМодули: {} \nКомпоненты: {}\n',
                                     '', '{}', '{}')),
                             # 3
                             ('', '{}', '{', (
                                     False, 'Не удалось заполнить словари данными. \nМодули: {} \nКомпоненты: {}\n',
                                     '', '{}', '{}')),
                             # 4
                             ('', '{}', '}', (
                                     False, 'Не удалось заполнить словари данными. \nМодули: {} \nКомпоненты: {}\n',
                                     '', '{}', '{}')),
                             # 5
                             ('', '', '', (
                                     False,
                                     'Не удалось заполнить словари данными. \nМодули: {} \nКомпоненты: {}\n',
                                     '', '{}', '{}')),
                             # 6
                             ('', '1', '', (
                                     False,
                                     'Не удалось заполнить словари данными. \nМодули: Неправильный словарь '
                                     '\nКомпоненты: {}\n',
                                     '', '{1}', '{}')),
                             # 7
                             ('', '', '2', (
                                     False,
                                      'Не удалось заполнить словари данными. \n'
                                      'Модули: {} \n'
                                      'Компоненты: Неправильный словарь\n',
                                     '', '{}', '{2}')),
                             # 8
                             ('', ':1', '', (
                                     False,
                                     'Не удалось заполнить словари данными. \n'
                                     'Модули: Приведите словарь к виду: {1: 1.5, 2: 6} или 1:1.5,2:6 \n'
                                     'Компоненты: {}\n',
                                     '', '{:1}', '{}')),
                             # 9
                             ('', '', ':2', (
                                     False,
                                     'Не удалось заполнить словари данными. \n'
                                     'Модули: {} \n'
                                     'Компоненты: Приведите словарь к виду: {1: 1.5, 2: 6} или 1:1.5,2:6\n',
                                     '', '{}', '{:2}')),
                             # 10
                             ('', '', 'asdf', (
                                     False,
                                     'Не удалось заполнить словари данными. \n'
                                     'Модули: {} \n'
                                     'Компоненты: Приведите словарь к виду: {1: 1.5, 2: 6} или 1:1.5,2:6\n',
                                     '', '{}', '{asdf}')),
                             # 11
                             ('', 'qwer', '', (
                                     False,
                                    'Не удалось заполнить словари данными. \n'
                                    'Модули: Приведите словарь к виду: {1: 1.5, 2: 6} или 1:1.5,2:6 \n'
                                    'Компоненты: {}\n',
                                     '', '{qwer}', '{}')),
                             # 12
                             ('', '1:5,2:6,7', '', (
                                     False,
                                     'Не удалось заполнить словари данными. \n'
                                     'Модули: Приведите словарь к виду: {1: 1.5, 2: 6} или 1:1.5,2:6 \n'
                                     'Компоненты: {}\n',
                                     '', '{1:5,2:6,7}', '{}')),
                             # 13
                             ('', '', '1:5,2:6,7', (
                                     False,
                                     'Не удалось заполнить словари данными. \n'
                                     'Модули: {} \n'
                                     'Компоненты: Приведите словарь к виду: {1: 1.5, 2: 6} или 1:1.5,2:6\n',
                                     '', '{}', '{1:5,2:6,7}'
                             )),
                             # 14
                             ('', '1:5,2:6.7', '', (
                                     True,
                                     'модули: {1: 5, 2: 6.7},\nкомпоненты: {}\n',
                                     '1_2', '{1: 5, 2: 6.7}', '{}')),
                             # 15
                             ('zz', '1:5,2:6.7', '3:5.5,     4:6.6', (
                                     True,
                                     'модули: {1: 5, 2: 6.7},\nкомпоненты: {3: 5.5, 4: 6.6}\n',
                                     'zz', '{1: 5, 2: 6.7}', '{3: 5.5, 4: 6.6}')),
                             # 16
                             ('fld-nano', '\n \nC1529\n1\n \nC1495\n1\n \n \n2\n2005\n \n1\n741\n \n1\n', '', (
                                     True,
                                     ("ОШИБКИ: {'': '2'},\n" +
                                      'модули: {1529: 1.0, 1495: 1.0},\nкомпоненты: {2005: 1.0, 741: 1.0}\n'),
                                     'fld-nano', '{1529: 1.0, 1495: 1.0}', '{2005: 1.0, 741: 1.0}')),
                             # 17
                             ('zz', '\n \nc986\n1\n \nc987\n1\n', '', (
                                     True,
                                     'модули: {986: 1.0, 987: 1.0},\nкомпоненты: {}\n',
                                     'zz',
                                     '{986: 1.0, 987: 1.0}',
                                     '{}')),
                             # 18
                             ('pca',
                              '\nс857\n1\nс858\n1\nс859\n1\nc1007\n1\nс306\n1\nс861\n1\nc908\n2\n*c925\n1\nс973\n1\n3130\n1\n210\n4\n186\n10\nc926\n1\nc1159\n1\nc909\n1\nс560\n2\nс860\n1\nc308\n1\nc607\n0,5\nc924\n1\nc995\n1\nc581\n1\nc585\n1\nс220\n2\nс42\n2\nс43\n2\nc\n1\n**\n1\nс808\n1\n95\n1\n142\n1\nc735\n2\n2385\n2\nс1036\n1\n',
                              '', (
                                      True,
                                      ("ОШИБКИ: {'*c925': '1', 'c': '1', '**': '1'},\n" +
                                       'модули: {857: 1.0, 858: 1.0, 859: 1.0, 1007: 1.0, 306: 1.0, 861: 1.0, 908: '
                                       '2.0, 973: 1.0, 926: 1.0, 1159: 1.0, 909: 1.0, 560: 2.0, 860: 1.0, 308: 1.0, '
                                       '607: 0.5, 924: 1.0, 995: 1.0, 581: 1.0, 585: 1.0, 220: 2.0, 42: 2.0, 43: '
                                       '2.0, 808: 1.0, 735: 2.0, 1036: 1.0},\nкомпоненты: {3130: 1.0, 210: 4.0, 186: 10.0, 95: 1.0, 142: 1.0, 2385: 2.0}\n'),
                                      'pca',
                                      '{857: 1.0, 858: 1.0, 859: 1.0, 1007: 1.0, 306: 1.0, 861: 1.0, 908: '
                                      '2.0, 973: 1.0, 926: 1.0, 1159: 1.0, 909: 1.0, 560: 2.0, 860: 1.0, 308: 1.0, '
                                      '607: 0.5, 924: 1.0, 995: 1.0, 581: 1.0, 585: 1.0, 220: 2.0, 42: 2.0, 43: '
                                      '2.0, 808: 1.0, 735: 2.0, 1036: 1.0}',
                                      '{3130: 1.0, 210: 4.0, 186: 10.0, 95: 1.0, 142: 1.0, 2385: 2.0}')),
                             # 19
                             ('QBU-10kV-NR  STD 1.0 (27.04.2023)',
                              '\nc728\n1\nc1488\n2\nc727\n1\n413c\n32\nс1185\n1\n97c\n0,5\n96c\n1\n', '{}', (
                                      True,
                                      'модули: {728: 1.0, 1488: 2.0, 727: 1.0, 413: 32.0, 1185: 1.0, 97: 0.5, 96: '
                                      '1.0},\n'
                                      'компоненты: {}\n',
                                      'QBU-10kV-NR  STD 1.0 (27.04.2023)',
                                      '{728: 1.0, 1488: 2.0, 727: 1.0, 413: 32.0, 1185: 1.0, 97: 0.5, 96: 1.0}', '{}')),
                             # 20
                             ('QBU-10kV-NR  STD 1.0 (27.04.2023)',
                              '\nc728 \n1 \nc1488 \n2 \nc727 \n1 \n413c \n32 \nс1185 \n1 \n97c \n0,5 \n96c \n1 \n',
                              '{}', (
                                      True,
                                      'модули: {728: 1.0, 1488: 2.0, 727: 1.0, 413: 32.0, 1185: 1.0, 97: 0.5, 96: '
                                      '1.0},\n'
                                      'компоненты: {}\n',
                                      'QBU-10kV-NR  STD 1.0 (27.04.2023)',
                                      '{728: 1.0, 1488: 2.0, 727: 1.0, 413: 32.0, 1185: 1.0, 97: 0.5, 96: 1.0}',
                                      '{}')),
                         ]
                         )
def test_data_reader_2(block_name, moduls_dict_str, components_dict_str, expected_result):
    res = Validator(block_name, moduls_dict_str, components_dict_str).validate()
    assert res == expected_result
