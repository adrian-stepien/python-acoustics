"""Tests for :mod:`acoustics.quantity`."""

import pytest

from acoustics.quantity import Quantity, Unit, get_quantity
from acoustics.standards.iso_tr_25417_2007 import REFERENCE_PRESSURE


class TestUnit:
    def test_attributes(self):
        u = Unit("pascal", "Pa", "$Pa$")
        assert u.name == "pascal"
        assert u.symbol == "Pa"
        assert u.symbol_latex == "$Pa$"

    def test_str_is_name(self):
        assert str(Unit("pascal", "Pa", "$Pa$")) == "pascal"

    def test_repr(self):
        assert repr(Unit("pascal", "Pa", "$Pa$")) == "Unit(pascal)"


class TestQuantity:
    def test_dynamic_and_energetic_are_complementary(self):
        q = Quantity("pressure", Unit("pascal", "Pa", "$Pa$"), dynamic=True)
        assert q.dynamic is True
        assert q.energetic is False

    def test_default_reference_is_one(self):
        q = Quantity("x", Unit("m", "m", "$m$"), dynamic=True)
        assert q.reference == 1.0

    def test_str_is_name(self):
        q = Quantity("pressure", Unit("pascal", "Pa", "$Pa$"), dynamic=True)
        assert str(q) == "pressure"

    def test_repr(self):
        q = Quantity("pressure", Unit("pascal", "Pa", "$Pa$"), dynamic=True)
        assert repr(q) == "Quantity(pressure)"


class TestGetQuantity:
    def test_returns_pressure_with_pascal_unit(self):
        q = get_quantity("pressure")
        assert q.name == "Pressure"
        assert q.dynamic is True
        assert q.reference == REFERENCE_PRESSURE
        assert isinstance(q.unit, Unit)
        assert q.unit.name == "pascal"
        assert q.unit.symbol == "Pa"

    def test_unknown_quantity_raises_value_error(self):
        with pytest.raises(ValueError, match="Unknown quantity"):
            get_quantity("bogus")
