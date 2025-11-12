"""
This file deals with our country-level data.
"""

ID = "id"
NAME = "name"
CAPITAL = "capital"

# Example seed data
country_cache = {
    "1": {NAME: "United States", CAPITAL: "Washington, D.C."},
    "2": {NAME: "Canada",        CAPITAL: "Ottawa"},
    "3": {NAME: "Mexico",        CAPITAL: "Mexico City"},
}


def read() -> dict:
    """Return all countries (in-memory)."""
    return country_cache


def get_country_by_id(country_id: str) -> dict:
    if country_id not in country_cache:
        raise ValueError("No such country")
    return country_cache[country_id]


def create(country_data: dict) -> str:
    """Add a new country record and return its ID."""
    if not isinstance(country_data, dict):
        raise ValueError("Invalid country data type; must be dict.")
    if NAME not in country_data or CAPITAL not in country_data:
        raise ValueError("Country data must include 'name' and 'capital'.")

    # Auto-generate a new numeric ID (as string)
    new_id = str(len(country_cache) + 1)
    country_cache[new_id] = {
        NAME: country_data[NAME],
        CAPITAL: country_data[CAPITAL],
    }
    return new_id
