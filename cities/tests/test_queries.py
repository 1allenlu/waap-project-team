from unittest.mock import patch
import pytest

import cities.queries as qry


@pytest.fixture(scope='function')
def temp_city():
    new_rec_id = qry.create(qry.SAMPLE_CITY)
    yield new_rec_id
    try:
        qry.delete(new_rec_id)
    except ValueError:
        print('The record was already deleted.')


@pytest.mark.skip('This is an example of a bad test!')
def test_bad_test_for_num_cities():
    assert qry.num_cities() == len(qry.city_cache)


@pytest.mark.skip('revive once all functions are cutover!')
def test_num_cities():
    # get the count
    old_count = qry.num_cities()
    # add a record
    qry.create(qry.SAMPLE_CITY)
    assert qry.num_cities() == old_count + 1

@pytest.mark.skip("Skipping until MongoDB mock or service is added")
def test_good_create():
    old_count = qry.num_cities()
    new_rec_id = qry.create(qry.SAMPLE_CITY)
    assert qry.is_valid_id(new_rec_id)
    # assert qry.num_cities() == old_count + 1


def test_create_bad_name():
    with pytest.raises(ValueError):
        qry.create({})


def test_create_bad_param_type():
    with pytest.raises(ValueError):
        qry.create(17)


@pytest.mark.skip('revive once all functions are cutover!')
def test_delete(temp_city):
    qry.delete(temp_city)
    assert temp_city not in qry.read()


def test_delete_not_there():
    with pytest.raises(ValueError):
        qry.delete('some value that is not there')


@pytest.mark.skip('revive once all functions are cutover!')
def test_read(temp_city):
    cities = qry.read()
    assert isinstance(cities, dict)
    assert temp_city in cities


@pytest.mark.skip('revive once all functions are cutover!')
def test_read_cant_connect():
    with pytest.raises(ConnectionError):
        cities = qry.read()
