"""
All interaction with MongoDB should be through this file!
We may be required to use a new database at any point.
"""
import os
import time
import re
import logging
from functools import wraps
# import certifi

import pymongo as pm
from contextlib import contextmanager

LOCAL = "0"
CLOUD = "1"

GEO_DB = 'geo2025DB'

client = None

MONGO_ID = '_id'

MIN_ID_LEN = 24
MAX_ID_LEN = 24
_OBJECTID_RE = re.compile(r'^[0-9a-fA-F]{24}$')

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")


user_nm = os.getenv('MONGO_USER_NM', 'datamixmaster')
cloud_svc = os.getenv('MONGO_HOST', 'datamixmaster.26rvk.mongodb.net')
passwd = os.environ.get("MONGO_PASSWORD", '')
cloud_mdb = "mongodb+srv"
db_params = "retryWrites=false&w=majority"


# Configure logger for this module
logger = logging.getLogger(__name__)


# Retry configuration for connecting to MongoDB. Can be tuned via env vars.
CONNECT_RETRIES = int(os.environ.get('DB_CONNECT_RETRIES', '3'))
RETRY_DELAY_SECONDS = float(os.environ.get('DB_CONNECT_RETRY_DELAY', '1'))


def is_valid_id(s) -> bool:
    """Return True if s looks like a MongoDB ObjectId (24 hex chars)."""
    if not isinstance(s, str):
        return False
    return bool(_OBJECTID_RE.fullmatch(s))


def measure_performance(fn):
    """Track performance metrics for database operations."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        start_memory = None

        try:
            import psutil
            process = psutil.Process(os.getpid())
            start_memory = process.memory_info().rss / 1024 / 1024  # MB
        except ImportError:
            pass

        result = fn(*args, **kwargs)

        elapsed = time.time() - start_time
        logger.info(f'{fn.__name__} took {elapsed:.3f}s')

        if start_memory:
            end_memory = process.memory_info().rss / 1024 / 1024
            logger.info(
                f'{fn.__name__} memory delta:'
                f' {end_memory - start_memory:.2f}MB')

        return result

    return wrapper


def retry_on_failure(max_retries=3, delay=1, backoff=2):
    """Retry database operations on failure with exponential backoff."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None

            for attempt in range(1, max_retries + 1):
                try:
                    return fn(*args, **kwargs)
                except (pm.errors.AutoReconnect,
                        pm.errors.NetworkTimeout,
                        pm.errors.ServerSelectionTimeoutError) as e:
                    last_exception = e
                    logger.warning(
                        f'Attempt {attempt}/{max_retries} failed '
                        f'for {fn.__name__}: {e}'
                    )

                    if attempt < max_retries:
                        logger.info(f'Retrying in {current_delay}s...')
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(
                            f'All {max_retries} attempts failed for '
                            f'{fn.__name__}')
                        raise last_exception

            raise last_exception

        return wrapper
    return decorator


