import os
import pytest

# This is an optional integration test that hits a running MongoDB instance.
# It is skipped by default; set RUN_INTEGRATION=1 in the environment to run it.

pytestmark = pytest.mark.skipif(
    os.environ.get('RUN_INTEGRATION', '0') != '1',
    reason='Integration tests disabled by default',
)


def test_connect_and_basic_ops():
    """Attempt to connect and perform a simple list/create/delete sequence.

    This will use real MongoDB and is intended for local/manual testing only.
    """
    from data import db_connect as dbc

    # Try to get a client and list collections
    # (no assertions beyond no-exception)
    client = dbc.connect_db()
    assert client is not None

    # Simple smoke: ensure the database object exists
    db = client[dbc.GEO_DB]
    assert db is not None

    # Insert a test document and then remove it
    coll = db['__integration_test']
    res = coll.insert_one({'x': 1})
    assert res.inserted_id is not None
    deleted = coll.delete_one({'_id': res.inserted_id})
    assert deleted.deleted_count == 1
    # Emit a clear success message for manual runs
    print('successful')
