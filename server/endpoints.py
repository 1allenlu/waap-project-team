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


@api.route(f'{CITIES_EPS}/{READ}')
class Cities(Resource):
    """
    The purpose of the HelloWorld class is to have a simple test to see if the
    app is working at all.
    """
    def get(self):
        """
        A trivial endpoint to see if the server is running.
        """
        try:
            cities = cqry.read()
            num_recs = len(cities)
        except ConnectionError as e:
            return {ERROR: str(e)}
        print(f'{cities=}')
        return {
            CITY_RESP: cities,
            NUM_RECS: num_recs,
        }


@api.route(HELLO_EP)
class Hello(Resource):
    def get(self):
        return {HELLO_RESP: 'world'}
