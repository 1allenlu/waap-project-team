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

country_cache = {}

def read() -> dict:
    """Return all countries (in-memory)."""
    return country_cache

def get_country_by_id(country_id: str)->dict:
    if country_id not in country_cache:
        raise ValueError(f"No such country")
    return country_cahce[country_id]
