"""
All interaction with MongoDB should be through this file!
We may be required to use a new database at any point.
"""
import os
import time
import logging
from functools import wraps

import pymongo as pm

LOCAL = "0"
CLOUD = "1"

GEO_DB = 'geo2025DB'

client = None

MONGO_ID = '_id'

# Configure logger for this module
logger = logging.getLogger(__name__)

# Retry configuration for connecting to MongoDB. Can be tuned via env vars.
CONNECT_RETRIES = int(os.environ.get('DB_CONNECT_RETRIES', '3'))
RETRY_DELAY_SECONDS = float(os.environ.get('DB_CONNECT_RETRY_DELAY', '1'))


def needs_db(fn, *args, **kwargs):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        """Ensure a live MongoDB client exists before calling fn.

        If the client is not set, or if the server is unreachable
        (server_info raises), try to (re)connect.
        """
        global client
        try:
            if client is None:
                connect_db()
            else:
                # A lightweight check to ensure the client is still connected.
                # server_info() will raise if the server is not reachable.
                client.server_info()
        except Exception:
            # Attempt to reconnect once
            connect_db()
        return fn(*args, **kwargs)

    return wrapper


def connect_db():
    """
    This provides a uniform way to connect to the DB across all uses.
    Returns a mongo client object... maybe we shouldn't?
    Also set global client variable.
    We should probably either return a client OR set a
    client global.
    """
    global client
    if client is not None:
        return client

    last_exc = None
    for attempt in range(1, CONNECT_RETRIES + 1):
        try:
            logger.info('Connecting to MongoDB (attempt %d/%d)', attempt, CONNECT_RETRIES)
            if os.environ.get('CLOUD_MONGO', LOCAL) == CLOUD:
                password = os.environ.get('MONGO_PASSWD')
                if not password:
                    raise ValueError('You must set your password to use Mongo in the cloud.')
                logger.debug('Using cloud Mongo configuration')
                client_candidate = pm.MongoClient(f'mongodb+srv://gcallah:{password}'
                                                    + '@koukoumongo1.yud9b.mongodb.net/'
                                                    + '?retryWrites=true&w=majority')
            else:
                logger.debug('Using local Mongo configuration')
                client_candidate = pm.MongoClient()

            # Verify connection by requesting server info; this will raise
            # an exception if the server is unreachable.
            client_candidate.server_info()

            # Success: set global and return
            client = client_candidate
            logger.info('Connected to MongoDB successfully')
            return client
        except Exception as e:
            logger.warning('MongoDB connection attempt %d failed: %s', attempt, e)
            last_exc = e
            try:
                # Close candidate if it was created
                if 'client_candidate' in locals():
                    client_candidate.close()
            except Exception:
                pass
            if attempt < CONNECT_RETRIES:
                time.sleep(RETRY_DELAY_SECONDS)

    # If we exit the loop without returning, raise the last exception
    logger.error('Could not connect to MongoDB after %d attempts', CONNECT_RETRIES)
    raise last_exc


def convert_mongo_id(doc: dict):
    if MONGO_ID in doc:
        # Convert mongo ID to a string so it works as JSON
        doc[MONGO_ID] = str(doc[MONGO_ID])


@needs_db
def create(collection, doc, db=GEO_DB):
    """
    Insert a single doc into collection.
    """
    print(f'{doc=}')
    ret = client[db][collection].insert_one(doc)
    return str(ret.inserted_id)


@needs_db
def read_one(collection, filt, db=GEO_DB):
    """
    Find with a filter and return on the first doc found.
    Return None if not found.
    """
    for doc in client[db][collection].find(filt):
        convert_mongo_id(doc)
        return doc


@needs_db
def delete(collection: str, filt: dict, db=GEO_DB):
    """
    Find with a filter and return after deleting the first doc found.
    """
    print(f'{filt=}')
    del_result = client[db][collection].delete_one(filt)
    return del_result.deleted_count


@needs_db
def update(collection, filters, update_dict, db=GEO_DB):
    return client[db][collection].update_one(filters, {'$set': update_dict})


@needs_db
def read(collection, db=GEO_DB, no_id=True) -> list:
    """
    Returns a list from the db.
    """
    ret = []
    for doc in client[db][collection].find():
        if no_id:
            del doc[MONGO_ID]
        else:
            convert_mongo_id(doc)
        ret.append(doc)
    return ret


def read_dict(collection, key, db=GEO_DB, no_id=True) -> dict:
    """
    Doesn't need db decorator because read() has it.
    """
    # Ensure there is a live connection for callers that may bypass read()
    # by calling this function directly.
    @needs_db
    def _inner_read():
        return read(collection, db=db, no_id=no_id)

    recs = _inner_read()
    recs_as_dict = {}
    for rec in recs:
        recs_as_dict[rec[key]] = rec
    return recs_as_dict