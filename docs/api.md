# API specification Project - Geographic API

This document lists the planned endpoints, request/response JSON shapes, and brief notes for Swagger documentation.

Base URL: / (server root)

Health & metadata
- GET /health
  - Description: service health and DB connectivity
  - Response: 200 { "status": "ok", "db": "connected" }

- GET /endpoints
  - Description: returns a list of available endpoints and brief descriptions
  - Response: 200 { "endpoints": ["/cities", "/states", "/countries", "/health"] }

Countries
- GET /countries
  - Query parameters: ?q=<search>&?limit=50&?offset=0
  - Description: list countries
  - Response: 200 { "countries": [{"id":"US","name":"United States","iso2":"US"}], "count": 1 }

- POST /countries
  - Body: { "name": "United States", "iso2": "US", "iso3": "USA", "population": 331002651 }
  - Description: create a country
  - Response: 201 { "id": "<id>", "name": "United States" }

- GET /countries/{country_id}
  - Description: get a single country
  - Response: 200 { "id":"US","name":"United States","iso2":"US" }

- PUT /countries/{country_id}
  - Body: partial or full update fields
  - Response: 200 { "id": "US", "updated": true }

- DELETE /countries/{country_id}
  - Response: 200 { "id":"US","deleted": true }

States
- GET /states
  - Query params: ?country=<country_id>&?q=<search>
  - Response: 200 { "states": [{"id":"CA-ON","country":"CA","name":"Ontario"}], "count": 1 }

- POST /states
  - Body: { "country": "CA", "name": "Ontario", "code": "ON" }
  - Response: 201 { "id": "<id>", "name": "Ontario" }

- GET /states/{state_id}
- PUT /states/{state_id}
- DELETE /states/{state_id}

Cities
- GET /cities
  - Query params: ?state=<state_id>&?country=<country_id>&?q=<search>&?limit=50&?offset=0
  - Response: 200 { "cities": [{"id":"toronto","name":"Toronto","state":"ON","country":"CA"}], "count": 1 }

- POST /cities
  - Body: { "name": "Toronto", "state": "ON", "country": "CA", "population": 2731571 }
  - Response: 201 { "id": "<id>", "name": "Toronto" }

- GET /cities/{city_id}
- PUT /cities/{city_id}
- DELETE /cities/{city_id}

Search & metadata
- GET /counts
  - Response: 200 { "countries": 195, "states": 5000, "cities": 100000 }

Notes for implementation
- Use Flask-RESTX for endpoints and models to auto-generate Swagger UI at /swagger or /doc.
- Data validation: each POST/PUT should validate required fields and types (use Marshmallow or simple checks).
- Tests: unit tests for each query helper and endpoint (happy path + error cases). Use fixtures and mock DB calls with patch.
- CI: run lint, unit tests, then integration tests; use `mongod` in CI or use `mongomock` for unit tests.


