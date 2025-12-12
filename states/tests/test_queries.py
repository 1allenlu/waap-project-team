from copy import deepcopy

# from unittest.mock import patch
import pytest
import uuid

import states.queries as qry


def get_temp_rec():
    rec = deepcopy(qry.SAMPLE_STATE)
    # use unique code per test to avoid duplicate-key failures
    rec[qry.STATE_CODE] = f"TS-{uuid.uuid4().hex[:6]}"
    rec[qry.NAME] = f"TestState-{rec[qry.STATE_CODE]}"
    return rec


@pytest.fixture(scope='function')
def temp_state_no_del():
    temp_rec = get_temp_rec()
    qry.create(temp_rec)
    return temp_rec


@pytest.fixture(scope='function')
def temp_state():
    temp_rec = get_temp_rec()
    new_rec_id = qry.create(temp_rec)
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


def test_read(temp_state_no_del):
    states = qry.read()
    assert isinstance(states, list)
    assert any(
        s.get(qry.STATE_CODE) == temp_state_no_del[qry.STATE_CODE]
        for s in states
    )


def test_count():
    count = qry.count()
    assert isinstance(count, int)
    assert count >= 0


def test_is_valid_id():
    # Valid IDs
    assert qry.is_valid_id('507f1f77bcf86cd799439011')
    assert qry.is_valid_id('a')
    # Invalid IDs
    assert not qry.is_valid_id('')
    assert not qry.is_valid_id(123)
    assert not qry.is_valid_id(None)


def test_get_by_id(temp_state):
    state = qry.get_by_id(temp_state)
    assert state is not None
    assert qry.NAME in state


def test_get_by_id_invalid():
    with pytest.raises(ValueError, match='Invalid id'):
        qry.get_by_id('')


def test_get_by_id_not_found():
    with pytest.raises(ValueError, match='State not found'):
        qry.get_by_id('507f1f77bcf86cd799439011')


def test_update_by_id(temp_state):
    updated = qry.update_by_id(temp_state, {qry.NAME: 'Updated State'})
    assert isinstance(updated, bool)


def test_update_by_id_invalid_id():
    with pytest.raises(ValueError, match='Invalid id'):
        qry.update_by_id('', {qry.NAME: 'Updated'})


def test_update_by_id_invalid_fields():
    with pytest.raises(ValueError, match='update_fields must be a dict'):
        qry.update_by_id('507f1f77bcf86cd799439011', 'not a dict')


def test_delete_by_id(temp_state):
    result = qry.delete_by_id(temp_state)
    assert result is True


def test_delete_by_id_invalid():
    with pytest.raises(ValueError, match='Invalid id'):
        qry.delete_by_id('')


def test_delete_by_id_not_found():
    result = qry.delete_by_id('507f1f77bcf86cd799439011')
    assert result is False


def test_create_duplicate_key():
    temp_rec = get_temp_rec()
    qry.create(temp_rec)
    # Try to create the same state code + country code again
    with pytest.raises(ValueError, match='Duplicate key'):
        qry.create(temp_rec)


def test_create_missing_state_code():
    with pytest.raises(ValueError):
        qry.create({qry.NAME: 'Test', qry.COUNTRY_CODE: 'USA'})


def test_create_missing_country_code():
    with pytest.raises(ValueError):
        qry.create({qry.NAME: 'Test', qry.STATE_CODE: 'TS'})
