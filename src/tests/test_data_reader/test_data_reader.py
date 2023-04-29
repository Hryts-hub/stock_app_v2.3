import pytest
import os

import pandas as pd

from stock_app_v2.data_reader_class import DataReader

# from stock_app_v2.stock_app import FILE_OF_PRODUCTS, COLUMN_PRODUCT_NAMES

# TEST_PATH = 'test_data_reader/data_test.csv'
TEST_FILE_OF_PRODUCTS = 'data_test.csv'
# TEST_PATH = f'D:/OEMTECH/Projects/stock_app_v2/src/tests/test_data_reader/{TEST_FILE_OF_PRODUCTS}'
TEST_PATH = f'../tests/test_data_reader/'  # {TEST_FILE_OF_PRODUCTS}'
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

@pytest.mark.parametrize('path, file_name, column_name, expected_result',
                         [
                             ('sdfsdf', 'file_name', 'cncncn', (
                                     None, f'Путь sdfsdf не найден.', 'red')),
                             (None, 'file_name', None, (
                                     None, f'Путь None не найден.', 'red')),
                             ('1/', 'file_name', '1', (
                                     None, 'Путь 1/ не найден.', 'red')),
                             (TEST_PATH, 'file_name', TEST_COLUMN_1, (
                                     None, "Файл file_name по пути ../tests/test_data_reader/ не найден.", 'red')),
                             (TEST_PATH, TEST_FILE_OF_PRODUCTS, 1, (
                                     None, "ОШИБКА <class 'KeyError'>: 1", 'red')),
                             (TEST_PATH, TEST_FILE_OF_PRODUCTS, '', (
                                     None, "ОШИБКА <class 'KeyError'>: ''", 'red')),
                             (TEST_PATH, TEST_FILE_OF_PRODUCTS, None, (
                                     None, "ОШИБКА <class 'KeyError'>: None", 'red')),
                             ('', 'file_name', '', (
                                     None, 'Путь  не найден.', 'red')),
                         ]
                         )
def test_data_reader_1(create_test_csv_file, path, file_name, column_name, expected_result):
    res = DataReader(path, file_name).read_csv_file(column_name)
    assert res == expected_result


@pytest.mark.parametrize('path, file_name, column_name, expected_result',
                         [
                             (TEST_PATH, TEST_FILE_OF_PRODUCTS, TEST_COLUMN_1, (
                                     pd.DataFrame(TEST_DF_1), '', 'blue')),
                         ]
                         )
def test_data_reader_2(create_test_csv_file, path, file_name, column_name, expected_result):
    res = DataReader(path, file_name).read_csv_file(column_name)
    # assert res[0] == expected_result[0] --> table of answers -->ERROR--
    # res[0] is expected_result[0] --> FALSE!!!
    assert res[0].equals(expected_result[0])
    assert res[1] == expected_result[1]
    assert res[2] == expected_result[2]


@pytest.mark.parametrize('path, file_name, df, expected_result',
                         [
                             (TEST_PATH, TEST_FILE_OF_PRODUCTS, TEST_DF_1, (
                                     'Файл data_test.csv создан! Запись добавлена!', 'blue')),
                             (TEST_PATH, TEST_FILE_OF_PRODUCTS, TEST_DF_3, (
                                     'Файл data_test.csv создан! Запись добавлена!', 'blue')),
                         ]
                         )
def test_add_to_file_csv_1(path, file_name, df, expected_result):
    if os.path.exists(f'{path}{file_name}'):
        os.remove(f'{path}{file_name}')
    res = DataReader(path, file_name).add_to_file_csv(df)
    assert res == expected_result


@pytest.mark.parametrize('path, file_name, df, expected_result',
                         [
                             (TEST_PATH, TEST_FILE_OF_PRODUCTS, TEST_DF_1, (
                                     'Запись добавлена в файл data_test.csv !', 'blue')),
                             (TEST_PATH, TEST_FILE_OF_PRODUCTS, TEST_DF_3, (
                                     'Запись добавлена в файл data_test.csv !', 'blue')),
                         ]
                         )
def test_add_to_file_csv_2(path, file_name, df, expected_result):
    if os.path.exists(f'{path}{file_name}'):
        os.remove(f'{path}{file_name}')
    DataReader(path, file_name).add_to_file_csv(TEST_DF_2)
    res = DataReader(path, file_name).add_to_file_csv(df)
    assert res == expected_result