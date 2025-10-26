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
