
"""
This file deals with our state-level data.
"""
import data.db_connect as dbc
MIN_ID_LEN = 1

STATE_COLLECTION = 'states'

ID = 'id'
NAME = 'name'
STATE_CODE = 'state_code'
POPULATION = 'population'

SAMPLE_STATE = {
    NAME: 'New York',
    STATE_CODE: 'NY',
    POPULATION: 19500000,
}

# Placeholder for potential in-memory caching (currently unused)
state_cache = {}

SORTABLE_FIELDS = {NAME, STATE_CODE, POPULATION}


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


def delete(name: str, state_code: str) -> bool:
    ret = dbc.delete(STATE_COLLECTION, {NAME: name, STATE_CODE: state_code})
    if ret < 1:
        raise ValueError(f'State not found: {name}, {state_code}')
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
