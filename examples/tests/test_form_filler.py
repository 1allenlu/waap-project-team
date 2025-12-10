from unittest.mock import patch

import examples.form_filler as ff


def test_get_fld_names():
    # Call get_fld_names() with the test field descriptions
    ret = ff.get_fld_names(ff.TEST_FLD_DESCRIPS)
    # The result should be a list of field names
    assert isinstance(ret, list)
    # The test field should be included in the returned list
    assert ff.TEST_FLD in ret


def test_get_form_descr():
    # Call get_form_descr() to retrieve the field description mapping
    ret = ff.get_form_descr(ff.TEST_FLD_DESCRIPS)
    # The return value should be a dictionary
    assert isinstance(ret, dict)
    # The test field must exist in the description dictionary
    assert ff.TEST_FLD in ret


@patch('examples.form_filler.get_input', return_value='Y')
def test_form(mock_get_input):
    assert isinstance(ff.form(ff.TEST_FLD_DESCRIPS), dict)
