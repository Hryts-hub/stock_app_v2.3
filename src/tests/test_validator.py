import pytest

from stock_app_v2.validator_class import Validator


@pytest.mark.parametrize("input_string, expected_output", [
    ("example", "{example}"),         # No curly brackets
    ("{example", "{example}"),        # Missing closing curly bracket
    ("example}", "{example}"),        # Missing opening curly bracket
    ("{example}", "{example}"),       # Both curly brackets present
    ("", "{}"),                       # Empty string
    ("{", "{}"),                      # Only opening curly bracket
    ("}", "{}"),                      # Only closing curly bracket
])
def test_check_curly_brackets(input_string, expected_output):
    result = Validator._check_curly_brackets(input_string)
    assert result == expected_output


@pytest.mark.parametrize("input_string, expected_output", [
    ("{111:2, 333:4}", ("{111: 2.0, 333: 4.0}", False, True)),         # valid dictionary string
    ("{111:2, 333:0}", ("{111: 2.0}", True, True)),                    # 0
    ("{111:2, 0:4}", ("{111: 2.0}", True, True)),                      # 0
    ("{c111:2, 333:4}", ("{111: 2.0, 333: 4.0}", True, True)),         # c
    ("{111:2, 333c:4}", ("{333: 4.0, 111: 2.0}", True, True)),         # c
    ("{111:2, 333:4c}", ("{111: 2.0}", True, True)),                   # err in q-ty
    ("{111:2, 3c33:4}", ("{111: 2.0}", True, True)),                   # err in art
    ("{111:2, 333:4, 111:5}", ("{111: 7.0, 333: 4.0}", False, True)),  # valid dictionary string, sum
    ("{111:2, 333:4, 111:5, 333:4.4, 333:0}", ("{111: 7.0, 333: 8.4}", False, True)),  # valid dictionary string, sum
])
def test_try_dict_true(input_string, expected_output):
    result = Validator._try_dict(input_string)
    assert (result[0], result[1] != '', result[2]) == expected_output


@pytest.mark.parametrize("input_string, expected_output", [
    ("{}", ("{}", False, False)),                     # empty dict
    ("{ }", ("{}", True, False)),                     # err format, empty
    ("{a111:2, a333:4}", ("{}", True, False)),        # err key
    ("{111:2a, 333:a4}", ("{}", True, False)),        # err value
    ("{111:0, 333c:0}", ("{}", True, False)),         # 0-value
    ("{0:2, 0:4}", ("{}", True, False)),              # 0-key
    ("{111, }", ("{}", True, False)),                 # err format
])
def test_try_dict_false(input_string, expected_output):
    result = Validator._try_dict(input_string)
    assert (result[0], result[1] != '', result[2]) == expected_output


@pytest.mark.parametrize("block_name, moduls_dict_str, components_dict_str, expected_output", [
    (None, "{111: 1, 222: 2}", "{33: 3}", "111_222"),
    ("", "{111: 1, 222: 2}", "{33: 3}", "111_222"),
    ("   ", "{111: 1, 222: 2}", "{33: 3}", "111_222"),
    ("NBU-1012", "{111: 1, 222: 2}", "{33: 3}", "NBU-1012"),
])
def test_block_name_validation(block_name, moduls_dict_str, components_dict_str, expected_output):
    instance = Validator(block_name, moduls_dict_str, components_dict_str)
    instance._block_name_validation()
    result = instance.block_name
    assert result == expected_output


