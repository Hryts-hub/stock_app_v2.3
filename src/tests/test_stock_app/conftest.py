import pytest

# from tests.test_stock_app.test_stock_app_class import TEST_DF_1, TEST_PATH, TEST_FILE_OF_PRODUCTS
from tests.test_stock_app.test_stock_app_class import TEST_DF_4, TEST_PATH, TEST_FILE_OF_PRODUCTS


@pytest.fixture()  # autouse=True  --- if need to do it before other fixtures
def create_test_csv_file_fin():
    TEST_DF_4.to_csv(f'{TEST_PATH}{TEST_FILE_OF_PRODUCTS}', index=False)
