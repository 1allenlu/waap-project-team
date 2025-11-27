
"""
This file deals with our state-level data.
"""
import data.db_connect as dbc
from data.db_connect import is_valid_id 
from functools import wraps
MIN_ID_LEN = 1

STATE_COLLECTION = 'states'

ID = 'id'
NAME = 'name'
CODE = 'code'
COUNTRY_CODE = 'country_code'

SAMPLE_CODE = 'NY'
SAMPLE_COUNTRY = 'USA'
SAMPLE_KEY = (SAMPLE_CODE, SAMPLE_COUNTRY)
SAMPLE_STATE = {
    NAME: 'New York',
    CODE: SAMPLE_CODE,
    COUNTRY_CODE: SAMPLE_COUNTRY,
}

cache = None


def needs_cache(fn, *args, **kwargs):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not cache:
            load_cache()
        return fn(*args, **kwargs)
    return wrapper


@needs_cache
def count() -> int:
    return len(cache)


@needs_cache
def create(flds: dict, reload=True) -> str:
    if not isinstance(flds, dict):
        raise ValueError(f'Bad type for {type(flds)=}')
    code = flds.get(CODE)
    country_code = flds.get(COUNTRY_CODE)
    if not flds.get(NAME):
        raise ValueError(f'Bad value for {flds.get(NAME)=}')
    if not code:
        raise ValueError(f'Bad value for {code=}')
    if not country_code:
        raise ValueError(f'Bad value for {country_code=}')
    if (code, country_code) in cache:
        raise ValueError(f'Duplicate key: {code=}; {country_code=}')
    new_id = dbc.create(STATE_COLLECTION, flds)
    print(f'{new_id=}')
    if reload:
        load_cache()
    return new_id


@needs_cache
def read() -> dict:
    return cache


def load_cache():
    global cache
    cache = {}
    states = dbc.read(STATE_COLLECTION)
    for state in states:
        cache[(state[CODE], state[COUNTRY_CODE])] = state



def is_valid_id(_id: str) -> bool:
    # Accept only non-empty strings; numeric or other types are rejected early
    if not isinstance(_id, str):
        return False
    if len(_id) < MIN_ID_LEN:
        return False
    return True


def num_states() -> int:
    return len(read())


def create(flds: dict) -> str:
    print(f'{flds=}')
    if not isinstance(flds, dict):
        raise ValueError(f'Bad type for {type(flds)=}')
    if not flds.get(NAME):
        raise ValueError(f'Bad value for {flds.get(NAME)=}')
    new_id = dbc.create(STATE_COLLECTION, flds)
    print(f'{new_id=}')
    return new_id



def delete(code: str, cntry_code: str) -> bool:
    ret = dbc.delete(STATE_COLLECTION, {CODE: code, COUNTRY_CODE: cntry_code})
    if ret < 1:
        raise ValueError(f'State not found: {code}, {cntry_code}')
    load_cache()
    return ret


def read_sorted(sort=None):
    items = dbc.read(STATE_COLLECTION)
    if not sort:
        return items

    desc = sort.startswith("-")
    key = sort[1:] if desc else sort
    if key not in SORTABLE_FIELDS:
        return items

    def keyfunc(rec):
        val = rec.get(key)
        # For numeric fields, return as-is; for strings, uppercase
        if isinstance(val, (int, float)):
            return val
        return (val or "").upper()

    return sorted(items, key=keyfunc, reverse=desc)


def read() -> dict:
    return dbc.read(STATE_COLLECTION)


def main():
    print(read())


if __name__ == '__main__':
    main()