def validate_inputs(fn):
    """Validate inputs before database operations."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        collection = kwargs.get('collection') or (args[0] if args else None)

        if collection and not isinstance(collection, str):
            raise ValueError(
                f'Collection name must be a string, got {type(collection)}')

        if collection and not collection.strip():
            raise ValueError('Collection name cannot be empty')

        # Validate document if present
        doc = kwargs.get('doc') or (args[1] if len(args) > 1 else None)
        if doc is not None and not isinstance(doc, dict):
            raise ValueError(f'Document must be a dictionary, got {type(doc)}')

        return fn(*args, **kwargs)

    return wrapper


def cache_results(ttl_seconds=60):
    """Cache database read results for a specified time."""
    cache = {}

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Create a cache key from function name and arguments
            cache_key = (f"{fn.__name__}:{str(args)}:"
                         f"{str(sorted(kwargs.items()))}")
            current_time = time.time()

            # Check if we have a cached result that's still valid
            if cache_key in cache:
                result, timestamp = cache[cache_key]
                if current_time - timestamp < ttl_seconds:
                    logger.debug(f'Cache hit for {fn.__name__}')
                    return result

            # Call the function and cache the result
            result = fn(*args, **kwargs)
            cache[cache_key] = (result, current_time)

            return result

        # Add a method to clear cache
        wrapper.clear_cache = lambda: cache.clear()

        return wrapper
    return decorator


def handle_mongo_errors(fn):
    """Convert MongoDB exceptions to more user-friendly error messages."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except pm.errors.DuplicateKeyError as e:
            logger.error(f'Duplicate key error in {fn.__name__}: {e}')
            raise ValueError(f'Duplicate entry detected: {str(e)}')
        except pm.errors.InvalidDocument as e:
            logger.error(f'Invalid document in {fn.__name__}: {e}')
            raise ValueError(f'Invalid document format: {str(e)}')
        except pm.errors.WriteError as e:
            logger.error(f'Write error in {fn.__name__}: {e}')
            raise RuntimeError(f'Database write failed: {str(e)}')
        except pm.errors.OperationFailure as e:
            logger.error(f'Operation failure in {fn.__name__}: {e}')
            raise RuntimeError(f'Database operation failed: {str(e)}')

    return wrapper


def require_nonempty_filter(fn):
    """Ensure filter is provided for delete/update operations."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        filt = kwargs.get('filt') or kwargs.get('filters')
        if not filt:
            filt = args[1] if len(args) > 1 else None

        if not filt:
            logger.warning(
                f'{fn.__name__} called with empty filter - '
                'this affects all documents!')

        return fn(*args, **kwargs)

    return wrapper


def log_detailed_operation(fn):
    """Log database operations with detailed information."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        collection = (
            kwargs.get('collection')
            or (args[0] if args else 'unknown')
        )
        db = kwargs.get('db', GEO_DB)

        logger.info(
            f'DB Operation: {fn.__name__} |'
            f'Collection: {collection} | DB: {db}'
        )

        start_time = time.time()
        try:
            result = fn(*args, **kwargs)
            elapsed = time.time() - start_time
            logger.info(
                f'Success: {fn.__name__} completed in {elapsed:.3f}s'
            )
            return result
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(
                f'Failed: {fn.__name__} after {elapsed:.3f}s - {str(e)}'
            )
            raise

    return wrapper


def rate_limit(calls_per_second=10):
    """Rate limit database operations to prevent overload."""
    last_called = {}
    min_interval = 1.0 / calls_per_second

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            now = time.time()
            fn_name = fn.__name__

            if fn_name in last_called:
                elapsed = now - last_called[fn_name]
                if elapsed < min_interval:
                    sleep_time = min_interval - elapsed
                    logger.debug(
                        f'Rate limiting {fn_name}, sleeping {sleep_time:.3f}s')
                    time.sleep(sleep_time)

            last_called[fn_name] = time.time()
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def convert_empty_to_none(fn):
    """Convert empty results to None instead of empty list/dict."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        result = fn(*args, **kwargs)

        if result is not None:
            if isinstance(result, (list, dict)) and len(result) == 0:
                return None

        return result

    return wrapper


def ensure_connection_health(fn):
    """Verify connection health before operation and log status."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if client is None:
            logger.warning(
                f'{fn.__name__} called with no client, connecting...')
            connect_db()

        try:
            # Quick health check
            client.admin.command('ping')
        except Exception as e:
            logger.error(f'Connection health check failed: {e}')
            connect_db()
        return fn(*args, **kwargs)

    return wrapper


@contextmanager
def db_session(db=GEO_DB):
    """Context manager for database sessions with automatic cleanup."""
    session = None
    try:
        if client is None:
            connect_db()
        session = client.start_session()
        logger.debug('Database session started')
        yield session
    except Exception as e:
        logger.error(f'Session error: {e}')
        raise
    finally:
        if session:
            session.end_session()
            logger.debug('Database session ended')


