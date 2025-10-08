import pytest

import cities.cities as ct


def test_create():
    with pytest.raises(ValueError):
        ct.create(17)