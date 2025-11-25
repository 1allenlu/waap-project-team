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
import country.country as cntry
import states.queries as sqry


app = Flask(__name__)
CORS(app)
api = Api(app)

# Reusable RESTX models (used by @api.expect for Swagger docs)
city_create_model = api.model('CityCreate', {
    'name': {'type': 'string', 'required': True, 'description': 'City name'},
    'state_code': {
        'type': 'string', 'required': False, 'description': 'State code'
    },
})

country_create_model = api.model('CountryCreate', {
    'id': {'type': 'string', 'required': True, 'description': 'Country ID'},
    'name': {
        'type': 'string', 'required': True, 'description': 'Country name'},
    'capital': {
        'type': 'string', 'required': True, 'description': 'Capital city'
    },
})

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

STATES_EPS = '/state'
STATE_RESP = 'States'

COUNTRIES_EP = '/countries'
COUNTRY_RESP = 'Countries'

sort_parser = api.parser()
sort_parser.add_argument(
    "sort",
    type=str,
    required=False,
    help="Sort by name/state_code; use '-name' for descending",
)


@api.route(f'{CITIES_EPS}/{READ}')
class Cities(Resource):
    """
    The purpose of the HelloWorld class is to have a simple test to see if the
    app is working at all.
    """
    @api.expect(sort_parser)
    @api.doc(
        description=(
            "Return a list of cities from the database. "
            "Optionally sort by name or state_code using the 'sort' query"
        )
    )
    @api.response(200, "Cities returned successfully")
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

    @api.expect(city_create_model)
    @api.doc(
        description=(
            "Create a new city record in the database. "
            "The request body must include at least 'name'; "
            "'state_code' is optional."
        )
    )
    @api.response(201, "City created successfully")
    def post(self):
        """Create a new city record"""
        payload = api.payload
        try:
            new_id = cqry.create(payload)
        except ValueError as e:
            return {ERROR: str(e)}, 400
        return {'id': str(new_id)}, 201


# reusable model for city create/update
city_model = api.model('CityModel', {
    'name': {'type': 'string', 'required': True, 'description': 'City name'},
    'state_code': {
        'type': 'string', 'required': False, 'description': 'State code'},
})


@api.route(f'{STATES_EPS}/{READ}')
class States(Resource):
    """
    The purpose of the HelloWorld class is to have a simple test to see if the
    app is working at all.
    """
    @api.doc(
        description="Return a list of all states from the backing store."
    )
    @api.response(200, "States returned successfully")
    @api.response(500, "Backend error while reading states")
    def get(self):
        """
        A trivial endpoint to see if the server is running.
        """
        try:
            states = sqry.read()
            num_recs = len(states)
        except ConnectionError as e:
            return {ERROR: str(e)}
        return {
            STATE_RESP: states,
            NUM_RECS: num_recs,
        }


@api.route(CITIES_EPS)
class CitiesRoot(Resource):
    """POST-only endpoint for creating cities at /cities
    Kept separate so clients can POST to /cities while the
    listing endpoint remains at /cities/read.
    """
    @api.expect(city_model)
    def post(self):
        """Create a new city record"""
        payload = api.payload
        try:
            new_id = cqry.create(payload)
        except ValueError as e:
            return {ERROR: str(e)}, 400
        return {'id': str(new_id)}, 201


@api.route(f'{CITIES_EPS}/<string:city_id>')
class CityItem(Resource):
    """GET/PUT/DELETE operations for a single city by id."""
    @api.doc(params={'city_id': 'City database id'})
    def get(self, city_id):
        try:
            city = cqry.get_by_id(city_id)
        except ValueError as e:
            return {ERROR: str(e)}, 404
        return city

    @api.expect(city_model)
    def put(self, city_id):
        payload = api.payload
        try:
            ok = cqry.update_by_id(city_id, payload)
        except ValueError as e:
            return {ERROR: str(e)}, 400
        if not ok:
            return {ERROR: 'No changes made or city not found'}, 404
        return {MESSAGE: 'Updated'}, 200

    def delete(self, city_id):
        try:
            ok = cqry.delete_by_id(city_id)
        except ValueError as e:
            return {ERROR: str(e)}, 400
        if not ok:
            return {ERROR: 'City not found'}, 404
        return {MESSAGE: 'Deleted'}, 200


@api.route('/health')
class Health(Resource):
    def get(self):
        try:
            # lightweight DB ping
            import data.db_connect as dbc
            dbc.connect_db()
        except Exception as e:
            return {ERROR: str(e)}, 500
        return {'status': 'ok'}


@api.route(f'{COUNTRIES_EP}/read')
class Countries(Resource):
    @api.doc(
        description="Return all countries from the in-memory country cache."
    )
    @api.response(200, "Countries returned successfully")
    @api.response(500, "Backend error while reading countries")
    def get(self):
        """
        Return all countries
        """
        try:
            countries = cntry.read()
            num_recs = len(countries)
        except Exception as e:
            return {ERROR: str(e)}, 500
        return {
            COUNTRY_RESP: countries,
            NUM_RECS: num_recs,
        }

    @api.expect(country_create_model)
    def post(self):
        """Add a new country to the in-memory cache."""
        payload = api.payload
        try:
            country_id = payload.get('id')
            if not country_id:
                raise ValueError("id is required")
            # add to the in-memory country cache
            cntry.country_cache[country_id] = {
                cntry.NAME: payload.get('name'),
                cntry.CAPITAL: payload.get('capital'),
            }
        except Exception as e:
            return {ERROR: str(e)}, 400
        return {'Message': f'Country {country_id} added successfully'}, 201


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
