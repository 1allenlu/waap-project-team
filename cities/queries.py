
"""
This file deals with our city-level data.
"""
import data.db_connect as dbc
MIN_ID_LEN = 1

CITY_COLLECTION = 'cities'

ID = 'id'
NAME = 'name'
STATE_CODE = 'state_code'

SAMPLE_CITY = {
    NAME: 'New York',
    STATE_CODE: 'NY',
}

# Placeholder for potential in-memory caching (currently unused)
city_cache = {}

SORTABLE_FIELDS = {NAME, STATE_CODE}


def is_valid_id(_id: str) -> bool:
    # Accept only non-empty strings; numeric or other types are rejected early
    if not isinstance(_id, str):
        return False
    if len(_id) < MIN_ID_LEN:
        return False
    return True


def num_cities() -> int:
    return len(read())


def create(flds: dict) -> str:
    print(f'{flds=}')
    if not isinstance(flds, dict):
        raise ValueError(f'Bad type for {type(flds)=}')
    if not flds.get(NAME):
        raise ValueError(f'Bad value for {flds.get(NAME)=}')
    new_id = dbc.create(CITY_COLLECTION, flds)
    print(f'{new_id=}')
    return new_id


def get_by_id(city_id: str) -> dict:
    """Return a single city by its database id (string)."""
    if not is_valid_id(city_id):
        raise ValueError('Invalid id')
    rec = dbc.read_one(CITY_COLLECTION, {dbc.MONGO_ID: city_id})
    if rec is None:
        raise ValueError('City not found')
    return rec


def update_by_id(city_id: str, update_fields: dict) -> bool:
    """Update a city by id; returns True if modified_count > 0"""
    if not is_valid_id(city_id):
        raise ValueError('Invalid id')
    if not isinstance(update_fields, dict):
        raise ValueError('update_fields must be a dict')
    res = dbc.update(CITY_COLLECTION, {dbc.MONGO_ID: city_id}, update_fields)
    # pymongo UpdateResult has modified_count attribute
    try:
        return getattr(res, 'modified_count', 0) > 0
    except Exception:
        return False


def delete_by_id(city_id: str) -> bool:
    """Delete a city by id; returns True if deleted_count > 0"""
    if not is_valid_id(city_id):
        raise ValueError('Invalid id')
    deleted = dbc.delete(CITY_COLLECTION, {dbc.MONGO_ID: city_id})
    return deleted > 0


def delete(name: str, state_code: str) -> bool:
    ret = dbc.delete(CITY_COLLECTION, {NAME: name, STATE_CODE: state_code})
    if ret < 1:
        raise ValueError(f'City not found: {name}, {state_code}')
    return ret


def read_sorted(sort=None):
    items = dbc.read(CITY_COLLECTION)
    if not sort:
        return items

    desc = sort.startswith("-")
    key = sort[1:] if desc else sort
    if key not in SORTABLE_FIELDS:
        return items

    def keyfunc(rec):
        return (rec.get(key) or "").upper()

    return sorted(items, key=keyfunc, reverse=desc)


def read() -> dict:
    return dbc.read(CITY_COLLECTION)


def main():
    print(read())


if __name__ == '__main__':
    main()