def audit_operation(fn):
    """Audit trail for database modifications."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        operation = fn.__name__
        collection = kwargs.get(
            'collection') or (args[0] if args else 'unknown')
        timestamp = time.time()

        logger.info(f'AUDIT: {operation} on {collection} at {timestamp}')

        try:
            result = fn(*args, **kwargs)
            logger.info(f'AUDIT: {operation} completed successfully')
            return result
        except Exception as e:
            logger.error(f'AUDIT: {operation} failed - {str(e)}')
            raise
    return wrapper


def needs_db(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        """Ensure a live MongoDB client exists before calling fn.
        If the client is not set, or if the server is unreachable
        (server_info raises), try to (re)connect. """
        try:
            if client is None:
                connect_db()
            else:
                client.server_info()
        except Exception:
            # Attempt to reconnect once
            connect_db()
        return fn(*args, **kwargs)
    return wrapper


def connect_db():
    """
    This provides a uniform way to connect to the DB across all uses.
    Returns a mongo client object.
    """
    global client
    if client is not None:
        return client

    last_exc = None
    for attempt in range(1, CONNECT_RETRIES + 1):
        try:
            logger.info(
                'Connecting to MongoDB (attempt %d/%d)',
                attempt, CONNECT_RETRIES)

            if os.environ.get('CLOUD_MONGO', LOCAL) == CLOUD:
                username = os.environ.get('MONGO_USER_NM', 'ss15580_db_user')
                password = os.environ.get('MONGO_PASSWD')
                host = os.environ.get(
                    'MONGO_HOST',
                    'geo2025-cluster.jooae0o.mongodb.net'
                )
                if not password:
                    raise ValueError(
                        'You must set your password to use Mongo in the cloud.'
                    )

                logger.debug('Using cloud Mongo configuration')

                # Using the new cloud connection format with certifi
                cloud_mdb = 'mongodb+srv'
                user_nm = 'ss15580_db_user'
                cloud_svc = 'geo2025-cluster.jooae0o.mongodb.net'
                db_params = 'appName=geo2025-cluster'
                client_candidate = pm.MongoClient(
                    f'mongodb+srv://ss15580_db_user:{password}'
                    + '@geo2025-cluster.jooae0o.mongodb.net/'
                    + '?appName=geo2025-cluster')
            else:
                logger.debug('Using local Mongo configuration')
                client_candidate = pm.MongoClient(
                    os.environ.get("MONGO_URI", "mongodb://localhost:27017"),
                    serverSelectionTimeoutMS=2000
                )

            # Verify connection
            client_candidate.server_info()

            # Success: set global and return
            client = client_candidate
            logger.info('Connected to MongoDB successfully')
            return client

        except Exception as e:
            logger.warning(
                'MongoDB connection attempt %d failed: %s',
                attempt, e)
            last_exc = e

            try:
                if 'client_candidate' in locals():
                    client_candidate.close()
            except Exception:
                pass

            if attempt < CONNECT_RETRIES:
                time.sleep(RETRY_DELAY_SECONDS)

    # If we exit the loop without returning, raise the last exception
    logger.error(
        'Could not connect to MongoDB after %d attempts',
        CONNECT_RETRIES
    )
    raise last_exc


def convert_mongo_id(doc: dict):
    if MONGO_ID in doc:
        # Convert mongo ID to a string so it works as JSON
        doc[MONGO_ID] = str(doc[MONGO_ID])


@needs_db
def create(collection: str, doc: dict, db: str = GEO_DB) -> str:
    """
    Insert a single doc into collection.
    """
    print(f'{doc=}')
    ret = client[db][collection].insert_one(doc)
    return str(ret.inserted_id)


@needs_db
def read_one(collection: str, filt: dict, db: str = GEO_DB):
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
