import pytest
import os

import pandas as pd

from stock_app_v2.data_reader_class import DataReader

from stock_app_v2.stock_app import COLUMN_PRODUCT_NAMES, COLUMN_DICT_OF_MODULS, COLUMN_DICT_OF_COMPONENTS


TEST_FILE_OF_PRODUCTS = 'data_test.csv'
# TEST_PATH = '../tests/test_data_reader/'
TEST_PATH = os.path.dirname(__file__)

# TEST_COLUMN_1 = 'наименование блока'
# TEST_COLUMN_2 = 'словарь модулей'
# TEST_COLUMN_3 = 'словарь эл.компонентов'

TEST_COLUMN_1 = COLUMN_PRODUCT_NAMES
TEST_COLUMN_2 = COLUMN_DICT_OF_MODULS
TEST_COLUMN_3 = COLUMN_DICT_OF_COMPONENTS

TEST_DF_1 = pd.DataFrame({
    TEST_COLUMN_1: ['тест_блок'],
    TEST_COLUMN_2: ['{2: 2, 55:1, 44: 8, 954: 1}'],
    TEST_COLUMN_3: ['{}'],
})
TEST_DF_2 = pd.DataFrame({
    TEST_COLUMN_1: ['тест_блок'],
    TEST_COLUMN_2: ['{22: 2, 255: 1, 244: 8, 2954: 1}'],
    TEST_COLUMN_3: ['{}'],
})
TEST_DF_3 = pd.DataFrame({
    TEST_COLUMN_1: ['тест_блок_2'],
    TEST_COLUMN_2: ['{12: 2, 112: 3, 155: 1, 144: 8, 1954: 1}'],
    TEST_COLUMN_3: ['{}'],
})


def remove_test_file(file_path, file_name):
    if os.path.exists(os.path.join(file_path, file_name)):
        os.remove(os.path.join(file_path, file_name))


@pytest.mark.parametrize('file_path, file_name, expected_result',
                         [
                             # 0
                             ('file_path', 'file_name', (
                                     False, 'Путь file_path не найден!', 'red')),
                             # 1
                             (None, 'file_name', (
                                     False, 'Путь к файлу не задан!', 'red'
                             )),
                             # 2
                             ('', 'file_name', (
                                     False, 'Путь к файлу не задан!', 'red'
                             )),
                             # 3
                             (TEST_PATH, None, (
                                     False, 'Файл не задан!', 'red'
                             )),
                             # 4
                             (TEST_PATH, '', (
                                     False, 'Файл не задан!', 'red'
                             )),
                             # 5
                             (TEST_PATH, 'file_name', (
                                     False, f'Файл file_name по пути {TEST_PATH} не найден!', 'orange'
                             )),
                             # 6
                             (TEST_PATH, TEST_FILE_OF_PRODUCTS, (
                                     True, "", 'blue')),
                         ]
                         )
def test_data_reader_is_file_path_exists(create_test_csv_file, file_path, file_name, expected_result):
    res = DataReader(file_path, file_name).is_file_path_exists()
    assert res == expected_result


@pytest.mark.parametrize('file_path, file_name, column_name, expected_result',
                         [
                             # 0
                             ('file_path', 'file_name', 'cncncn', (
                                     None, f'Путь file_path не найден!', 'red')),
                             # 1
                             (TEST_PATH, TEST_FILE_OF_PRODUCTS, 'cncncn', (
                                     None, "ОШИБКА <class 'KeyError'>: 'cncncn'", 'red'
                             )),
                             # 2
                             (TEST_PATH, TEST_FILE_OF_PRODUCTS, 1, (
                                     None, "ОШИБКА <class 'KeyError'>: 1", 'red')),
                             # 3
                             (TEST_PATH, TEST_FILE_OF_PRODUCTS, '', (
                                     None, "ОШИБКА <class 'KeyError'>: ''", 'red')),
                             # 4
                             (TEST_PATH, TEST_FILE_OF_PRODUCTS, None, (
                                     None, "ОШИБКА <class 'KeyError'>: None", 'red')),
                         ]
                         )
def test_data_reader_read_csv_file_1(create_test_csv_file, file_path, file_name, column_name, expected_result):
    res = DataReader(file_path, file_name).read_csv_file(column_name)
    assert res == expected_result


@pytest.mark.parametrize('file_path, file_name, column_name, expected_result',
                         [
                             (TEST_PATH, TEST_FILE_OF_PRODUCTS, TEST_COLUMN_1, (
                                     pd.DataFrame(TEST_DF_1), '', 'blue')),
                         ]
                         )
def test_data_reader_read_csv_file_2(create_test_csv_file, file_path, file_name, column_name, expected_result):
    res = DataReader(file_path, file_name).read_csv_file(column_name)
    # res[0] --> is a DF --> need to compare DFs --> == is a table of answers --> df1.equals(df2)
    assert res[0].equals(expected_result[0])
    assert res[1] == expected_result[1]
    assert res[2] == expected_result[2]


# data-to-add is already validated. We are checking the first-time-adding and second-time-adding

@pytest.mark.parametrize('file_path, file_name, df, expected_result',
                         [
                             (TEST_PATH, TEST_FILE_OF_PRODUCTS, TEST_DF_1, (
                                     f'Файл {TEST_FILE_OF_PRODUCTS} создан! Запись добавлена!', 'blue')),
                             (TEST_PATH, TEST_FILE_OF_PRODUCTS, TEST_DF_3, (
                                     f'Файл {TEST_FILE_OF_PRODUCTS} создан! Запись добавлена!', 'blue')),
                         ]
                         )
def test_data_reader_add_to_file_csv_1(file_path, file_name, df, expected_result):
    res = DataReader(file_path, file_name).add_to_file_csv(df)
    remove_test_file(TEST_PATH, TEST_FILE_OF_PRODUCTS)
    assert res == expected_result


@pytest.mark.parametrize('file_path, file_name, df, expected_result',
                         [
                             (TEST_PATH, TEST_FILE_OF_PRODUCTS, TEST_DF_1, (
                                     f'Запись добавлена в файл {TEST_FILE_OF_PRODUCTS} !', 'blue')),
                             (TEST_PATH, TEST_FILE_OF_PRODUCTS, TEST_DF_3, (
                                     f'Запись добавлена в файл {TEST_FILE_OF_PRODUCTS} !', 'blue')),
                         ]
                         )
def test_data_reader_add_to_file_csv_2(file_path, file_name, df, expected_result):
    DataReader(file_path, file_name).add_to_file_csv(TEST_DF_2)
    res = DataReader(file_path, file_name).add_to_file_csv(df)
    remove_test_file(TEST_PATH, TEST_FILE_OF_PRODUCTS)
    assert res == expected_result


@pytest.mark.parametrize('file_path, file_name, df, expected_result',
                         [
                             (TEST_PATH, TEST_FILE_OF_PRODUCTS, TEST_DF_2, (
                                     f'Запись добавлена в файл {TEST_FILE_OF_PRODUCTS} !', 'blue')),
                             (TEST_PATH, TEST_FILE_OF_PRODUCTS, TEST_DF_3, (
                                     f'Запись добавлена в файл {TEST_FILE_OF_PRODUCTS} !', 'blue')),
                         ]
                         )
def test_data_reader_add_to_file_csv_3(create_test_csv_file, file_path, file_name, df, expected_result):
    res = DataReader(file_path, file_name).add_to_file_csv(df)
    assert res == expected_result

