# test_country.py
import pytest
import country.country as country


def test_get_country_by_id_valid():
    """Test retrieving a valid country by ID."""
    us = country.get_country_by_id("1")
    assert us[country.NAME] == "United States"
    assert us[country.CAPITAL] == "Washington, D.C."


def test_get_invalid_country_raises():
    """Test that invalid country ID raises ValueError."""
    with pytest.raises(ValueError, match="No such country"):
        country.get_country_by_id("9999")


def test_read_returns_all_countries():
    """Test that read() returns all countries in cache."""
    countries = country.read()
    assert isinstance(countries, dict)
    assert len(countries) >= 3
    assert "1" in countries
    assert "2" in countries
    assert "3" in countries


def test_create_country_success():
    """Test creating a new country successfully."""
    initial_count = len(country.country_cache)
    new_country = {
        country.NAME: "France",
        country.CAPITAL: "Paris"
    }
    new_id = country.create(new_country)
    
    assert new_id is not None
    assert new_id in country.country_cache
    assert country.country_cache[new_id][country.NAME] == "France"
    assert country.country_cache[new_id][country.CAPITAL] == "Paris"
    assert len(country.country_cache) == initial_count + 1


def test_create_country_missing_name():
    """Test that creating a country without 'name' raises ValueError."""
    with pytest.raises(ValueError, match="must include 'name' and 'capital'"):
        country.create({country.CAPITAL: "Berlin"})


def test_create_country_missing_capital():
    """Test that creating a country without 'capital' raises ValueError."""
    with pytest.raises(ValueError, match="must include 'name' and 'capital'"):
        country.create({country.NAME: "Germany"})


def test_create_country_invalid_type():
    """Test that passing non-dict to create() raises ValueError."""
    with pytest.raises(ValueError, match="Invalid country data type"):
        country.create("not a dict")


def test_create_country_empty_dict():
    """Test that creating a country with empty dict raises ValueError."""
    with pytest.raises(ValueError, match="must include 'name' and 'capital'"):
        country.create({})


def test_create_then_retrieve():
    """Test creating a country and then retrieving it by ID."""
    new_country = {
        country.NAME: "Japan",
        country.CAPITAL: "Tokyo"
    }
    new_id = country.create(new_country)
    
    retrieved = country.get_country_by_id(new_id)
    assert retrieved[country.NAME] == "Japan"
    assert retrieved[country.CAPITAL] == "Tokyo"


def test_create_multiple_countries():
    """Test creating multiple countries generates unique IDs."""
    initial_count = len(country.country_cache)
    
    id1 = country.create({country.NAME: "Germany", country.CAPITAL: "Berlin"})
    id2 = country.create({country.NAME: "Spain", country.CAPITAL: "Madrid"})
    
    assert id1 != id2
    assert len(country.country_cache) == initial_count + 2
    assert country.country_cache[id1][country.NAME] == "Germany"
    assert country.country_cache[id2][country.NAME] == "Spain"