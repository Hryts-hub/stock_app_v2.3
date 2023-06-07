import pytest
import pandas as pd

from stock_app_v2.dict_macker_class import DictMaker

combobox_dict = {'fld_nano_test': [{777: 1, 1529: 1, 1495: 1}, {}, 1, 1],
                 'pp_control_std_1_4_test': [{777: 1, 723: 1, 613: 1, 371: 1, 629: 1, 524: 1, 377: 1, 384: 1},{}, 1, 2]}

TEST_COL_NAME1 = 'Артикул'
TEST_COL_NAME2 = 'Число'

TEST_MODUL_DF_1 = pd.DataFrame({
    TEST_COL_NAME1: [1.036e+03, 2.000e+03],
    TEST_COL_NAME2: [-1.000e+00, -3.000e+00],
})

TEST_MODUL_DF_2 = pd.DataFrame()


def test_make_report_dict():
    assert DictMaker(combobox_dict).make_report_dict() == {371: 1,
                                                           377: 1,
                                                           384: 1,
                                                           524: 1,
                                                           613: 1,
                                                           629: 1,
                                                           723: 1,
                                                           777: 2,
                                                           1495: 1,
                                                           1529: 1}


@pytest.mark.parametrize('modul_df, col_name1, col_name2, expected_result',
                         [
                             (TEST_MODUL_DF_1, TEST_COL_NAME1, TEST_COL_NAME2, ({1036: 1.0, 2000: 3.0})),
                             (TEST_MODUL_DF_2, TEST_COL_NAME1, TEST_COL_NAME2, ({})),
                         ]
                         )
def test_make_dict_from_df(modul_df, col_name1, col_name2, expected_result):
    res = DictMaker().make_dict_from_df(modul_df, col_name1, col_name2)
    assert res == expected_result


@pytest.mark.parametrize('test_str, expected_result',
                         [
                             ('{111: 0, 222: 2}', ({222: 2}, {111: 0})),
                             ('{111: 1, 222: 0}', ({111: 1}, {222: 0}))
                         ]
                         )
def test_remove_zero_values(test_str, expected_result):
    res = DictMaker().remove_zero_values(test_str)
    assert res == expected_result

