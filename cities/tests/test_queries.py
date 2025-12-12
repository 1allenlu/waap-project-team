from copy import deepcopy

# from unittest.mock import patch
import pytest

import cities.queries as qry


def get_temp_rec():
    return deepcopy(qry.SAMPLE_CITY)


@pytest.fixture(scope='function')
def temp_city_no_del():
    temp_rec = get_temp_rec()
    qry.create(get_temp_rec())
    return temp_rec


@pytest.fixture(scope='function')
def temp_city():
    temp_rec = get_temp_rec()
    new_rec_id = qry.create(get_temp_rec())
    yield new_rec_id
    try:
        qry.delete(temp_rec[qry.NAME], temp_rec[qry.STATE_CODE])
    except ValueError:
        print('The record was already deleted.')


@pytest.mark.skip('This is an example of a bad test!')
def test_bad_test_for_num_cities():
    assert qry.num_cities() == len(qry.city_cache)


def test_num_cities():
    # get the count
    old_count = qry.num_cities()
    # add a record
    qry.create(get_temp_rec())
    assert qry.num_cities() == old_count + 1


def test_good_create():
    old_count = qry.num_cities()
    new_rec_id = qry.create(get_temp_rec())
    assert qry.is_valid_id(new_rec_id)
    assert qry.num_cities() == old_count + 1


def test_create_bad_name():
    with pytest.raises(ValueError):
        qry.create({})


def test_create_bad_param_type():
    with pytest.raises(ValueError):
        qry.create(17)


def test_delete(temp_city_no_del):
    ret = qry.delete(
        temp_city_no_del[qry.NAME], temp_city_no_del[qry.STATE_CODE])
    assert ret == 1


def test_delete_not_there():
    with pytest.raises(ValueError):
        qry.delete('some city name that is not there', 'not a state')


def test_read(temp_city):
    cities = qry.read()
    assert isinstance(cities, list)
    assert get_temp_rec() in cities


def test_is_valid_id():
    # Valid IDs
    assert qry.is_valid_id('507f1f77bcf86cd799439011')
    assert qry.is_valid_id('a')
    # Invalid IDs
    assert not qry.is_valid_id('')
    assert not qry.is_valid_id(123)
    assert not qry.is_valid_id(None)


def test_get_by_id(temp_city):
    city = qry.get_by_id(temp_city)
    assert city is not None
    assert qry.NAME in city


def test_get_by_id_invalid():
    with pytest.raises(ValueError, match='Invalid id'):
        qry.get_by_id('')


def test_get_by_id_not_found():
    with pytest.raises(ValueError, match='City not found'):
        qry.get_by_id('507f1f77bcf86cd799439011')


def test_update_by_id(temp_city):
    updated = qry.update_by_id(temp_city, {qry.NAME: 'Updated City'})
    assert isinstance(updated, bool)


def test_update_by_id_invalid_id():
    with pytest.raises(ValueError, match='Invalid id'):
        qry.update_by_id('', {qry.NAME: 'Updated'})


def test_update_by_id_invalid_fields():
    with pytest.raises(ValueError, match='update_fields must be a dict'):
        qry.update_by_id('507f1f77bcf86cd799439011', 'not a dict')


def test_delete_by_id(temp_city):
    result = qry.delete_by_id(temp_city)
    assert result is True


def test_delete_by_id_invalid():
    with pytest.raises(ValueError, match='Invalid id'):
        qry.delete_by_id('')


def test_delete_by_id_not_found():
    result = qry.delete_by_id('507f1f77bcf86cd799439011')
    assert result is False


def test_read_sorted_ascending():
    cities = qry.read_sorted(sort=qry.NAME)
    assert isinstance(cities, list)


def test_read_sorted_descending():
    cities = qry.read_sorted(sort=f'-{qry.NAME}')
    assert isinstance(cities, list)


def test_read_sorted_invalid_field():
    with pytest.raises(ValueError, match='Invalid sort field'):
        qry.read_sorted(sort='invalid_field')

