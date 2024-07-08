import pytest
import os

from tests.test_data_reader.test_data_reader import TEST_DF_1, TEST_PATH, TEST_FILE_OF_PRODUCTS, remove_test_file


# def remove_test_file(file_path, file_name):
#     if os.path.exists(os.path.join(file_path, file_name)):
#         os.remove(os.path.join(file_path, file_name))


@pytest.fixture(scope="function")  # autouse=True  --- if need to do it before other fixtures
def create_test_csv_file():
    a = TEST_DF_1.to_csv(os.path.join(TEST_PATH, TEST_FILE_OF_PRODUCTS), index=False)
    # return is swapped out for yield
    yield a  # Any teardown code for the fixture is placed after the yield
    remove_test_file(TEST_PATH, TEST_FILE_OF_PRODUCTS)
