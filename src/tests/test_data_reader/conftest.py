import pytest

from tests.test_data_reader.test_data_reader import TEST_DF_1, TEST_PATH, TEST_FILE_OF_PRODUCTS


@pytest.fixture()  # autouse=True  --- if need to do it before other fixtures
def create_test_csv_file():
    TEST_DF_1.to_csv(f'{TEST_PATH}{TEST_FILE_OF_PRODUCTS}', index=False)