@pytest.mark.parametrize("block_name, moduls_dict_str, components_dict_str, expected_output", [
    ('', '\n \nc986\n1\n \nc987\n1\n', '', ('{986: 1.0, 987: 1.0}', '{}')),  # 2str mod
    ('', '\n \nc986\n1\n \nc987\n1\n \nc986\n3\n', '', ('{986: 4.0, 987: 1.0}', '{}')),  # 3str mod-duplicates
    ('', '\n \n986\n1\n \n987\n1\n', '', ('{}', '{987: 1.0}')),  # 2str compo ***BUG***
    ('', '\n \n986\n1\n \n987\n1\n \n986\n3\n', '', ('{}', '{986: 4.0, 987: 1.0}')),  # 3str compo-duplicates
    ('', '\n \nc986\n1\n \n987\n1\n', '', ('{986: 1.0}', '{987: 1.0}')),  # 2str mod+compo
    ('', '\n \nc986\n1\n \n987\n1\n \n987\n5\n', '', ('{986: 1.0}', '{987: 6.0}')),  # 3str mod+compo compo-duplicates
    ('', '\n \nс2201\n1\n \nc2166\n1\n \nc2202\n1\n', '', ('{2201: 1.0, 2166: 1.0, 2202: 1.0}', '{}')),  # 3str mod
    ('', '\n \n2201\n1\n \n2166\n1\n \n2202\n1\n', '', ('{}', '{2201: 1.0, 2166: 1.0, 2202: 1.0}')),  # 3str compo
    ('', '\n \n2201\n1\n \n2166\n1\n \n2201\n1\n', '', ('{}', '{2201: 2.0, 2166: 1.0}')),  # 3str compo-dupl
    ('', '\n \nc9zz86\n1\n \nc987\n1\n', '', ('{987: 1.0}', '{}')),  # 2str mod err
    ('', '\n \n2zz201\n1\n \n2166\n1\n \n2202\n1\n', '', ('{}', '{2166: 1.0, 2202: 1.0}')),  # 3str compo err
])
def test_validate_input_excel_3col(block_name, moduls_dict_str, components_dict_str, expected_output):
    result = Validator(block_name, moduls_dict_str, components_dict_str)._validate_input_excel()
    assert result == expected_output


@pytest.mark.parametrize("block_name, moduls_dict_str, components_dict_str, expected_output", [
    ('', '\nc1966\n32\nс1185\n1\n97c\n0,5\n96c\n1\n', '', ('{1966: 32.0, 1185: 1.0, 97: 0.5, 96: 1.0}', '{}')),
    ('', '\nc1966\n32\nс1185\n1\nс1185\n0,5\n96c\n1\n', '', ('{1966: 32.0, 1185: 1.5, 96: 1.0}', '{}')),
    ('', '\n1966\n32\n1185\n1\n97c\n0,5\n96c\n1\n', '', ('{97: 0.5, 96: 1.0}', '{1966: 32.0, 1185: 1.0}')),
    ('', '\nc1966\n32\nс1185\n1\n97\n0,5\n97\n1\n', '', ('{1966: 32.0, 1185: 1.0}', '{97: 1.5}')),
    ('', '\nc1zz966\n32\nс1185\n1\n97c\n0,5\n96c\n1\n', '', ('{1185: 1.0, 97: 0.5, 96: 1.0}', '{}')),
    ('', '\n1966\n32\n1zz185\n1\n97c\n0,5\n96c\n1\n', '', ('{97: 0.5, 96: 1.0}', '{1966: 32.0}')),
    ('', '\nc1966\n0\nс1185\n1\n97c\n0,5\n96c\n1\n', '', ('{1966: 0.0, 1185: 1.0, 97: 0.5, 96: 1.0}', '{}')),
    ('', '\nc0\n32\nс1185\n1\n97c\n0,5\n96c\n1\n', '', ('{0: 32.0, 1185: 1.0, 97: 0.5, 96: 1.0}', '{}')),
    ('', '\n0\n32\nс1185\n1\n97c\n0,5\n96c\n1\n', '', ('{1185: 1.0, 97: 0.5, 96: 1.0}', '{0: 32.0}')),
])
def test_validate_input_excel_2col(block_name, moduls_dict_str, components_dict_str, expected_output):
    result = Validator(block_name, moduls_dict_str, components_dict_str)._validate_input_excel()
    assert result == expected_output


