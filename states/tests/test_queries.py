from copy import deepcopy

# from unittest.mock import patch
import pytest

import states.queries as qry


def get_temp_rec():
    return deepcopy(qry.SAMPLE_STATE)


@pytest.fixture(scope='function')
def temp_state_no_del():
    temp_rec = get_temp_rec()
    qry.create(get_temp_rec())
    return temp_rec


@pytest.fixture(scope='function')
def temp_state():
    temp_rec = get_temp_rec()
    new_rec_id = qry.create(get_temp_rec())
    yield new_rec_id
    try:
        qry.delete(temp_rec[qry.NAME], temp_rec[qry.STATE_CODE])
    except ValueError:
        print('The record was already deleted.')


def test_num_states():
    # get the count
    old_count = qry.num_states()
    # add a record
    qry.create(get_temp_rec())
    assert qry.num_states() == old_count + 1


def test_good_create():
    old_count = qry.num_states()
    new_rec_id = qry.create(get_temp_rec())
    assert qry.is_valid_id(new_rec_id)
    assert qry.num_states() == old_count + 1


def test_create_bad_name():
    with pytest.raises(ValueError):
        qry.create({})


def test_create_bad_param_type():
    with pytest.raises(ValueError):
        qry.create(17)


def test_delete(temp_state_no_del):
    ret = qry.delete(temp_state_no_del[qry.NAME],
                     temp_state_no_del[qry.STATE_CODE])
    assert ret == 1


def test_delete_not_there():
    with pytest.raises(ValueError):
        qry.delete('some state name that is not there', 'not a state')


def test_read(temp_state):
    states = qry.read()
    assert isinstance(states, list)
    assert get_temp_rec() in states
