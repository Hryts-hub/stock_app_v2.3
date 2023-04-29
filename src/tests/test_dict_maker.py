from stock_app_v2.dict_macker_class import DictMaker

combobox_dict = {'fld_nano_test': [{777: 1, 1529: 1, 1495: 1}, 1, 1],
                 'pp_control_std_1_4_test': [{777: 1, 723: 1, 613: 1, 371: 1, 629: 1, 524: 1, 377: 1, 384: 1}, 1, 2]}


def test_dict():
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


