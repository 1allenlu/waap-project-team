import pytest
import country.country as country

def test_get_invalid_country_raises():
    """Check that invalid country ID raises a ValueError."""
    with pytest.raises(ValueError):
        # This assumes you'll add a function like get_country_by_id in country.py
        country.get_country_by_id("9999")
