"""
This is the file containing all of the endpoints for our flask app.
The endpoint called `endpoints` will return all available endpoints.
"""
# from http import HTTPStatus

from flask import Flask  # , request
from flask_restx import Resource, Api  # , fields  # Namespace
from flask_cors import CORS

# import werkzeug.exceptions as wz

import cities.queries as cqry

app = Flask(__name__)
CORS(app)
api = Api(app)

ERROR = 'Error'
MESSAGE = 'Message'
NUM_RECS = 'Number of Records'
READ = 'read'

ENDPOINT_EP = '/endpoints'
ENDPOINT_RESP = 'Available endpoints'

HELLO_EP = '/hello'
HELLO_RESP = 'hello'

CITIES_EPS = '/cities'
CITY_RESP = 'Cities'


sort_parser = api.parser()
sort_parser.add_argument(
    "sort",
    type=str,
    required=False,
    help="Sort by name or state_code; prefix with '-' for descending (e.g., -name)",
)


@api.route(f'{CITIES_EPS}/{READ}')
class Cities(Resource):
    """
    The purpose of the HelloWorld class is to have a simple test to see if the
    app is working at all.
    """
    @api.expect(sort_parser)
    def get(self):
        """
        A trivial endpoint to see if the server is running.
        """
        try:
            args = sort_parser.parse_args()
            sort = args.get("sort")
            cities = cqry.read_sorted(sort)
            num_recs = len(cities)
        except ConnectionError as e:
            return {ERROR: str(e)}
        return {
            CITY_RESP: cities,
            NUM_RECS: num_recs,
        }


@api.route(HELLO_EP)
class HelloWorld(Resource):
    """
    The purpose of the HelloWorld class is to have a simple test to see if the
    app is working at all.
    """
    def get(self):
        """
        A trivial endpoint to see if the server is running.
        """
        return {HELLO_RESP: 'world'}


@api.route(ENDPOINT_EP)
class Endpoints(Resource):
    """
    This class will serve as live, fetchable documentation of what endpoints
    are available in the system.
    """
    def get(self):
        """
        The `get()` method will return a sorted list of available endpoints.
        """
        endpoints = sorted(rule.rule for rule in api.app.url_map.iter_rules())
        return {"Available endpoints": endpoints}
