
"""
This file deals with our state-level data.
"""
from functools import wraps

import data.db_connect as dbc
from bson import ObjectId

MIN_ID_LEN = 1

STATE_COLLECTION = 'states'

ID = 'id'
NAME = 'name'
STATE_CODE = 'code'
COUNTRY_CODE = 'country_code'

SAMPLE_CODE = 'NY'
SAMPLE_COUNTRY = 'USA'
SAMPLE_KEY = (SAMPLE_CODE, SAMPLE_COUNTRY)
SAMPLE_STATE = {
    NAME: 'New York',
    STATE_CODE: SAMPLE_CODE,
    COUNTRY_CODE: SAMPLE_COUNTRY,
}

# Optional set of sortable fields (unused currently)
SORTABLE_FIELDS = {NAME, STATE_CODE, COUNTRY_CODE}

# In-memory cache keyed by (STATE_CODE, COUNTRY_CODE)
cache = None


def needs_cache(fn):
    """Decorator: ensures cache is loaded before function runs."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if cache is None:
            load_cache()
        return fn(*args, **kwargs)
    return wrapper


def load_cache():
    """Loads all states from DB into memory, keyed by (code, country)."""
    global cache
    cache = {}
    states = dbc.read(STATE_COLLECTION)
    for state in states:
        code = state.get(STATE_CODE)
        country = state.get(COUNTRY_CODE)
        if code is None or country is None:
            continue
        cache[(code, country)] = state


@needs_cache
def count() -> int:
    """Returns total number of cached states."""
    if cache is None:
        load_cache()
    return len(cache)


@needs_cache
def num_states() -> int:
    """Alias for count(); returns total cached states."""
    if cache is None:
        load_cache()
    return len(cache)


@needs_cache
def create(flds: dict, reload=True) -> str:
    """Creates a new state in DB. Validates fields and checks for duplicates."""
    if not isinstance(flds, dict):
        raise ValueError(f'Bad type for {type(flds)=}')
    code = flds.get(STATE_CODE)
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
    if reload:
        load_cache()
    return new_id


@needs_cache
def read() -> list:
    """Returns all states as a list from cache."""
    return list(cache.values())


def is_valid_id(_id: str) -> bool:
    """Checks if _id is a non-empty string."""
    if not isinstance(_id, str):
        return False
    if len(_id) < MIN_ID_LEN:
        return False
    return True


@needs_cache
def get_by_id(state_id: str) -> dict:
    """Fetches a single state by its MongoDB ObjectId string."""
    if not is_valid_id(state_id):
        raise ValueError('Invalid id')
    rec = dbc.read_one(STATE_COLLECTION, {dbc.MONGO_ID: ObjectId(state_id)})
    if rec is None:
        raise ValueError('State not found')
    return rec


@needs_cache
def update_by_id(state_id: str, update_fields: dict) -> bool:
    """Updates a state by id. Returns True if a document was modified."""
    if not is_valid_id(state_id):
        raise ValueError('Invalid id')
    if not isinstance(update_fields, dict):
        raise ValueError('update_fields must be a dict')
    res = dbc.update(
        STATE_COLLECTION, {dbc.MONGO_ID: ObjectId(state_id)}, update_fields)
    load_cache()
    return getattr(res, 'modified_count', 0) > 0


@needs_cache
def delete_by_id(state_id: str) -> bool:
    """Deletes a state by id. Returns True if a document was deleted."""
    if not is_valid_id(state_id):
        raise ValueError('Invalid id')
    deleted = dbc.delete(STATE_COLLECTION, {dbc.MONGO_ID: ObjectId(state_id)})
    load_cache()
    return deleted > 0


def delete(name: str, state_code: str) -> bool:
    """Deletes a state by name + code (legacy). Raises if not found."""
    ret = dbc.delete(STATE_COLLECTION, {NAME: name, STATE_CODE: state_code})
    if ret < 1:
        raise ValueError(f'State not found: {state_code}')
    load_cache()
    return ret


# def read_sorted(sort=None):
# endpoints for states do not call read_sorted
#     items = dbc.read(STATE_COLLECTION)
#     if not sort:
#         return items
#     desc = sort.startswith("-")
#     key = sort[1:] if desc else sort
#     if key not in SORTABLE_FIELDS:
#         return items
#     def keyfunc(rec):
#         val = rec.get(key)
#         # For numeric fields, return as-is; for strings, uppercase
#         if isinstance(val, (int, float)):
#             return val
#         return (val or "").upper()
#     return sorted(items, key=keyfunc, reverse=desc)


def main():
    print(read())


if __name__ == '__main__':
    main()
