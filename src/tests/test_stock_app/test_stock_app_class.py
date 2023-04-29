import sys

import pytest
import os

import pandas as pd
from PyQt5.QtWidgets import QApplication

from stock_app_v2.stock_app import MyApp
from stock_app_v2.data_reader_class import DataReader

# from stock_app_v2.stock_app import FILE_OF_PRODUCTS, COLUMN_PRODUCT_NAMES

# TEST_PATH = 'test_data_reader/data_test.csv'
TEST_FILE_OF_PRODUCTS = 'data_test.csv'
# TEST_PATH = f'D:/OEMTECH/Projects/stock_app_v2/src/tests/test_data_reader/{TEST_FILE_OF_PRODUCTS}'
TEST_PATH = f'../tests/test_stock_app/'  # {TEST_FILE_OF_PRODUCTS}'
# TEST_PATH = TEST_FILE_OF_PRODUCTS
TEST_COLUMN_1 = 'наименование блока'
TEST_COLUMN_2 = 'словарь модулей'

TEST_DF_1 = pd.DataFrame({
    'наименование блока': ['тест_блок'],
    'словарь модулей': ['{2: 2, 55:1, 44: 8, 954: 1}'],
})
TEST_DF_2 = pd.DataFrame({
    'наименование блока': ['тест_блок'],
    'словарь модулей': ['{22: 2, 255: 1, 244: 8, 2954: 1}'],
})
TEST_DF_3 = pd.DataFrame({
    'наименование блока': ['тест_блок_2'],
    'словарь модулей': ['{12: 2, 112: 3, 155: 1, 144: 8, 1954: 1}'],
})

TEST_DF_4 = pd.DataFrame({
    'наименование блока': ['тест_блок', 'тест_блок_2'],
    'словарь модулей': ['{22: 2, 255: 1, 244: 8, 2954: 1}','{12: 2, 112: 3, 155: 1, 144: 8, 1954: 1}'],
})
# def test_1():
#     app = QApplication([])
#     ex = MyApp()
#     res_1 = ex.color
#     res_2 = ex.block_list_dict
#     assert res_1 == 'blue'
#     assert res_2 == {}
#
# def test_2():
#     app = QApplication([])
#     ex = MyApp()
#     ex.update_info_label
#     res_1 = ex.color
#     assert res_1 == 'blue'

@pytest.mark.parametrize('path, file_name, column_name, expected_result',
                         [
                             (TEST_PATH, TEST_FILE_OF_PRODUCTS, TEST_COLUMN_1, (
                                     'blue')),
                             ('TEST_PATH', TEST_FILE_OF_PRODUCTS, TEST_COLUMN_1, (
                                     'red')),
                         ]
                         )
def test_file_csv_reading(create_test_csv_file_fin, path, file_name, column_name, expected_result):
    app = QApplication([])
    ex = MyApp(path, file_name, column_name)
    # ex.set_data_msg_color(path, file_name, column_name)
    # ex.update_info_label
    res_1 = ex.color
    assert res_1 == expected_result

@pytest.mark.parametrize('path, file_name, column_name, idx, expected_result',
                         [
                             (TEST_PATH, TEST_FILE_OF_PRODUCTS, TEST_COLUMN_1, 0, (
                                     'Поиск обновлен', 'blue')),
                             (TEST_PATH, TEST_FILE_OF_PRODUCTS, TEST_COLUMN_1, 1, (
                                     'Количество найденных результатов: 2', 'green')),
                             (TEST_PATH, TEST_FILE_OF_PRODUCTS, TEST_COLUMN_1, 2, (
                                     'Количество найденных результатов: 1', 'green')),
                             ('TEST_PATHdddd', TEST_FILE_OF_PRODUCTS, TEST_COLUMN_1, 0, (
                                     'Файл не найден или пуст', 'red')),
                         ]
                         )
def test_file_csv_reading_2(create_test_csv_file_fin, path, file_name, column_name, idx, expected_result):
    app = QApplication([])
    ex = MyApp(path, file_name, column_name)
    # ex.set_data_msg_color(path, file_name, column_name)
    # ex.update_info_label()
    ex.comboBox.setCurrentIndex(idx)
    ex.update_info_label()
    res = ex.msg, ex.color
    assert res == expected_result


@pytest.mark.parametrize('path, file_name, column_name, text, expected_result',
                         [
                             (TEST_PATH, TEST_FILE_OF_PRODUCTS, TEST_COLUMN_1, 'zz', (
                                     'Выбранная строка не найдена', 'red')),
                             (TEST_PATH, TEST_FILE_OF_PRODUCTS, TEST_COLUMN_1, 'Обновить поиск', (
                                     'Поиск обновлен', 'blue')),
                             (TEST_PATH, TEST_FILE_OF_PRODUCTS, TEST_COLUMN_1, 'тест', (
                                     'Количество найденных результатов: 2', 'green')),
                             (TEST_PATH, TEST_FILE_OF_PRODUCTS, TEST_COLUMN_1, 'тест_блок_2', (
                                     'Количество найденных результатов: 1', 'green')),
                         ]
                         )
def test_file_csv_reading_2(create_test_csv_file_fin, path, file_name, column_name, text, expected_result):
    app = QApplication([])
    ex = MyApp(path, file_name, column_name)
    # if new string in input it automatically adds to the comboBox with text and index after ENTER
    # here we should add new item manually to pass test
    if text != 'Обновить поиск':
        ex.comboBox.addItems([text])
        ex.comboBox.setCurrentIndex(ex.comboBox.count()-1)
    ex.update_info_label()
    res = ex.msg, ex.color
    assert res == expected_result

